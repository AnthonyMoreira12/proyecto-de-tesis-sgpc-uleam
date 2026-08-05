"""
Vista pública de búsqueda académica general.

Permite buscar simultáneamente:

- Investigadores.
- Proyectos.
- Publicaciones.
- Autores.

El endpoint conserva las colecciones históricas ``usuarios`` y ``autores``
para compatibilidad, pero también expone ``investigadores`` como colección
canónica deduplicada mediante ``Autor.id``.

La búsqueda es únicamente de lectura. Los parámetros recibidos se validan
antes de ejecutar consultas en PostgreSQL y las respuestas no se almacenan
en caché.
"""

import logging
import unicodedata

from django.db import DatabaseError

from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.busqueda.selectors.busqueda_general_selectors import (
    MAX_SEARCH_LIMIT,
    MAX_SEARCH_QUERY_LENGTH,
    SEARCH_LIMIT,
    buscar_autores,
    buscar_proyectos,
    buscar_publicaciones,
    buscar_usuarios,
)
from core.busqueda.serializers.busqueda_autor_serializers import (
    AutorBusquedaSerializer,
)
from core.busqueda.serializers.busqueda_proyecto_serializers import (
    ProyectoBusquedaSerializer,
)
from core.busqueda.serializers.busqueda_publicacion_serializers import (
    PublicacionBusquedaSerializer,
)
from core.busqueda.serializers.busqueda_usuario_serializers import (
    UsuarioBusquedaSerializer,
)


logger = logging.getLogger(__name__)


# ============================================================
# SERIALIZER DE PARÁMETROS
# ============================================================

class BusquedaGeneralQuerySerializer(serializers.Serializer):
    """Valida los parámetros de la búsqueda general."""

    q = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=MAX_SEARCH_QUERY_LENGTH,
        default="",
        error_messages={
            "max_length": (
                "El término de búsqueda no puede superar "
                f"los {MAX_SEARCH_QUERY_LENGTH} caracteres."
            ),
        },
    )

    limit = serializers.IntegerField(
        required=False,
        default=SEARCH_LIMIT,
        min_value=1,
        max_value=MAX_SEARCH_LIMIT,
        error_messages={
            "invalid": "El límite debe ser un número entero.",
            "min_value": "El límite debe ser mayor que cero.",
            "max_value": (
                "El límite no puede superar "
                f"{MAX_SEARCH_LIMIT} resultados por sección."
            ),
        },
    )

    solo_con_pdf = serializers.BooleanField(
        required=False,
        default=False,
        error_messages={
            "invalid": "El filtro de PDF debe ser verdadero o falso.",
        },
    )

    def validate_q(self, value):
        """Normaliza Unicode y elimina espacios repetidos."""
        normalized_query = unicodedata.normalize(
            "NFKC",
            str(value or ""),
        )

        normalized_query = " ".join(normalized_query.split())

        if len(normalized_query) > MAX_SEARCH_QUERY_LENGTH:
            raise serializers.ValidationError(
                "El término de búsqueda no puede superar "
                f"los {MAX_SEARCH_QUERY_LENGTH} caracteres."
            )

        return normalized_query


# ============================================================
# UTILIDADES DE PARÁMETROS
# ============================================================

def _normalize_boolean_alias(value):
    """Convierte los formatos booleanos utilizados por el frontend."""
    if isinstance(value, bool):
        return value

    if value in (None, ""):
        return False

    normalized = str(value).strip().lower()

    true_values = {
        "1",
        "true",
        "t",
        "yes",
        "y",
        "si",
        "sí",
        "on",
    }

    false_values = {
        "0",
        "false",
        "f",
        "no",
        "n",
        "off",
    }

    if normalized in true_values:
        return True

    if normalized in false_values:
        return False

    return value


def _get_pdf_filter_value(request):
    """Obtiene el filtro PDF utilizando los aliases admitidos."""
    aliases = (
        "solo_con_pdf",
        "solo_pdf",
        "con_pdf",
        "has_pdf",
    )

    for alias in aliases:
        if alias in request.query_params:
            return _normalize_boolean_alias(
                request.query_params.get(alias)
            )

    return False


