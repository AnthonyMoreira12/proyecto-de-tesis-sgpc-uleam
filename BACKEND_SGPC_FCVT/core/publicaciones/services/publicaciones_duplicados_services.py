"""Detección centralizada de publicaciones duplicadas.

FASE 7 — Integridad y calidad de datos.

Se distinguen dos niveles:

- Coincidencia fuerte: bloquea creación/actualización.
- Posible coincidencia: se informa como advertencia, pero no bloquea.

Criterios fuertes actuales:

- mismo SHA-256 del PDF principal;
- mismo DOI normalizado en artículos;
- mismo ISBN normalizado entre libros;
- mismo ISBN + mismo título de capítulo normalizado entre capítulos.

Los títulos semejantes nunca bloquean por sí solos. Se consideran una
advertencia para revisión humana.
"""

from difflib import SequenceMatcher
import re
import unicodedata

from rest_framework.exceptions import ValidationError

from core.models import (
    Articulo,
    CapituloLibro,
    Libro,
    Publicacion,
)
from core.utils.files import compute_file_sha256


TITLE_SIMILARITY_WARNING_THRESHOLD = 0.92

ARTICLE_CODES = {
    "articulo_regional",
    "articulo_alto_impacto",
}

TYPE_CATEGORY_MAP = {
    "ponencia": "ponencia",
    "libro": "libro",
    "capitulo_libro": "capitulo",
    "capitulo": "capitulo",
    "articulo": "articulo",
    "articulo_regional": "articulo",
    "articulo_alto_impacto": "articulo",
}

TITLE_FIELD_MAP = {
    "ponencia": "nombre_ponencia",
    "articulo": "nombre_articulo",
    "libro": "nombre_libro",
    "capitulo": "nombre_capitulo",
}


# ============================================================
# NORMALIZACIÓN
# ============================================================


def _text(value):
    return str(value or "").strip()


def normalize_title(value):
    """Normaliza un título sin convertir similitud en identidad."""

    text = _text(value).lower()

    if not text:
        return ""

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return " ".join(
        text.split()
    )


def normalize_doi(value):
    value = _text(value).lower()

    if not value:
        return ""

    value = re.sub(
        r"^doi\s*:\s*",
        "",
        value,
    )

    value = re.sub(
        r"^https?://(?:dx\.)?doi\.org/",
        "",
        value,
    )

    return value.strip().rstrip("/.")


def normalize_isbn(value):
    value = _text(value).upper()

    if not value:
        return ""

    return re.sub(
        r"[^0-9X]",
        "",
        value,
    )


