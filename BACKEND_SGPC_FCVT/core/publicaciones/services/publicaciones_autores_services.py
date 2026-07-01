"""
Servicio para registrar y validar los autores asociados a una publicación.
Estructura esperada:
- 1 autor principal con orden = 1
- coautores con orden = 2, 3, 4...
"""

from rest_framework.exceptions import ValidationError

from core.models import Autor, PublicacionAutor


def registrar_autores_publicacion(*, publicacion, autores_data):
    if not autores_data:
        return

    rels = []
    autor_ids = []
    ordenes = []
    principal_count = 0

    for item in autores_data:
        autor_value = item.get("autor", None)
        autor_id = item.get("autor_id", None)

        if autor_id is None and autor_value is not None:
            autor_id = getattr(autor_value, "id", autor_value)

        if autor_id is None:
            raise ValidationError(
                {"autores": ["Cada autor debe incluir 'autor_id' o 'autor'."]}
            )

        try:
            autor_id = int(autor_id)
        except Exception:
            raise ValidationError({"autores": ["'autor_id' debe ser numérico."]})

        orden = item.get("orden", None)
        if orden is None:
            raise ValidationError({"autores": ["Cada autor debe tener un 'orden'."]})

        try:
            orden = int(orden)
        except Exception:
            raise ValidationError({"autores": ["El 'orden' debe ser un número entero."]})

        if orden < 1:
            raise ValidationError({"autores": ["El 'orden' debe ser mayor o igual a 1."]})

        rol = item.get("rol_autoria", None)
        if rol not in dict(PublicacionAutor.ROL_AUTORIA):
            raise ValidationError(
                {"autores": ["Cada autor debe incluir un 'rol_autoria' válido."]}
            )

        if rol == "principal":
            principal_count += 1
            if orden != 1:
                raise ValidationError(
                    {"autores": ["El autor principal debe registrarse con orden = 1."]}
                )

        autor_ids.append(autor_id)
        ordenes.append(orden)

    if len(autor_ids) != len(set(autor_ids)):
        raise ValidationError({"autores": ["No se permite repetir el mismo autor."]})

    if len(ordenes) != len(set(ordenes)):
        raise ValidationError({"autores": ["No se permite repetir el campo 'orden'."]})

    if principal_count != 1:
        raise ValidationError({"autores": ["Debe existir exactamente un autor principal."]})

    if 1 not in set(ordenes):
        raise ValidationError({"autores": ["Debe existir un autor con orden = 1."]})

    expected_orders = list(range(1, len(ordenes) + 1))
    if sorted(ordenes) != expected_orders:
        raise ValidationError(
            {"autores": [f"Los órdenes deben ser consecutivos: {expected_orders}."]}
        )

    autores_map = {autor.id: autor for autor in Autor.objects.filter(id__in=set(autor_ids))}
    missing = [aid for aid in set(autor_ids) if aid not in autores_map]
    if missing:
        raise ValidationError({"autores": [f"Autor no existe: {missing}"]})

    for item in autores_data:
        autor_value = item.get("autor", None)
        autor_id = item.get("autor_id", None)

        if autor_id is None and autor_value is not None:
            autor_id = getattr(autor_value, "id", autor_value)

        autor_id = int(autor_id)
        orden = int(item["orden"])
        rol = item["rol_autoria"]
        autor_obj = autores_map[autor_id]

        rels.append(
            PublicacionAutor(
                publicacion=publicacion,
                autor=autor_obj,
                rol_autoria=rol,
                orden=orden,
            )
        )

    PublicacionAutor.objects.bulk_create(rels)