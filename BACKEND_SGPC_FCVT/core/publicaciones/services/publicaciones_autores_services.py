"""
Servicio para registrar autores asociados a una publicación.

Reglas:

- debe existir al menos un autor;
- todos los participantes se consideran autores;
- no existe autor principal ni coautor;
- no puede repetirse un autor;
- no puede repetirse un orden;
- los órdenes deben ser consecutivos: 1, 2, 3...;
- el orden representa únicamente la posición bibliográfica
  de los autores;
- se conserva exactamente ese orden en detalles, listados,
  perfiles, reportes y exportaciones.
"""

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import (
    Autor,
    Publicacion,
    PublicacionAutor,
)


def _resolve_autor_id(
    item,
):
    """
    Obtiene el identificador del Autor.

    Acepta cualquiera de estas representaciones:

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

    if autor_id in (
        None,
        "",
    ):
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
    """
    Obtiene y valida el orden bibliográfico del autor.

    El orden comienza en 1 y no representa ninguna jerarquía
    ni nivel de contribución.
    """

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
    """
    Normaliza y valida el conjunto completo de autores.

    Resultado:

        [
            {
                "autor_id": 10,
                "orden": 1,
            },
            {
                "autor_id": 15,
                "orden": 2,
            },
        ]

    Nunca genera ni interpreta roles de autoría.
    """

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

    # =========================================================
    # AUTORES DUPLICADOS
    # =========================================================

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

    # =========================================================
    # ÓRDENES DUPLICADOS
    # =========================================================

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

    # =========================================================
    # ÓRDENES CONSECUTIVOS
    # =========================================================

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
                    "Los órdenes de los autores "
                    "deben ser consecutivos: "
                    f"{expected_orders}."
                ]
            }
        )

    # El orden únicamente representa posición bibliográfica.
    normalized.sort(
        key=lambda item: item["orden"]
    )

    return normalized


@transaction.atomic
def registrar_autores_publicacion(
    *,
    publicacion,
    autores_data,
):
    """
    Registra las relaciones entre Publicacion y Autor.

    Todos los registros creados poseen únicamente:

        publicacion
        autor
        orden

    No se asignan roles de autoría.
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

    normalized = _normalizar_autores(
        autores_data
    )

    # =========================================================
    # COMPROBAR EXISTENCIA DE LOS AUTORES
    # =========================================================

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

    # =========================================================
    # EVITAR REGISTRO DUPLICADO
    # =========================================================
    #
    # Este servicio se utiliza durante la creación de una
    # publicación. Si ya existen autores asociados, algo en
    # el flujo de creación está intentando registrar dos veces
    # las relaciones.
    # =========================================================

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

    # =========================================================
    # CREACIÓN
    # =========================================================
    #
    # Se utiliza .create() en lugar de bulk_create() para
    # conservar las validaciones definidas por el modelo
    # PublicacionAutor.
    # =========================================================

    for item in normalized:
        relacion = (
            PublicacionAutor.objects
            .create(
                publicacion=publicacion,
                autor=autores_map[
                    item["autor_id"]
                ],
                orden=item["orden"],
            )
        )

        created.append(
            relacion
        )

    return created