# ============================================================
# UTILIDADES DE INVESTIGADORES
# ============================================================

def _canonical_researcher_id(record):
    """Obtiene ``Autor.id`` desde un resultado serializado."""
    if not isinstance(record, dict):
        return None

    value = record.get("autor_id") or record.get("id")

    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return parsed if parsed > 0 else None


def _profile_is_available(record):
    """Descarta cuentas que todavía no tienen un perfil Autor."""
    if not isinstance(record, dict):
        return False

    if record.get("perfil_disponible") is False:
        return False

    return _canonical_researcher_id(record) is not None


def _merge_unique_text_lists(first, second):
    """Une dos listas de texto sin duplicados."""
    seen = set()
    result = []

    for value in [
        *(first if isinstance(first, list) else []),
        *(second if isinstance(second, list) else []),
    ]:
        normalized = " ".join(str(value or "").split())
        if not normalized:
            continue

        key = normalized.casefold()
        if key in seen:
            continue

        seen.add(key)
        result.append(normalized)

    return result


def _merge_researcher_record(current, incoming):
    """Completa un investigador sin sobrescribir datos útiles."""
    merged = dict(current)

    for field_name, value in incoming.items():
        if field_name in {"id", "autor_id"}:
            continue

        if field_name == "tags":
            merged[field_name] = _merge_unique_text_lists(
                merged.get(field_name),
                value,
            )
            continue

        if field_name in {"publications", "publicaciones_count"}:
            try:
                current_count = int(merged.get(field_name) or 0)
            except (TypeError, ValueError, OverflowError):
                current_count = 0

            try:
                incoming_count = int(value or 0)
            except (TypeError, ValueError, OverflowError):
                incoming_count = 0

            merged[field_name] = max(current_count, incoming_count)
            continue

        current_value = merged.get(field_name)

        if current_value in (None, "", [], {}):
            merged[field_name] = value

    researcher_id = _canonical_researcher_id(merged)
    merged["id"] = researcher_id
    merged["autor_id"] = researcher_id

    return merged


def _build_canonical_researchers(author_records, user_records):
    """
    Construye la colección pública canónica de investigadores.

    Los autores se procesan primero porque ``Autor`` es la entidad académica
    principal. Los Usuarios únicamente completan datos visuales faltantes.
    """
    records_by_id = {}
    ordered_ids = []

    for source in (author_records, user_records):
        for raw_record in source:
            record = dict(raw_record)

            if not _profile_is_available(record):
                continue

            researcher_id = _canonical_researcher_id(record)
            record["id"] = researcher_id
            record["autor_id"] = researcher_id

            if researcher_id not in records_by_id:
                records_by_id[researcher_id] = record
                ordered_ids.append(researcher_id)
                continue

            records_by_id[researcher_id] = _merge_researcher_record(
                records_by_id[researcher_id],
                record,
            )

    return [records_by_id[item_id] for item_id in ordered_ids]


# ============================================================
# UTILIDADES DE RESPUESTA
# ============================================================

def _build_counts(*, users, authors, researchers, projects, publications):
    """Construye conteos consistentes para el frontend."""
    return {
        "usuarios": len(users),
        "autores": len(authors),
        "investigadores": len(researchers),
        "proyectos": len(projects),
        "publicaciones": len(publications),
        # Evita contar dos veces al mismo investigador.
        "total": len(researchers) + len(projects) + len(publications),
    }


def _empty_search_payload(*, query="", limit=SEARCH_LIMIT, only_with_pdf=False):
    """Devuelve la estructura estable utilizada por el frontend."""
    counts = _build_counts(
        users=[],
        authors=[],
        researchers=[],
        projects=[],
        publications=[],
    )

    return {
        "query": query,
        "limit": limit,
        "filters": {
            "solo_con_pdf": bool(only_with_pdf),
            "has_pdf": bool(only_with_pdf),
        },
        "usuarios": [],
        "autores": [],
        "investigadores": [],
        "proyectos": [],
        "publicaciones": [],
        "counts": counts,
        "total": counts["total"],
        "truncated": {
            "usuarios": False,
            "autores": False,
            "investigadores": False,
            "proyectos": False,
            "publicaciones": False,
        },
    }


