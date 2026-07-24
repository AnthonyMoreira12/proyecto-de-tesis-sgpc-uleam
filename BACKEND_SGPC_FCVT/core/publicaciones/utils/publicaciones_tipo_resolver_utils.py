"""
Utilidades para normalizar, resolver y etiquetar
el tipo final de una publicación.

Tipos públicos utilizados por el sistema:

- articulo_alto_impacto
- articulo_regional
- ponencia
- libro
- capitulo_libro
"""

from django.db.models import (
    Case,
    CharField,
    Q,
    Value,
    When,
)


TIPOS_PUBLICACION_FINALES = {
    "articulo_alto_impacto": (
        "Artículo de alto impacto"
    ),
    "articulo_regional": (
        "Artículo regional"
    ),
    "ponencia": "Ponencia",
    "libro": "Libro",
    "capitulo_libro": (
        "Capítulo de libro"
    ),
}


TIPOS_PUBLICACION_ALIASES = {
    # Artículo alto impacto
    "articulo_alto_impacto": (
        "articulo_alto_impacto"
    ),
    "alto_impacto": (
        "articulo_alto_impacto"
    ),
    "aai": (
        "articulo_alto_impacto"
    ),

    # Artículo regional
    "articulo_regional": (
        "articulo_regional"
    ),
    "regional": (
        "articulo_regional"
    ),
    "ar": (
        "articulo_regional"
    ),

    # Ponencia
    "ponencia": "ponencia",
    "ponencias": "ponencia",
    "pon": "ponencia",

    # Libro
    "libro": "libro",
    "libros": "libro",
    "lib": "libro",

    # Capítulo
    "capitulo": (
        "capitulo_libro"
    ),
    "capítulo": (
        "capitulo_libro"
    ),
    "capitulo_libro": (
        "capitulo_libro"
    ),
    "capítulo_libro": (
        "capitulo_libro"
    ),
    "cap": (
        "capitulo_libro"
    ),
}


def normalize_tipo_publicacion_final(
    value,
):
    """
    Convierte aliases del frontend/backend a uno de los
    cinco códigos oficiales.

    Devuelve None cuando no reconoce el valor.
    """

    normalized = str(
        value or ""
    ).strip().lower()

    if not normalized:
        return None

    return (
        TIPOS_PUBLICACION_ALIASES
        .get(normalized)
    )


def annotate_tipo_publicacion_final(
    queryset,
):
    """
    Añade al queryset:

        tipo_publicacion_final

    La resolución prioriza el subtipo real de Articulo
    y luego la categoría/código de TipoPublicacion.

    Se conservan comprobaciones por código para mantener
    compatibilidad con registros históricos.
    """

    return queryset.annotate(
        tipo_publicacion_final=Case(
            # -------------------------------------------------
            # Artículos
            # -------------------------------------------------

            When(
                Q(
                    articulo__tipo_articulo=(
                        "alto_impacto"
                    )
                )
                & (
                    Q(
                        tipo__categoria=(
                            "articulo"
                        )
                    )
                    | Q(
                        tipo__codigo=(
                            "articulo"
                        )
                    )
                    | Q(
                        tipo__codigo=(
                            "articulo_alto_impacto"
                        )
                    )
                ),
                then=Value(
                    "articulo_alto_impacto"
                ),
            ),

            When(
                Q(
                    articulo__tipo_articulo=(
                        "regional"
                    )
                )
                & (
                    Q(
                        tipo__categoria=(
                            "articulo"
                        )
                    )
                    | Q(
                        tipo__codigo=(
                            "articulo"
                        )
                    )
                    | Q(
                        tipo__codigo=(
                            "articulo_regional"
                        )
                    )
                ),
                then=Value(
                    "articulo_regional"
                ),
            ),

            # -------------------------------------------------
            # Ponencia
            # -------------------------------------------------

            When(
                Q(
                    tipo__categoria="ponencia"
                )
                | Q(
                    tipo__codigo="ponencia"
                ),
                then=Value(
                    "ponencia"
                ),
            ),

            # -------------------------------------------------
            # Libro
            # -------------------------------------------------

            When(
                Q(
                    tipo__categoria="libro"
                )
                | Q(
                    tipo__codigo="libro"
                ),
                then=Value(
                    "libro"
                ),
            ),

            # -------------------------------------------------
            # Capítulo
            # -------------------------------------------------

            When(
                Q(
                    tipo__categoria="capitulo"
                )
                | Q(
                    tipo__codigo="capitulo"
                )
                | Q(
                    tipo__codigo=(
                        "capitulo_libro"
                    )
                ),
                then=Value(
                    "capitulo_libro"
                ),
            ),

            default=Value(
                "sin_clasificar"
            ),

            output_field=CharField(),
        )
    )


def tipo_publicacion_label(
    tipo_id,
) -> str:
    """
    Devuelve la etiqueta visible de un tipo.

    Acepta tanto el código oficial como los aliases
    reconocidos.
    """

    tipo_normalizado = (
        normalize_tipo_publicacion_final(
            tipo_id
        )
    )

    if not tipo_normalizado:
        return "Sin clasificar"

    return (
        TIPOS_PUBLICACION_FINALES.get(
            tipo_normalizado,
            "Sin clasificar",
        )
    )


def tipo_publicacion_es_valido(
    value,
) -> bool:
    return (
        normalize_tipo_publicacion_final(
            value
        )
        is not None
    )