"""
Servicio para registrar autores asociados a una publicación.

Reglas:
- Debe existir al menos un autor.
- No puede repetirse un autor.
- No puede repetirse un orden.
- Los órdenes deben ser consecutivos: 1, 2, 3...
- Debe existir exactamente un autor principal.
- El autor principal debe ocupar el orden 1.
- Todo autor con orden superior a 1 es coautor.
"""

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import (
    Autor,
    Publicacion,
    PublicacionAutor,
)


def _resolve_autor_id(item):
    """
    Acepta payload normalizado de cualquiera de estas formas:

    {
        "autor": <Autor instance>
    }

    {
        "autor": 12
    }

    {
        "autor_id": 12
    }
    """

    autor_value = item.get(
        "autor",
        None,
    )

    autor_id = item.get(
        "autor_id",
        None,
    )

    if (
        autor_id is None
        and autor_value is not None
    ):
        autor_id = getattr(
            autor_value,
            "id",
            autor_value,
        )

    if autor_id is None:
        raise ValidationError(
            {
                "autores": [
                    "Cada autor debe incluir "
                    "'autor_id' o 'autor'."
                ]
            }
        )

    try:
        autor_id = int(
            autor_id
        )
    except (
        TypeError,
        ValueError,
    ):
        raise ValidationError(
            {
                "autores": [
                    "El identificador del autor "
                    "debe ser numérico."
                ]
            }
        )

    if autor_id < 1:
        raise ValidationError(
            {
                "autores": [
                    "El identificador del autor "
                    "no es válido."
                ]
            }
        )

    return autor_id


def _resolve_orden(
    item,
    *,
    index,
):
    orden = item.get(
        "orden",
        None,
    )

    if orden in (
        None,
        "",
    ):
        raise ValidationError(
            {
                "autores": [
                    f"El autor #{index} debe "
                    "tener un orden."
                ]
            }
        )

    try:
        orden = int(
            orden
        )
    except (
        TypeError,
        ValueError,
    ):
        raise ValidationError(
            {
                "autores": [
                    f"El orden del autor "
                    f"#{index} debe ser numérico."
                ]
            }
        )

    if orden < 1:
        raise ValidationError(
            {
                "autores": [
                    "El orden debe ser mayor "
                    "o igual a 1."
                ]
            }
        )

    return orden


def _normalizar_autores(
    autores_data,
):
    if not isinstance(
        autores_data,
        (list, tuple),
    ):
        raise ValidationError(
            {
                "autores": [
                    "Los autores deben enviarse "
                    "como una lista."
                ]
            }
        )

    if not autores_data:
        raise ValidationError(
            {
                "autores": [
                    "Debe registrar al menos "
                    "un autor."
                ]
            }
        )

    normalized = []

    for index, item in enumerate(
        autores_data,
        start=1,
    ):
        if not isinstance(
            item,
            dict,
        ):
            raise ValidationError(
                {
                    "autores": [
                        f"El autor #{index} "
                        "debe ser un objeto."
                    ]
                }
            )

        autor_id = _resolve_autor_id(
            item
        )

        orden = _resolve_orden(
            item,
            index=index,
        )

        normalized.append(
            {
                "autor_id": autor_id,
                "orden": orden,
            }
        )

    autor_ids = [
        item["autor_id"]
        for item in normalized
    ]

    ordenes = [
        item["orden"]
        for item in normalized
    ]

    # ---------------------------------------------------------
    # Duplicados
    # ---------------------------------------------------------

    if (
        len(autor_ids)
        != len(set(autor_ids))
    ):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir "
                    "el mismo autor."
                ]
            }
        )

    if (
        len(ordenes)
        != len(set(ordenes))
    ):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir "
                    "el orden de los autores."
                ]
            }
        )

    # ---------------------------------------------------------
    # Órdenes consecutivos
    # ---------------------------------------------------------

    expected_orders = list(
        range(
            1,
            len(normalized) + 1,
        )
    )

    if (
        sorted(ordenes)
        != expected_orders
    ):
        raise ValidationError(
            {
                "autores": [
                    "Los órdenes deben ser "
                    "consecutivos: "
                    f"{expected_orders}."
                ]
            }
        )

    normalized.sort(
        key=lambda item: item["orden"]
    )

    # ---------------------------------------------------------
    # Rol derivado del orden
    # ---------------------------------------------------------

    for item in normalized:
        item["rol_autoria"] = (
            "principal"
            if item["orden"] == 1
            else "coautor"
        )

    return normalized


@transaction.atomic
def registrar_autores_publicacion(
    *,
    publicacion,
    autores_data,
):
    """
    Registra las relaciones PublicacionAutor.

    Está pensado para utilizarse durante la creación
    de una publicación.
    """

    if not isinstance(
        publicacion,
        Publicacion,
    ):
        raise ValidationError(
            {
                "publicacion": [
                    "La publicación indicada "
                    "no es válida."
                ]
            }
        )

    if not publicacion.pk:
        raise ValidationError(
            {
                "publicacion": [
                    "La publicación debe existir "
                    "antes de registrar sus autores."
                ]
            }
        )

    normalized = (
        _normalizar_autores(
            autores_data
        )
    )

    # ---------------------------------------------------------
    # Comprobar existencia de autores
    # ---------------------------------------------------------

    autor_ids = [
        item["autor_id"]
        for item in normalized
    ]

    autores_map = Autor.objects.in_bulk(
        autor_ids
    )

    missing_ids = sorted(
        set(autor_ids)
        - set(autores_map.keys())
    )

    if missing_ids:
        raise ValidationError(
            {
                "autores": [
                    "Uno o más autores "
                    "seleccionados no existen: "
                    f"{missing_ids}."
                ]
            }
        )

    # ---------------------------------------------------------
    # Este servicio corresponde a creación.
    # Evitamos registrar dos veces la misma autoría.
    # ---------------------------------------------------------

    if (
        PublicacionAutor.objects
        .filter(
            publicacion=publicacion
        )
        .exists()
    ):
        raise ValidationError(
            {
                "autores": [
                    "La publicación ya tiene "
                    "autores registrados."
                ]
            }
        )

    created = []

    # ---------------------------------------------------------
    # Usamos .create() en lugar de bulk_create().
    #
    # PublicacionAutor.save() ejecuta full_clean(), por lo
    # que mantenemos activas las reglas del modelo.
    # ---------------------------------------------------------

    for item in normalized:
        relacion = (
            PublicacionAutor.objects
            .create(
                publicacion=publicacion,
                autor=autores_map[
                    item["autor_id"]
                ],
                rol_autoria=(
                    item[
                        "rol_autoria"
                    ]
                ),
                orden=item["orden"],
            )
        )

        created.append(
            relacion
        )

    return created