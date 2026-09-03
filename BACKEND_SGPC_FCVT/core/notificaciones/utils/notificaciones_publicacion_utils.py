"""
Resolución de información legible de publicaciones para notificaciones.

La entidad ``Publicacion`` no almacena el título de forma directa. El
texto visible vive en el detalle correspondiente a su categoría:

- Articulo.nombre_articulo
- Ponencia.nombre_ponencia
- Libro.nombre_libro
- CapituloLibro.nombre_capitulo

La resolución intenta primero utilizar la relación OneToOne ya cargada.
Si por cualquier motivo esa relación no está disponible en la instancia
recibida, realiza una consulta directa por ``publicacion_id``. De esta
forma las notificaciones nuevas y las históricas pueden mostrar el título
sin exponer identificadores internos.
"""

from django.core.exceptions import ObjectDoesNotExist

from core.models import (
    Articulo,
    CapituloLibro,
    Libro,
    Ponencia,
)


def _text(value):
    return str(value or "").strip()


def _safe_related(instance, attribute):
    if instance is None:
        return None

    try:
        return getattr(instance, attribute, None)
    except ObjectDoesNotExist:
        return None


def _tipo_categoria(publicacion):
    tipo = _safe_related(publicacion, "tipo")
    return _text(
        getattr(tipo, "categoria", None)
    ).lower()


def obtener_nombre_tipo_publicacion(publicacion):
    """Devuelve el nombre institucional del tipo de publicación."""

    tipo = _safe_related(publicacion, "tipo")

    return _text(
        getattr(tipo, "nombre", None)
    )


def _detalle_config_por_categoria(categoria):
    return {
        "articulo": (
            "articulo",
            Articulo,
            "nombre_articulo",
        ),
        "ponencia": (
            "ponencia",
            Ponencia,
            "nombre_ponencia",
        ),
        "libro": (
            "libro",
            Libro,
            "nombre_libro",
        ),
        "capitulo": (
            "capitulo_libro",
            CapituloLibro,
            "nombre_capitulo",
        ),
    }.get(categoria)


def _titulo_desde_relacion(
    publicacion,
    relation_name,
    field_name,
):
    detail = _safe_related(
        publicacion,
        relation_name,
    )

    return _text(
        getattr(detail, field_name, None)
    )


def _titulo_desde_bd(
    publicacion_id,
    model,
    field_name,
):
    if not publicacion_id:
        return ""

    value = (
        model.objects
        .filter(publicacion_id=publicacion_id)
        .values_list(field_name, flat=True)
        .first()
    )

    return _text(value)


def obtener_titulo_publicacion(publicacion):
    """
    Devuelve el título humano de una ``Publicacion``.

    La categoría del tipo determina qué modelo de detalle consultar. Si
    faltara la categoría por datos históricos, se prueban los cuatro
    detalles conocidos como último recurso.
    """

    if publicacion is None:
        return ""

    publicacion_id = getattr(
        publicacion,
        "pk",
        None,
    ) or getattr(
        publicacion,
        "id",
        None,
    )

    categoria = _tipo_categoria(publicacion)
    config = _detalle_config_por_categoria(
        categoria
    )

    if config:
        relation_name, model, field_name = config

        title = _titulo_desde_relacion(
            publicacion,
            relation_name,
            field_name,
        )

        if title:
            return title

        return _titulo_desde_bd(
            publicacion_id,
            model,
            field_name,
        )

    fallback_configs = [
        (
            "articulo",
            Articulo,
            "nombre_articulo",
        ),
        (
            "ponencia",
            Ponencia,
            "nombre_ponencia",
        ),
        (
            "libro",
            Libro,
            "nombre_libro",
        ),
        (
            "capitulo_libro",
            CapituloLibro,
            "nombre_capitulo",
        ),
    ]

    for relation_name, model, field_name in fallback_configs:
        title = _titulo_desde_relacion(
            publicacion,
            relation_name,
            field_name,
        )

        if title:
            return title

        title = _titulo_desde_bd(
            publicacion_id,
            model,
            field_name,
        )

        if title:
            return title

    return ""