def _no_store_response(payload, *, status_code=status.HTTP_200_OK):
    """Construye una respuesta que no debe almacenarse en caché."""
    response = Response(payload, status=status_code)

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0, private"
    )
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


# ============================================================
# VISTA
# ============================================================

class BusquedaGeneralAPIView(APIView):
    """
    Endpoint público de búsqueda académica general.

    Ejemplos:

        GET /api/busqueda/?q=inteligencia&limit=8
        GET /api/busqueda/?q=software&has_pdf=true
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request):
        """Valida los parámetros y ejecuta los cuatro selectores."""
        query_data = {
            "q": request.query_params.get("q", ""),
            "limit": request.query_params.get("limit", SEARCH_LIMIT),
            "solo_con_pdf": _get_pdf_filter_value(request),
        }

        query_serializer = BusquedaGeneralQuerySerializer(
            data=query_data,
            context={"request": request},
        )

        if not query_serializer.is_valid():
            return _no_store_response(
                query_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        query = query_serializer.validated_data["q"]
        limit = query_serializer.validated_data["limit"]
        only_with_pdf = query_serializer.validated_data["solo_con_pdf"]

        if not query:
            return _no_store_response(
                _empty_search_payload(
                    query=query,
                    limit=limit,
                    only_with_pdf=only_with_pdf,
                ),
                status_code=status.HTTP_200_OK,
            )

        try:
            users = buscar_usuarios(query, limit=limit)
            projects = buscar_proyectos(query, limit=limit)
            publications = buscar_publicaciones(
                query,
                limit=limit,
                solo_con_pdf=only_with_pdf,
            )
            authors = buscar_autores(query, limit=limit)

            serializer_context = {"request": request}

            user_records = list(
                UsuarioBusquedaSerializer(
                    users,
                    many=True,
                    context=serializer_context,
                ).data
            )

            # Las cuentas sin Autor no tienen un perfil científico público.
            user_records = [
                dict(record)
                for record in user_records
                if _profile_is_available(dict(record))
            ]

            author_records = [
                dict(record)
                for record in AutorBusquedaSerializer(
                    authors,
                    many=True,
                    context=serializer_context,
                ).data
            ]

            project_records = [
                dict(record)
                for record in ProyectoBusquedaSerializer(
                    projects,
                    many=True,
                    context=serializer_context,
                ).data
            ]

            publication_records = [
                dict(record)
                for record in PublicacionBusquedaSerializer(
                    publications,
                    many=True,
                    context=serializer_context,
                ).data
            ]

            researcher_records = _build_canonical_researchers(
                author_records,
                user_records,
            )

            counts = _build_counts(
                users=user_records,
                authors=author_records,
                researchers=researcher_records,
                projects=project_records,
                publications=publication_records,
            )

            payload = {
                "query": query,
                "limit": limit,
                "filters": {
                    "solo_con_pdf": bool(only_with_pdf),
                    "has_pdf": bool(only_with_pdf),
                },

                # Contrato histórico.
                "usuarios": user_records,
                "autores": author_records,
                "proyectos": project_records,
                "publicaciones": publication_records,

                # Contrato canónico recomendado.
                "investigadores": researcher_records,

                "counts": counts,
                "total": counts["total"],

                # No representa un conteo total de base de datos. Indica que
                # la sección alcanzó el límite solicitado y podría contener
                # más coincidencias.
                "truncated": {
                    "usuarios": len(user_records) >= limit,
                    "autores": len(author_records) >= limit,
                    "investigadores": len(researcher_records) >= limit,
                    "proyectos": len(project_records) >= limit,
                    "publicaciones": len(publication_records) >= limit,
                },
            }

        except DatabaseError:
            logger.exception(
                "Error de base de datos durante la búsqueda académica general."
            )

            return _no_store_response(
                {
                    "detail": (
                        "La búsqueda no está disponible temporalmente "
                        "debido a un error de la base de datos."
                    )
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return _no_store_response(
            payload,
            status_code=status.HTTP_200_OK,
        )