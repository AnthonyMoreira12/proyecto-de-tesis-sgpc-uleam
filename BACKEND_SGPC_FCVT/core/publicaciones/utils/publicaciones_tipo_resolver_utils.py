"""
Utilidad para resolver y etiquetar el tipo final de una publicación.
"""

from django.db.models import Case, CharField, Value, When

TIPOS_PUBLICACION_FINALES = {
    "articulo_alto_impacto": "Artículo de alto impacto",
    "articulo_regional": "Artículo regional",
    "ponencia": "Ponencia",
    "libro": "Libro",
    "capitulo_libro": "Capítulo del libro",
}


def annotate_tipo_publicacion_final(qs):
    return qs.annotate(
        tipo_publicacion_final=Case(
            When(
                tipo__categoria="articulo",
                articulo__tipo_articulo="alto_impacto",
                then=Value("articulo_alto_impacto"),
            ),
            When(
                tipo__categoria="articulo",
                articulo__tipo_articulo="regional",
                then=Value("articulo_regional"),
            ),
            When(tipo__categoria="ponencia", then=Value("ponencia")),
            When(tipo__categoria="libro", then=Value("libro")),
            When(tipo__categoria="capitulo", then=Value("capitulo_libro")),
            default=Value("sin_clasificar"),
            output_field=CharField(),
        )
    )


def tipo_publicacion_label(tipo_id: str) -> str:
    return TIPOS_PUBLICACION_FINALES.get(tipo_id, "Sin clasificar")