def _positive_int(value):
    try:
        value = int(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return value if value > 0 else None


def _resolve_type_code(data):
    raw = _text(
        data.get("tipo_codigo")
        or data.get("tipo_publicacion")
        or data.get("tipo")
        or data.get("categoria")
    ).lower()

    if raw in TYPE_CATEGORY_MAP:
        return raw

    return ""


def _resolve_category(type_code):
    return TYPE_CATEGORY_MAP.get(
        _text(type_code).lower(),
        "",
    )


# ============================================================
# REPRESENTACIÓN DE COINCIDENCIAS
# ============================================================


def _related(publication, relation_name):
    try:
        return getattr(
            publication,
            relation_name,
            None,
        )
    except Exception:
        return None


def _publication_title(publication):
    category = _text(
        getattr(
            getattr(publication, "tipo", None),
            "categoria",
            "",
        )
    ).lower()

    if category == "articulo":
        related = _related(
            publication,
            "articulo",
        )
        return _text(
            getattr(
                related,
                "nombre_articulo",
                "",
            )
        )

    if category == "ponencia":
        related = _related(
            publication,
            "ponencia",
        )
        return _text(
            getattr(
                related,
                "nombre_ponencia",
                "",
            )
        )

    if category == "libro":
        related = _related(
            publication,
            "libro",
        )
        return _text(
            getattr(
                related,
                "nombre_libro",
                "",
            )
        )

    if category == "capitulo":
        related = _related(
            publication,
            "capitulo_libro",
        )
        return _text(
            getattr(
                related,
                "nombre_capitulo",
                "",
            )
        )

    return ""


def _base_queryset():
    return (
        Publicacion.objects
        .select_related(
            "tipo",
            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
    )


def _serialize_match(
    publication,
    *,
    level,
    reasons,
    criteria,
    similarity=None,
):
    publication_type = getattr(
        publication,
        "tipo",
        None,
    )

    data = {
        "publicacion_id": publication.pk,
        "numero": publication.numero,
        "tipo_codigo": _text(
            getattr(
                publication_type,
                "codigo",
                "",
            )
        ),
        "tipo_nombre": _text(
            getattr(
                publication_type,
                "nombre",
                "",
            )
        ),
        "categoria": _text(
            getattr(
                publication_type,
                "categoria",
                "",
            )
        ),
        "titulo": _publication_title(
            publication
        ),
        "anio_publicacion": (
            publication.anio_publicacion
        ),
        "estado": publication.estado,
        "estado_label": (
            publication.get_estado_display()
        ),
        "nivel": level,
        "motivos": list(
            dict.fromkeys(reasons)
        ),
        "criterios": list(
            dict.fromkeys(criteria)
        ),
    }

    if similarity is not None:
        data["similitud_titulo"] = round(
            float(similarity),
            4,
        )

    return data


def _add_match(
    store,
    publication,
    *,
    level,
    reason,
    criterion,
    similarity=None,
):
    publication_id = publication.pk

    item = store.get(
        publication_id
    )

    if item is None:
        store[publication_id] = {
            "publication": publication,
            "level": level,
            "reasons": [reason],
            "criteria": [criterion],
            "similarity": similarity,
        }
        return

    if reason not in item["reasons"]:
        item["reasons"].append(
            reason
        )

    if criterion not in item["criteria"]:
        item["criteria"].append(
            criterion
        )

    if similarity is not None:
        current = item.get(
            "similarity"
        )

        if (
            current is None
            or similarity > current
        ):
            item["similarity"] = (
                similarity
            )


def _render_store(store):
    items = []

    for publication_id in sorted(
        store
    ):
        item = store[
            publication_id
        ]

        items.append(
            _serialize_match(
                item["publication"],
                level=item["level"],
                reasons=item["reasons"],
                criteria=item["criteria"],
                similarity=item.get(
                    "similarity"
                ),
            )
        )

    return items


# ============================================================
# ANÁLISIS
# ============================================================


def _candidate_values_from_publication(
    publication,
):
    publication_type = getattr(
        publication,
        "tipo",
        None,
    )

    type_code = _text(
        getattr(
            publication_type,
            "codigo",
            "",
        )
    ).lower()

    category = _resolve_category(
        type_code
    ) or _text(
        getattr(
            publication_type,
            "categoria",
            "",
        )
    ).lower()

    values = {
        "type_code": type_code,
        "category": category,
        "year": publication.anio_publicacion,
        "sha256": _text(
            getattr(
                publication,
                "archivo_pdf_sha256",
                "",
            )
        ).lower(),
        "title": _publication_title(
            publication
        ),
        "doi": "",
        "isbn": "",
        "event_name": "",
    }

    if category == "articulo":
        related = _related(
            publication,
            "articulo",
        )
        values["doi"] = normalize_doi(
            getattr(
                related,
                "codigo_doi",
                "",
            )
        )

    elif category == "libro":
        related = _related(
            publication,
            "libro",
        )
        values["isbn"] = normalize_isbn(
            getattr(
                related,
                "codigo_isbn",
                "",
            )
        )

    elif category == "capitulo":
        related = _related(
            publication,
            "capitulo_libro",
        )
        values["isbn"] = normalize_isbn(
            getattr(
                related,
                "codigo_isbn",
                "",
            )
        )

    elif category == "ponencia":
        related = _related(
            publication,
            "ponencia",
        )
        values["event_name"] = _text(
            getattr(
                related,
                "nombre_evento",
                "",
            )
        )

    return values


def _candidate_values_from_payload(
    data,
    *,
    uploaded_file=None,
):
    type_code = _resolve_type_code(
        data
    )

    category = _resolve_category(
        type_code
    )

    if not type_code or not category:
        raise ValidationError(
            {
                "tipo_codigo": [
                    (
                        "Debe indicar un tipo de publicación válido "
                        "para comprobar duplicados."
                    )
                ]
            }
        )

    title_field = TITLE_FIELD_MAP[
        category
    ]

    sha256 = ""

    if uploaded_file not in (
        None,
        "",
    ):
        sha256 = _text(
            compute_file_sha256(
                uploaded_file
            )
        ).lower()

    values = {
        "type_code": type_code,
        "category": category,
        "year": _positive_int(
            data.get(
                "anio_publicacion"
            )
        ),
        "sha256": sha256,
        "title": _text(
            data.get(
                title_field
            )
        ),
        "doi": "",
        "isbn": "",
        "event_name": "",
    }

    if category == "articulo":
        values["doi"] = normalize_doi(
            data.get(
                "codigo_doi"
            )
        )

    elif category in {
        "libro",
        "capitulo",
    }:
        values["isbn"] = normalize_isbn(
            data.get(
                "codigo_isbn"
            )
        )

    elif category == "ponencia":
        values["event_name"] = _text(
            data.get(
                "nombre_evento"
            )
        )

    return values


def _analyse_values(
    values,
    *,
    exclude_publication_id=None,
):
    exclude_publication_id = (
        _positive_int(
            exclude_publication_id
        )
    )

    blocking = {}
    warnings = {}

    sha256 = _text(
        values.get("sha256")
    ).lower()

    category = _text(
        values.get("category")
    ).lower()

    title = _text(
        values.get("title")
    )

    normalized_title = normalize_title(
        title
    )

    year = _positive_int(
        values.get("year")
    )

    doi = normalize_doi(
        values.get("doi")
    )

    isbn = normalize_isbn(
        values.get("isbn")
    )

    # --------------------------------------------------------
    # 1. SHA-256: identidad binaria del PDF principal
    # --------------------------------------------------------

    if sha256:
        queryset = _base_queryset().filter(
            archivo_pdf_sha256=sha256
        )

        if exclude_publication_id:
            queryset = queryset.exclude(
                pk=exclude_publication_id
            )

        for publication in queryset:
            _add_match(
                blocking,
                publication,
                level="bloqueante",
                criterion="sha256",
                reason=(
                    "El PDF principal tiene exactamente la misma "
                    "huella SHA-256 que una publicación existente."
                ),
            )

    # --------------------------------------------------------
    # 2. DOI: identificador fuerte de artículo
    # --------------------------------------------------------

    if (
        category == "articulo"
        and doi
    ):
        queryset = (
            Articulo.objects
            .select_related(
                "publicacion",
                "publicacion__tipo",
            )
            .exclude(
                codigo_doi__isnull=True
            )
            .exclude(
                codigo_doi=""
            )
        )

        if exclude_publication_id:
            queryset = queryset.exclude(
                publicacion_id=(
                    exclude_publication_id
                )
            )

        for article in queryset.iterator():
            if normalize_doi(
                article.codigo_doi
            ) != doi:
                continue

            publication = (
                _base_queryset()
                .get(
                    pk=article.publicacion_id
                )
            )

            _add_match(
                blocking,
                publication,
                level="bloqueante",
                criterion="doi",
                reason=(
                    "El DOI coincide con el de un artículo ya "
                    "registrado en el SGPC."
                ),
            )

    # --------------------------------------------------------
    # 3. ISBN de libro: identidad bibliográfica fuerte
    # --------------------------------------------------------

    if (
        category == "libro"
        and isbn
    ):
        queryset = (
            Libro.objects
            .select_related(
                "publicacion",
                "publicacion__tipo",
            )
            .exclude(
                codigo_isbn=""
            )
        )

        if exclude_publication_id:
            queryset = queryset.exclude(
                publicacion_id=(
                    exclude_publication_id
                )
            )

        for book in queryset.iterator():
            if normalize_isbn(
                book.codigo_isbn
            ) != isbn:
                continue

            publication = (
                _base_queryset()
                .get(
                    pk=book.publicacion_id
                )
            )

            _add_match(
                blocking,
                publication,
                level="bloqueante",
                criterion="isbn_libro",
                reason=(
                    "El ISBN coincide con el de un libro ya "
                    "registrado en el SGPC."
                ),
            )

    # --------------------------------------------------------
    # 4. Capítulo: ISBN compartido + mismo capítulo
    # --------------------------------------------------------

    if (
        category == "capitulo"
        and isbn
        and normalized_title
    ):
        queryset = (
            CapituloLibro.objects
            .select_related(
                "publicacion",
                "publicacion__tipo",
            )
            .exclude(
                codigo_isbn=""
            )
        )

        if exclude_publication_id:
            queryset = queryset.exclude(
                publicacion_id=(
                    exclude_publication_id
                )
            )

        for chapter in queryset.iterator():
            if normalize_isbn(
                chapter.codigo_isbn
            ) != isbn:
                continue

            if normalize_title(
                chapter.nombre_capitulo
            ) != normalized_title:
                continue

            publication = (
                _base_queryset()
                .get(
                    pk=chapter.publicacion_id
                )
            )

            _add_match(
                blocking,
                publication,
                level="bloqueante",
                criterion=(
                    "isbn_capitulo_titulo"
                ),
                reason=(
                    "Ya existe un capítulo con el mismo ISBN y "
                    "el mismo título normalizado."
                ),
            )

    # --------------------------------------------------------
    # 5. Título + año: advertencia, nunca bloqueo automático
    # --------------------------------------------------------

    if (
        category
        and year
        and normalized_title
    ):
        queryset = (
            _base_queryset()
            .filter(
                tipo__categoria=category,
                anio_publicacion=year,
            )
        )

        if exclude_publication_id:
            queryset = queryset.exclude(
                pk=exclude_publication_id
            )

        for publication in queryset:
            existing_title = (
                _publication_title(
                    publication
                )
            )

            normalized_existing = (
                normalize_title(
                    existing_title
                )
            )

            if not normalized_existing:
                continue

            similarity = SequenceMatcher(
                None,
                normalized_title,
                normalized_existing,
            ).ratio()

            if (
                similarity
                < TITLE_SIMILARITY_WARNING_THRESHOLD
            ):
                continue

            if publication.pk in blocking:
                # La coincidencia fuerte ya contiene una razón
                # suficiente para detener el registro.
                continue

            reason = (
                "Existe una publicación del mismo año y categoría "
                "con un título igual o muy similar. Revísela antes "
                "de continuar."
            )

            _add_match(
                warnings,
                publication,
                level="advertencia",
                criterion="titulo_anio",
                reason=reason,
                similarity=similarity,
            )

    return {
        "tiene_bloqueantes": bool(
            blocking
        ),
        "tiene_advertencias": bool(
            warnings
        ),
        "bloqueantes": _render_store(
            blocking
        ),
        "advertencias": _render_store(
            warnings
        ),
        "criterios": {
            "sha256": bool(
                sha256
            ),
            "doi": bool(
                doi
            ),
            "isbn": bool(
                isbn
            ),
            "titulo": bool(
                normalized_title
            ),
            "anio": year,
            "umbral_similitud_titulo": (
                TITLE_SIMILARITY_WARNING_THRESHOLD
            ),
        },
    }


def analizar_duplicados_candidato(
    data,
    *,
    uploaded_file=None,
    exclude_publication_id=None,
):
    """Analiza un payload sin crear ni modificar la publicación."""

    values = _candidate_values_from_payload(
        data,
        uploaded_file=uploaded_file,
    )

    return _analyse_values(
        values,
        exclude_publication_id=(
            exclude_publication_id
            or data.get(
                "excluir_publicacion_id"
            )
        ),
    )


def analizar_duplicados_publicacion(
    publicacion,
):
    if publicacion is None:
        raise ValidationError(
            {
                "publicacion": [
                    "La publicación es obligatoria."
                ]
            }
        )

    # Recarga relaciones y metadatos generados por el modelo.
    publication = (
        _base_queryset()
        .get(
            pk=publicacion.pk
        )
    )

    values = (
        _candidate_values_from_publication(
            publication
        )
    )

    return _analyse_values(
        values,
        exclude_publication_id=(
            publication.pk
        ),
    )


def _relevant_strong_fields(
    publication,
):
    category = _text(
        getattr(
            getattr(publication, "tipo", None),
            "categoria",
            "",
        )
    ).lower()

    fields = {
        "archivo_pdf",
    }

    if category == "articulo":
        fields.add(
            "codigo_doi"
        )

    elif category == "libro":
        fields.add(
            "codigo_isbn"
        )

    elif category == "capitulo":
        fields.update(
            {
                "codigo_isbn",
                "nombre_capitulo",
            }
        )

    return fields


def validar_duplicados_fuerte_publicacion(
    publicacion,
    *,
    campos_modificados=None,
):
    """
    Impide únicamente coincidencias fuertes.

    En actualización se comprueban solo cuando cambió un campo que
    participa en un criterio fuerte, evitando que duplicados históricos
    preexistentes bloqueen ediciones de campos no relacionados.
    """

    if publicacion is None:
        return None

    if campos_modificados is not None:
        modified = {
            _text(field)
            for field in campos_modificados
            if _text(field)
        }

        if not (
            modified
            & _relevant_strong_fields(
                publicacion
            )
        ):
            return {
                "tiene_bloqueantes": False,
                "tiene_advertencias": False,
                "bloqueantes": [],
                "advertencias": [],
                "criterios": {},
            }

    result = analizar_duplicados_publicacion(
        publicacion
    )

    if not result[
        "tiene_bloqueantes"
    ]:
        return result

    raise ValidationError(
        {
            "duplicados": [
                (
                    "Se detectó una coincidencia fuerte con una "
                    "publicación existente. No se guardaron los cambios."
                )
            ],
            "coincidencias": result[
                "bloqueantes"
            ],
        }
    )