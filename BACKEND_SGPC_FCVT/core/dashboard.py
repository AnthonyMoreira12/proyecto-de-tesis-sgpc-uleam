# core/dashboard.py
# ============================================================
# SGPC ULEAM — Dashboard institucional + reporte Excel
# ============================================================

from io import BytesIO

from django.apps import apps
from django.db.models import Count, F
from django.db.models.functions import (
    ExtractMonth,
    ExtractYear,
)
from django.http import HttpResponse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import get_column_letter

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

TOP_DEFAULT = 10

TOP_ALLOWED = {
    5,
    10,
    15,
    20,
}


MONTH_LABELS_ES = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}


# ============================================================
# TIPOS CANÓNICOS DEL DASHBOARD
#
# IMPORTANTE:
#
# Estos códigos se conservan porque forman parte del contrato
# actual entre dashboard y frontend.
#
# No corresponden necesariamente al campo TipoPublicacion.codigo.
#
# AAI -> Artículo de alto impacto
# AR  -> Artículo regional
# PON -> Ponencia
# CAP -> Capítulo de libro
# LIB -> Libro
# ============================================================

CANONICAL_TYPES = (
    {
        "codigo": "AAI",
        "nombre": "Artículo de alto impacto",
        "categoria": "articulo",
        "orden": 1,
    },
    {
        "codigo": "AR",
        "nombre": "Artículo regional",
        "categoria": "articulo",
        "orden": 2,
    },
    {
        "codigo": "PON",
        "nombre": "Ponencia",
        "categoria": "ponencia",
        "orden": 3,
    },
    {
        "codigo": "CAP",
        "nombre": "Capítulo de libro",
        "categoria": "capitulo",
        "orden": 4,
    },
    {
        "codigo": "LIB",
        "nombre": "Libro",
        "categoria": "libro",
        "orden": 5,
    },
    {
        "codigo": "OTRO",
        "nombre": "Otro",
        "categoria": "otro",
        "orden": 99,
    },
)


CANONICAL_CODES = {
    item["codigo"]
    for item in CANONICAL_TYPES
}


CANONICAL_PRIMARY_CODES = (
    "AAI",
    "AR",
    "PON",
    "CAP",
    "LIB",
)


# ============================================================
# ALIASES
#
# Esto permite que el dashboard acepte tanto:
#
# ?tipo_codigo=AAI
#
# como:
#
# ?tipo_codigo=articulo_alto_impacto
#
# sin romper el frontend existente.
# ============================================================

CANONICAL_ALIASES = {
    # Alto impacto
    "AAI": "AAI",
    "ALTO_IMPACTO": "AAI",
    "ARTICULO_ALTO_IMPACTO": "AAI",

    # Regional
    "AR": "AR",
    "REGIONAL": "AR",
    "ARTICULO_REGIONAL": "AR",

    # Ponencia
    "PON": "PON",
    "PONENCIA": "PON",

    # Capítulo
    "CAP": "CAP",
    "CAPITULO": "CAP",
    "CAPITULO_LIBRO": "CAP",

    # Libro
    "LIB": "LIB",
    "LIBRO": "LIB",

    # Otros
    "OTRO": "OTRO",
}


# ============================================================
# MODEL RESOLVERS
# ============================================================


def get_publicacion_model():
    return apps.get_model(
        "core",
        "Publicacion",
    )


def get_articulo_model():
    return apps.get_model(
        "core",
        "Articulo",
    )


def get_ponencia_model():
    return apps.get_model(
        "core",
        "Ponencia",
    )


def get_libro_model():
    return apps.get_model(
        "core",
        "Libro",
    )


def get_capitulo_libro_model():
    return apps.get_model(
        "core",
        "CapituloLibro",
    )


def get_publicacion_autor_model():
    return apps.get_model(
        "core",
        "PublicacionAutor",
    )


def get_facultad_model():
    return apps.get_model(
        "core",
        "Facultad",
    )


def get_carrera_model():
    return apps.get_model(
        "core",
        "Carrera",
    )


# ============================================================
# HELPERS GENERALES
# ============================================================


def _safe_int(value):
    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return None


def _safe_top(value):
    top = (
        _safe_int(value)
        or TOP_DEFAULT
    )

    return (
        top
        if top in TOP_ALLOWED
        else TOP_DEFAULT
    )


def _label(
    value,
    fallback="Sin dato",
):
    value = str(
        value or ""
    ).strip()

    return (
        value
        if value
        else fallback
    )


def _normalize_canonical_code(
    value,
):
    """
    Normaliza códigos y aliases enviados desde frontend.

    Ejemplos:

        AAI
        articulo_alto_impacto
        alto-impacto

    -> AAI
    """

    raw = str(
        value or ""
    ).strip()

    if not raw:
        return None

    normalized = (
        raw.upper()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return (
        CANONICAL_ALIASES.get(
            normalized
        )
    )


def _canonical_meta(
    code,
):
    normalized = (
        _normalize_canonical_code(
            code
        )
        or "OTRO"
    )

    for item in CANONICAL_TYPES:
        if (
            item["codigo"]
            == normalized
        ):
            return item

    return next(
        item
        for item in CANONICAL_TYPES
        if item["codigo"] == "OTRO"
    )


def _normalize_year_range(
    anio_desde,
    anio_hasta,
):
    if (
        anio_desde
        and anio_hasta
        and anio_desde > anio_hasta
    ):
        return (
            anio_hasta,
            anio_desde,
        )

    return (
        anio_desde,
        anio_hasta,
    )


# ============================================================
# QUERYSETS BASE Y FILTROS
# ============================================================


def _build_base_queryset(
    params,
):
    Publicacion = (
        get_publicacion_model()
    )

    queryset = (
        Publicacion.objects
        .select_related(
            "tipo",

            "carrera",
            "carrera__facultad",

            "area",
            "subarea",

            "pais",
            "ciudad",

            "proyecto",
        )
    )

    facultad_id = _safe_int(
        params.get(
            "facultad_id"
        )
    )

    carrera_id = _safe_int(
        params.get(
            "carrera_id"
        )
    )

    anio_desde = _safe_int(
        params.get(
            "anio_desde"
        )
    )

    anio_hasta = _safe_int(
        params.get(
            "anio_hasta"
        )
    )

    (
        anio_desde,
        anio_hasta,
    ) = _normalize_year_range(
        anio_desde,
        anio_hasta,
    )

    # --------------------------------------------------------
    # Facultad
    #
    # Publicacion NO tiene facultad directa.
    #
    # Publicacion -> Carrera -> Facultad
    # --------------------------------------------------------

    if facultad_id:
        queryset = queryset.filter(
            carrera__facultad_id=(
                facultad_id
            )
        )

    # --------------------------------------------------------
    # Carrera
    # --------------------------------------------------------

    if carrera_id:
        queryset = queryset.filter(
            carrera_id=carrera_id
        )

    # --------------------------------------------------------
    # Año desde
    # --------------------------------------------------------

    if anio_desde:
        queryset = queryset.filter(
            anio_publicacion__gte=(
                anio_desde
            )
        )

    # --------------------------------------------------------
    # Año hasta
    # --------------------------------------------------------

    if anio_hasta:
        queryset = queryset.filter(
            anio_publicacion__lte=(
                anio_hasta
            )
        )

    return queryset


# ============================================================
# RESOLUCIÓN DE TIPOS CANÓNICOS
# ============================================================


def _build_canonical_id_sources(
    publicaciones,
):
    Articulo = (
        get_articulo_model()
    )

    Ponencia = (
        get_ponencia_model()
    )

    Libro = (
        get_libro_model()
    )

    CapituloLibro = (
        get_capitulo_libro_model()
    )

    return {
        "AAI": (
            Articulo.objects
            .filter(
                publicacion__in=(
                    publicaciones
                ),
                tipo_articulo=(
                    "alto_impacto"
                ),
            )
            .values_list(
                "publicacion_id",
                flat=True,
            )
            .distinct()
        ),

        "AR": (
            Articulo.objects
            .filter(
                publicacion__in=(
                    publicaciones
                ),
                tipo_articulo="regional",
            )
            .values_list(
                "publicacion_id",
                flat=True,
            )
            .distinct()
        ),

        "PON": (
            Ponencia.objects
            .filter(
                publicacion__in=(
                    publicaciones
                )
            )
            .values_list(
                "publicacion_id",
                flat=True,
            )
            .distinct()
        ),

        "CAP": (
            CapituloLibro.objects
            .filter(
                publicacion__in=(
                    publicaciones
                )
            )
            .values_list(
                "publicacion_id",
                flat=True,
            )
            .distinct()
        ),

        "LIB": (
            Libro.objects
            .filter(
                publicacion__in=(
                    publicaciones
                )
            )
            .values_list(
                "publicacion_id",
                flat=True,
            )
            .distinct()
        ),
    }


def _canonical_queryset(
    publicaciones,
    code,
    id_sources=None,
):
    normalized = (
        _normalize_canonical_code(
            code
        )
    )

    if not normalized:
        return publicaciones.none()

    if id_sources is None:
        id_sources = (
            _build_canonical_id_sources(
                publicaciones
            )
        )

    # --------------------------------------------------------
    # OTRO
    # --------------------------------------------------------

    if normalized == "OTRO":
        queryset = publicaciones

        for primary_code in (
            CANONICAL_PRIMARY_CODES
        ):
            source = id_sources.get(
                primary_code
            )

            if source is not None:
                queryset = (
                    queryset.exclude(
                        id__in=source
                    )
                )

        return queryset

    # --------------------------------------------------------
    # Tipo normal
    # --------------------------------------------------------

    source = id_sources.get(
        normalized
    )

    if source is None:
        return publicaciones.none()

    return publicaciones.filter(
        id__in=source
    )


def _apply_canonical_type_filter(
    publicaciones,
    tipo_codigo=None,
    id_sources=None,
):
    normalized = (
        _normalize_canonical_code(
            tipo_codigo
        )
    )

    if not normalized:
        return publicaciones

    return _canonical_queryset(
        publicaciones,
        normalized,
        id_sources=id_sources,
    )


def _count_by_canonical_type(
    publicaciones,
    id_sources=None,
):
    if id_sources is None:
        id_sources = (
            _build_canonical_id_sources(
                publicaciones
            )
        )

    counts = {}

    for item in CANONICAL_TYPES:
        code = item["codigo"]

        counts[code] = (
            _canonical_queryset(
                publicaciones,
                code,
                id_sources=id_sources,
            )
            .count()
        )

    return counts


# ============================================================
# PUBLICACIONES POR AÑO
# ============================================================


def _build_publicaciones_por_anio(
    publicaciones,
):
    rows = (
        publicaciones
        .exclude(
            anio_publicacion__isnull=True
        )
        .values(
            "anio_publicacion"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "anio_publicacion"
        )
    )

    return [
        {
            "label": str(
                row[
                    "anio_publicacion"
                ]
            ),
            "value": int(
                row["total"]
                or 0
            ),
        }
        for row in rows
    ]


# ============================================================
# PUBLICACIONES POR MES
# ============================================================


def _resolve_anio_base_mensual(
    publicaciones,
    explicit_year=None,
):
    if explicit_year:
        return explicit_year

    ultimo_anio_fecha = (
        publicaciones
        .exclude(
            fecha_publicacion__isnull=True
        )
        .annotate(
            fecha_year=ExtractYear(
                "fecha_publicacion"
            )
        )
        .values_list(
            "fecha_year",
            flat=True,
        )
        .distinct()
        .order_by(
            "-fecha_year"
        )
        .first()
    )

    if ultimo_anio_fecha:
        return ultimo_anio_fecha

    return (
        publicaciones
        .exclude(
            anio_publicacion__isnull=True
        )
        .values_list(
            "anio_publicacion",
            flat=True,
        )
        .order_by(
            "-anio_publicacion"
        )
        .first()
    )


def _build_publicaciones_por_mes(
    publicaciones,
    explicit_year=None,
):
    anio_base = (
        _resolve_anio_base_mensual(
            publicaciones,
            explicit_year=(
                explicit_year
            ),
        )
    )

    qs_fechadas = (
        publicaciones
        .exclude(
            fecha_publicacion__isnull=True
        )
        .annotate(
            fecha_year=ExtractYear(
                "fecha_publicacion"
            ),
            month=ExtractMonth(
                "fecha_publicacion"
            ),
        )
    )

    total_publicaciones = (
        publicaciones.count()
    )

    total_con_fecha = (
        qs_fechadas.count()
    )

    total_sin_fecha = max(
        total_publicaciones
        - total_con_fecha,
        0,
    )

    if anio_base:
        qs_anio = (
            qs_fechadas.filter(
                fecha_year=anio_base
            )
        )
    else:
        qs_anio = (
            qs_fechadas.none()
        )

    rows = (
        qs_anio
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    totals = {
        row["month"]: int(
            row["total"]
            or 0
        )
        for row in rows
        if row["month"]
    }

    return {
        "anio_base": (
            anio_base
        ),

        "items": [
            {
                "label": (
                    MONTH_LABELS_ES[i]
                ),
                "value": (
                    totals.get(
                        i,
                        0,
                    )
                ),
            }
            for i in range(
                1,
                13,
            )
        ],

        "total_publicaciones_anio": (
            qs_anio.count()
        ),

        "total_con_fecha": (
            total_con_fecha
        ),

        "total_sin_fecha": (
            total_sin_fecha
        ),
    }


# ============================================================
# PUBLICACIONES POR TIPO
# ============================================================


def _build_publicaciones_por_tipo(
    publicaciones,
    selected_tipo_codigo=None,
    id_sources=None,
):
    total_publicaciones = (
        publicaciones.count()
    )

    counts = (
        _count_by_canonical_type(
            publicaciones,
            id_sources=id_sources,
        )
    )

    all_items = []

    for item in CANONICAL_TYPES:
        code = item["codigo"]

        total = int(
            counts.get(
                code,
                0,
            )
            or 0
        )

        porcentaje = (
            round(
                (
                    total
                    / total_publicaciones
                )
                * 100,
                2,
            )
            if total_publicaciones
            else 0
        )

        all_items.append(
            {
                "tipo_id": code,
                "tipo_codigo": code,
                "tipo_nombre": (
                    item["nombre"]
                ),
                "categoria": (
                    item["categoria"]
                ),
                "total": total,
                "porcentaje": (
                    porcentaje
                ),
            }
        )

    items = [
        item
        for item in all_items
        if item["total"] > 0
    ]

    selected_code = (
        _normalize_canonical_code(
            selected_tipo_codigo
        )
    )

    seleccionado = None

    if selected_code:
        seleccionado = next(
            (
                item
                for item in all_items
                if (
                    item["tipo_codigo"]
                    == selected_code
                )
            ),
            None,
        )

    return {
        "total_publicaciones": (
            total_publicaciones
        ),
        "seleccionado": (
            seleccionado
        ),
        "items": items,
    }


# ============================================================
# TIPO POR AÑO
# ============================================================


def _build_publicaciones_por_tipo_anual(
    publicaciones,
    id_sources=None,
):
    categorias = list(
        publicaciones
        .exclude(
            anio_publicacion__isnull=True
        )
        .values_list(
            "anio_publicacion",
            flat=True,
        )
        .distinct()
        .order_by(
            "anio_publicacion"
        )
    )

    if not categorias:
        return {
            "categorias": [],
            "series": [],
            "total_publicaciones": 0,
        }

    if id_sources is None:
        id_sources = (
            _build_canonical_id_sources(
                publicaciones
            )
        )

    series = []

    for item in CANONICAL_TYPES:
        code = item["codigo"]

        rows = (
            _canonical_queryset(
                publicaciones,
                code,
                id_sources=id_sources,
            )
            .exclude(
                anio_publicacion__isnull=True
            )
            .values(
                "anio_publicacion"
            )
            .annotate(
                total=Count("id")
            )
            .order_by(
                "anio_publicacion"
            )
        )

        totals_by_year = {
            row["anio_publicacion"]: int(
                row["total"]
                or 0
            )
            for row in rows
        }

        data = [
            totals_by_year.get(
                anio,
                0,
            )
            for anio in categorias
        ]

        if sum(data) <= 0:
            continue

        series.append(
            {
                "id": code,
                "codigo": code,
                "label": (
                    item["nombre"]
                ),
                "categoria": (
                    item["categoria"]
                ),
                "data": data,
            }
        )

    return {
        "categorias": [
            str(anio)
            for anio in categorias
        ],

        "series": series,

        "total_publicaciones": (
            publicaciones.count()
        ),
    }


# ============================================================
# ÁREAS
# ============================================================


def _build_top_areas(
    publicaciones,
    limit,
):
    rows = (
        publicaciones
        .exclude(
            area__isnull=True
        )
        .values(
            "area__nombre"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total",
            "area__nombre",
        )[:limit]
    )

    return {
        "limite": limit,

        "items": [
            {
                "label": _label(
                    row["area__nombre"]
                ),
                "total": int(
                    row["total"]
                    or 0
                ),
            }
            for row in rows
        ],
    }


# ============================================================
# FACULTADES
# ============================================================


def _build_top_facultades(
    publicaciones,
    limit,
):
    rows = (
        publicaciones
        .exclude(
            carrera__facultad_id__isnull=True
        )
        .values(
            facultad_id=F(
                "carrera__facultad_id"
            ),
            facultad_nombre=F(
                "carrera__facultad__nombre"
            ),
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total",
            "facultad_nombre",
        )[:limit]
    )

    return {
        "limite": limit,

        "items": [
            {
                "facultad_id": (
                    row["facultad_id"]
                ),

                "facultad": _label(
                    row["facultad_nombre"]
                ),

                "total": int(
                    row["total"]
                    or 0
                ),
            }

            for row in rows
        ],
    }


# ============================================================
# CARRERAS
# ============================================================


def _build_top_carreras(
    publicaciones,
    limit,
):
    rows = (
        publicaciones
        .exclude(
            carrera__isnull=True
        )
        .values(
            "carrera_id",
            "carrera__nombre",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total",
            "carrera__nombre",
        )[:limit]
    )

    return {
        "limite": limit,

        "items": [
            {
                "carrera_id": (
                    row["carrera_id"]
                ),

                "carrera": _label(
                    row["carrera__nombre"]
                ),

                "total": int(
                    row["total"]
                    or 0
                ),
            }

            for row in rows
        ],
    }


# ============================================================
# AUTORES
# ============================================================


def _build_top_autores_por_rol(
    publicaciones,
    limit,
    rol_autoria,
):
    PublicacionAutor = (
        get_publicacion_autor_model()
    )

    base_qs = (
        PublicacionAutor.objects
        .filter(
            publicacion__in=(
                publicaciones
            ),
            rol_autoria=(
                rol_autoria
            ),
        )
        .exclude(
            autor_id__isnull=True
        )
    )

    rows = (
        base_qs
        .values(
            "autor_id",
            "autor__nombres",
            "autor__apellidos",
        )
        .annotate(
            total_publicaciones=Count(
                "publicacion",
                distinct=True,
            )
        )
        .order_by(
            "-total_publicaciones",
            "autor__apellidos",
            "autor__nombres",
        )[:limit]
    )

    total_autores_activos = (
        base_qs
        .values(
            "autor_id"
        )
        .distinct()
        .count()
    )

    items = []

    for row in rows:
        nombre_autor = (
            f"{str(row['autor__nombres'] or '').strip()} "
            f"{str(row['autor__apellidos'] or '').strip()}"
        ).strip()

        if not nombre_autor:
            nombre_autor = (
                "Autor sin nombre"
            )

        total_publicaciones = int(
            row[
                "total_publicaciones"
            ]
            or 0
        )

        items.append(
            {
                "autor_id": (
                    row["autor_id"]
                ),

                "autor": (
                    nombre_autor
                ),

                "label": (
                    nombre_autor
                ),

                "rol_autoria": (
                    rol_autoria
                ),

                "total_publicaciones": (
                    total_publicaciones
                ),

                "total": (
                    total_publicaciones
                ),
            }
        )

    return {
        "limite": limit,
        "rol_autoria": (
            rol_autoria
        ),
        "total_autores_activos": (
            total_autores_activos
        ),
        "items": items,
    }


def _build_top_autores_principales(
    publicaciones,
    limit,
):
    return (
        _build_top_autores_por_rol(
            publicaciones=(
                publicaciones
            ),
            limit=limit,
            rol_autoria=(
                "principal"
            ),
        )
    )


def _build_top_coautores(
    publicaciones,
    limit,
):
    return (
        _build_top_autores_por_rol(
            publicaciones=(
                publicaciones
            ),
            limit=limit,
            rol_autoria=(
                "coautor"
            ),
        )
    )


def _build_top_autores(
    publicaciones,
    limit,
):
    """
    Alias de compatibilidad.

    top_autores representa actualmente a los autores
    principales, no mezcla autores principales y coautores.
    """

    return (
        _build_top_autores_principales(
            publicaciones,
            limit,
        )
    )


# ============================================================
# REVISTAS
# ============================================================


def _build_journals(
    publicaciones,
    limit,
):
    Articulo = (
        get_articulo_model()
    )

    rows = (
        Articulo.objects
        .filter(
            publicacion__in=(
                publicaciones
            )
        )
        .exclude(
            nombre_revista__isnull=True
        )
        .exclude(
            nombre_revista=""
        )
        .values(
            "nombre_revista"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total",
            "nombre_revista",
        )[:limit]
    )

    return {
        "limite": limit,

        "items": [
            {
                "label": _label(
                    row["nombre_revista"]
                ),

                "total": int(
                    row["total"]
                    or 0
                ),
            }

            for row in rows
        ],
    }


# ============================================================
# PROYECTOS
# ============================================================


def _build_projects(
    publicaciones,
    limit,
):
    rows = (
        publicaciones
        .exclude(
            proyecto__isnull=True
        )
        .values(
            "proyecto__nombre"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total",
            "proyecto__nombre",
        )[:limit]
    )

    return {
        "limite": limit,

        "items": [
            {
                "label": _label(
                    row[
                        "proyecto__nombre"
                    ]
                ),

                "total": int(
                    row["total"]
                    or 0
                ),
            }

            for row in rows
        ],
    }


# ============================================================
# SUMMARY
# ============================================================


def _build_summary(
    publicaciones,
):
    PublicacionAutor = (
        get_publicacion_autor_model()
    )

    Articulo = (
        get_articulo_model()
    )

    total_publicaciones = (
        publicaciones.count()
    )

    total_autores = (
        PublicacionAutor.objects
        .filter(
            publicacion__in=(
                publicaciones
            )
        )
        .exclude(
            autor_id__isnull=True
        )
        .values(
            "autor_id"
        )
        .distinct()
        .count()
    )

    total_facultades = (
        publicaciones
        .exclude(
            carrera__facultad_id__isnull=True
        )
        .values(
            "carrera__facultad_id"
        )
        .distinct()
        .count()
    )

    total_carreras = (
        publicaciones
        .exclude(
            carrera_id__isnull=True
        )
        .values(
            "carrera_id"
        )
        .distinct()
        .count()
    )

    total_proyectos = (
        publicaciones
        .exclude(
            proyecto_id__isnull=True
        )
        .values(
            "proyecto_id"
        )
        .distinct()
        .count()
    )

    articulos_qs = (
        Articulo.objects
        .filter(
            publicacion__in=(
                publicaciones
            )
        )
    )

    total_articulos_alto_impacto = (
        articulos_qs.filter(
            tipo_articulo=(
                "alto_impacto"
            )
        )
        .count()
    )

    total_articulos_regionales = (
        articulos_qs.filter(
            tipo_articulo="regional"
        )
        .count()
    )

    return {
        "total_publicaciones": (
            total_publicaciones
        ),

        "total_autores": (
            total_autores
        ),

        "total_facultades": (
            total_facultades
        ),

        "total_carreras": (
            total_carreras
        ),

        "total_proyectos": (
            total_proyectos
        ),

        "articulos_alto_impacto": (
            total_articulos_alto_impacto
        ),

        "articulos_regionales": (
            total_articulos_regionales
        ),
    }


# ============================================================
# FILTROS DISPONIBLES
# ============================================================


def _build_filters_metadata(
    publicaciones,
    publicaciones_para_tipos=None,
    selected_facultad_id=None,
    anio_base_mensual=None,
):
    Publicacion = (
        get_publicacion_model()
    )

    Facultad = (
        get_facultad_model()
    )

    Carrera = (
        get_carrera_model()
    )

    # IMPORTANTE:
    #
    # No utilizar:
    #
    # publicaciones_para_tipos = publicaciones_para_tipos or publicaciones
    #
    # porque un QuerySet vacío se evaluaría y podría
    # sustituirse incorrectamente.
    if publicaciones_para_tipos is None:
        publicaciones_para_tipos = (
            publicaciones
        )

    anios = list(
        publicaciones
        .exclude(
            anio_publicacion__isnull=True
        )
        .values_list(
            "anio_publicacion",
            flat=True,
        )
        .distinct()
        .order_by(
            "-anio_publicacion"
        )
    )

    # --------------------------------------------------------
    # Fallback global
    # --------------------------------------------------------

    if not anios:
        anios = list(
            Publicacion.objects
            .exclude(
                anio_publicacion__isnull=True
            )
            .values_list(
                "anio_publicacion",
                flat=True,
            )
            .distinct()
            .order_by(
                "-anio_publicacion"
            )
        )

    # --------------------------------------------------------
    # Facultades
    # --------------------------------------------------------

    facultades = list(
        Facultad.objects
        .all()
        .order_by("nombre")
        .values(
            "id",
            "nombre",
        )
    )

    # --------------------------------------------------------
    # Carreras
    # --------------------------------------------------------

    carreras_qs = (
        Carrera.objects
        .select_related(
            "facultad"
        )
        .all()
        .order_by(
            "nombre"
        )
    )

    if selected_facultad_id:
        carreras_qs = (
            carreras_qs.filter(
                facultad_id=(
                    selected_facultad_id
                )
            )
        )

    carreras = list(
        carreras_qs.values(
            "id",
            "nombre",
            "facultad_id",
        )
    )

    # --------------------------------------------------------
    # Tipos
    # --------------------------------------------------------

    canonical_counts = (
        _count_by_canonical_type(
            publicaciones_para_tipos
        )
    )

    return {
        "tipos": [
            {
                "id": (
                    item["codigo"]
                ),

                "codigo": (
                    item["codigo"]
                ),

                "nombre": (
                    item["nombre"]
                ),

                "categoria": (
                    item["categoria"]
                ),

                "total": int(
                    canonical_counts.get(
                        item["codigo"],
                        0,
                    )
                    or 0
                ),
            }

            for item in CANONICAL_TYPES
        ],

        "facultades": [
            {
                "id": (
                    row["id"]
                ),
                "nombre": (
                    row["nombre"]
                ),
            }

            for row in facultades
        ],

        "carreras": [
            {
                "id": (
                    row["id"]
                ),

                "nombre": (
                    row["nombre"]
                ),

                "facultad_id": (
                    row["facultad_id"]
                ),
            }

            for row in carreras
        ],

        "anios": [
            {
                "value": anio,
                "label": str(anio),
            }

            for anio in anios
        ],

        "anio_base_mensual": (
            anio_base_mensual
        ),
    }


# ============================================================
# FILTROS APLICADOS
# ============================================================


def _build_filtros_aplicados(
    params,
    anio_base_mensual,
):
    Facultad = (
        get_facultad_model()
    )

    Carrera = (
        get_carrera_model()
    )

    facultad_id = _safe_int(
        params.get(
            "facultad_id"
        )
    )

    carrera_id = _safe_int(
        params.get(
            "carrera_id"
        )
    )

    tipo_codigo = (
        _normalize_canonical_code(
            params.get(
                "tipo_codigo"
            )
        )
    )

    anio_desde = _safe_int(
        params.get(
            "anio_desde"
        )
    )

    anio_hasta = _safe_int(
        params.get(
            "anio_hasta"
        )
    )

    (
        anio_desde,
        anio_hasta,
    ) = _normalize_year_range(
        anio_desde,
        anio_hasta,
    )

    anio = _safe_int(
        params.get(
            "anio"
        )
    )

    top = _safe_top(
        params.get(
            "top"
        )
    )

    facultad_nombre = None
    carrera_nombre = None

    if facultad_id:
        facultad_nombre = (
            Facultad.objects
            .filter(
                id=facultad_id
            )
            .values_list(
                "nombre",
                flat=True,
            )
            .first()
        )

    if carrera_id:
        carrera_nombre = (
            Carrera.objects
            .filter(
                id=carrera_id
            )
            .values_list(
                "nombre",
                flat=True,
            )
            .first()
        )

    tipo_meta = (
        _canonical_meta(
            tipo_codigo
        )
        if tipo_codigo
        else None
    )

    return {
        "facultad_id": (
            facultad_id
        ),

        "facultad_nombre": (
            facultad_nombre
        ),

        "carrera_id": (
            carrera_id
        ),

        "carrera_nombre": (
            carrera_nombre
        ),

        "tipo_codigo": (
            tipo_codigo
        ),

        "tipo_nombre": (
            tipo_meta["nombre"]
            if tipo_meta
            else None
        ),

        "anio_desde": (
            anio_desde
        ),

        "anio_hasta": (
            anio_hasta
        ),

        "anio": (
            anio
        ),

        "anio_base_mensual": (
            anio_base_mensual
        ),

        "top": (
            top
        ),
    }


# ============================================================
# PAYLOAD PRINCIPAL
# ============================================================


def _build_dashboard_payload(
    params,
):
    selected_facultad_id = (
        _safe_int(
            params.get(
                "facultad_id"
            )
        )
    )

    selected_tipo_codigo = (
        _normalize_canonical_code(
            params.get(
                "tipo_codigo"
            )
        )
    )

    selected_month_year = (
        _safe_int(
            params.get(
                "anio"
            )
        )
    )

    top_limit = (
        _safe_top(
            params.get(
                "top"
            )
        )
    )

    # --------------------------------------------------------
    # Queryset general con filtros institucionales/año
    # --------------------------------------------------------

    publicaciones_base = (
        _build_base_queryset(
            params
        )
    )

    # --------------------------------------------------------
    # Resolución de subtipos
    # --------------------------------------------------------

    base_id_sources = (
        _build_canonical_id_sources(
            publicaciones_base
        )
    )

    # --------------------------------------------------------
    # Aplicar tipo
    # --------------------------------------------------------

    publicaciones = (
        _apply_canonical_type_filter(
            publicaciones_base,
            tipo_codigo=(
                selected_tipo_codigo
            ),
            id_sources=(
                base_id_sources
            ),
        )
    )

    # --------------------------------------------------------
    # Mensual
    # --------------------------------------------------------

    publicaciones_por_mes = (
        _build_publicaciones_por_mes(
            publicaciones,
            explicit_year=(
                selected_month_year
            ),
        )
    )

    # --------------------------------------------------------
    # Autores
    # --------------------------------------------------------

    top_autores_principales = (
        _build_top_autores_principales(
            publicaciones,
            top_limit,
        )
    )

    top_coautores = (
        _build_top_coautores(
            publicaciones,
            top_limit,
        )
    )

    # --------------------------------------------------------
    # Payload
    # --------------------------------------------------------

    return {
        "ok": True,

        "summary": (
            _build_summary(
                publicaciones
            )
        ),

        "dashboards": {
            "publicaciones_por_anio": (
                _build_publicaciones_por_anio(
                    publicaciones
                )
            ),

            "publicaciones_por_mes": (
                publicaciones_por_mes
            ),

            "publicaciones_por_tipo": (
                _build_publicaciones_por_tipo(
                    publicaciones,
                    selected_tipo_codigo=(
                        selected_tipo_codigo
                    ),
                    id_sources=(
                        base_id_sources
                    ),
                )
            ),

            "publicaciones_por_tipo_anual": (
                _build_publicaciones_por_tipo_anual(
                    publicaciones,
                    id_sources=(
                        base_id_sources
                    ),
                )
            ),

            "areas": (
                _build_top_areas(
                    publicaciones,
                    top_limit,
                )
            ),

            "top_facultades": (
                _build_top_facultades(
                    publicaciones,
                    top_limit,
                )
            ),

            "top_carreras": (
                _build_top_carreras(
                    publicaciones,
                    top_limit,
                )
            ),

            "top_autores_principales": (
                top_autores_principales
            ),

            "top_coautores": (
                top_coautores
            ),

            # Alias histórico para no romper frontend.
            "top_autores": (
                top_autores_principales
            ),

            "journals": (
                _build_journals(
                    publicaciones,
                    top_limit,
                )
            ),

            "projects": (
                _build_projects(
                    publicaciones,
                    top_limit,
                )
            ),
        },

        "filtros_disponibles": (
            _build_filters_metadata(
                publicaciones,
                publicaciones_para_tipos=(
                    publicaciones_base
                ),
                selected_facultad_id=(
                    selected_facultad_id
                ),
                anio_base_mensual=(
                    publicaciones_por_mes.get(
                        "anio_base"
                    )
                ),
            )
        ),

        "filtros_aplicados": (
            _build_filtros_aplicados(
                params,
                anio_base_mensual=(
                    publicaciones_por_mes.get(
                        "anio_base"
                    )
                ),
            )
        ),
    }


# ============================================================
# API — DASHBOARD
# ============================================================


class DashboardResumenView(
    APIView
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        payload = (
            _build_dashboard_payload(
                request.query_params
            )
        )

        return Response(
            payload
        )


# ============================================================
# REPORTE EXCEL — HELPERS
# ============================================================


def _safe_excel_value(
    value,
):
    if value is None:
        return ""

    return value


def _report_generated_at():
    return (
        timezone.localtime()
        .strftime(
            "%Y-%m-%d %H:%M"
        )
    )


def _report_filename():
    stamp = (
        timezone.localtime()
        .strftime(
            "%Y-%m-%d_%H-%M-%S"
        )
    )

    return (
        "reporte-dashboard-"
        f"sgpc-uleam-{stamp}.xlsx"
    )


# ============================================================
# ESTILO EXCEL
# ============================================================


def _style_report_sheet(
    ws,
):
    max_row = (
        ws.max_row
        or 1
    )

    max_col = (
        ws.max_column
        or 1
    )

    last_col = (
        get_column_letter(
            max_col
        )
    )

    # --------------------------------------------------------
    # Fuentes
    # --------------------------------------------------------

    title_font = Font(
        name="Calibri",
        size=15,
        bold=True,
        color="111827",
    )

    subtitle_font = Font(
        name="Calibri",
        size=10,
        color="6B7280",
    )

    header_font = Font(
        name="Calibri",
        size=10,
        bold=True,
        color="FFFFFF",
    )

    body_font = Font(
        name="Calibri",
        size=10,
        color="111827",
    )

    # --------------------------------------------------------
    # Rellenos
    # --------------------------------------------------------

    header_fill = PatternFill(
        "solid",
        fgColor="111827",
    )

    muted_fill = PatternFill(
        "solid",
        fgColor="F3F4F6",
    )

    # --------------------------------------------------------
    # Bordes
    # --------------------------------------------------------

    thin_border = Border(
        left=Side(
            style="thin",
            color="D1D5DB",
        ),
        right=Side(
            style="thin",
            color="D1D5DB",
        ),
        top=Side(
            style="thin",
            color="D1D5DB",
        ),
        bottom=Side(
            style="thin",
            color="D1D5DB",
        ),
    )

    # --------------------------------------------------------
    # Combinar título/subtítulo
    # --------------------------------------------------------

    if max_col > 1:
        ws.merge_cells(
            start_row=1,
            start_column=1,
            end_row=1,
            end_column=max_col,
        )

        ws.merge_cells(
            start_row=2,
            start_column=1,
            end_row=2,
            end_column=max_col,
        )

    # --------------------------------------------------------
    # Cuerpo
    #
    # IMPORTANTE:
    # Comenzamos desde fila 4 para NO sobrescribir los estilos
    # del título y subtítulo.
    # --------------------------------------------------------

    for row in ws.iter_rows(
        min_row=4,
        max_row=max_row,
        min_col=1,
        max_col=max_col,
    ):
        for cell in row:
            cell.font = body_font

            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True,
            )

            cell.border = (
                thin_border
            )

    # --------------------------------------------------------
    # Headers
    # --------------------------------------------------------

    if max_row >= 4:
        for cell in ws[4]:
            cell.fill = (
                header_fill
            )

            cell.font = (
                header_font
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

            cell.border = (
                thin_border
            )

    # --------------------------------------------------------
    # Filas alternadas
    # --------------------------------------------------------

    for row_index in range(
        5,
        max_row + 1,
    ):
        if row_index % 2 == 0:
            for cell in ws[
                row_index
            ]:
                cell.fill = (
                    muted_fill
                )

    # --------------------------------------------------------
    # Título
    # --------------------------------------------------------

    ws["A1"].font = (
        title_font
    )

    ws["A1"].alignment = Alignment(
        horizontal="left",
        vertical="center",
    )

    # --------------------------------------------------------
    # Subtítulo
    # --------------------------------------------------------

    ws["A2"].font = (
        subtitle_font
    )

    ws["A2"].alignment = Alignment(
        horizontal="left",
        vertical="center",
    )

    # --------------------------------------------------------
    # Altura
    # --------------------------------------------------------

    ws.row_dimensions[
        1
    ].height = 24

    ws.row_dimensions[
        2
    ].height = 20

    ws.row_dimensions[
        4
    ].height = 22

    # --------------------------------------------------------
    # Freeze + filtro
    # --------------------------------------------------------

    if max_row >= 4:
        ws.freeze_panes = (
            "A5"
        )

        ws.auto_filter.ref = (
            f"A4:{last_col}{max_row}"
        )

    # --------------------------------------------------------
    # Ancho de columnas
    #
    # Se calcula desde la fila 4 para evitar problemas
    # con las celdas combinadas de título.
    # --------------------------------------------------------

    for column_index in range(
        1,
        max_col + 1,
    ):
        max_length = 0

        for row_index in range(
            4,
            max_row + 1,
        ):
            cell = ws.cell(
                row=row_index,
                column=column_index,
            )

            value = str(
                cell.value
                or ""
            )

            max_length = max(
                max_length,
                len(value),
            )

        column_letter = (
            get_column_letter(
                column_index
            )
        )

        ws.column_dimensions[
            column_letter
        ].width = min(
            max(
                max_length + 4,
                14,
            ),
            55,
        )


# ============================================================
# CREACIÓN DE HOJAS
# ============================================================


def _create_sheet(
    workbook,
    title,
    subtitle,
    headers,
    rows,
):
    ws = workbook.create_sheet(
        title=title[:31]
    )

    ws.append(
        [title]
    )

    ws.append(
        [subtitle]
    )

    ws.append([])

    ws.append(
        headers
    )

    for row in rows:
        ws.append(
            [
                _safe_excel_value(
                    value
                )
                for value in row
            ]
        )

    _style_report_sheet(
        ws
    )

    return ws


# ============================================================
# RESUMEN EXCEL
# ============================================================


def _build_resumen_rows(
    summary,
    filtros,
):
    return [
        [
            "Publicaciones",
            summary.get(
                "total_publicaciones",
                0,
            ),
        ],
        [
            "Autores vinculados",
            summary.get(
                "total_autores",
                0,
            ),
        ],
        [
            "Facultades",
            summary.get(
                "total_facultades",
                0,
            ),
        ],
        [
            "Carreras",
            summary.get(
                "total_carreras",
                0,
            ),
        ],
        [
            "Proyectos asociados",
            summary.get(
                "total_proyectos",
                0,
            ),
        ],
        [
            "Artículos de alto impacto",
            summary.get(
                "articulos_alto_impacto",
                0,
            ),
        ],
        [
            "Artículos regionales",
            summary.get(
                "articulos_regionales",
                0,
            ),
        ],

        [
            "",
            "",
        ],

        [
            "Facultad",
            (
                filtros.get(
                    "facultad_nombre"
                )
                or "Todas"
            ),
        ],

        [
            "Carrera",
            (
                filtros.get(
                    "carrera_nombre"
                )
                or "Todas"
            ),
        ],

        [
            "Tipo de publicación",
            (
                filtros.get(
                    "tipo_nombre"
                )
                or "Todos"
            ),
        ],

        [
            "Año desde",
            (
                filtros.get(
                    "anio_desde"
                )
                or "Todos"
            ),
        ],

        [
            "Año hasta",
            (
                filtros.get(
                    "anio_hasta"
                )
                or "Todos"
            ),
        ],

        [
            "Año mensual",
            (
                filtros.get(
                    "anio"
                )
                or filtros.get(
                    "anio_base_mensual"
                )
                or "Automático"
            ),
        ],

        [
            "Top aplicado",
            (
                filtros.get(
                    "top"
                )
                or TOP_DEFAULT
            ),
        ],

        [
            "Generado el",
            _report_generated_at(),
        ],
    ]


# ============================================================
# TIPO/AÑO EXCEL
# ============================================================


def _build_tipo_anual_rows(
    publicaciones_por_tipo_anual,
):
    rows = []

    categorias = (
        publicaciones_por_tipo_anual
        .get(
            "categorias",
            [],
        )
        or []
    )

    for serie in (
        publicaciones_por_tipo_anual
        .get(
            "series",
            [],
        )
        or []
    ):
        data = (
            serie.get(
                "data",
                [],
            )
            or []
        )

        for index, anio in enumerate(
            categorias
        ):
            total = (
                data[index]
                if index < len(data)
                else 0
            )

            rows.append(
                [
                    anio,
                    serie.get(
                        "codigo"
                    ),
                    serie.get(
                        "label"
                    ),
                    total,
                ]
            )

    return rows


# ============================================================
# WORKBOOK
# ============================================================


def _build_report_workbook(
    payload,
):
    summary = (
        payload.get(
            "summary",
            {},
        )
        or {}
    )

    dashboards = (
        payload.get(
            "dashboards",
            {},
        )
        or {}
    )

    filtros = (
        payload.get(
            "filtros_aplicados",
            {},
        )
        or {}
    )

    workbook = Workbook()

    default_ws = (
        workbook.active
    )

    workbook.remove(
        default_ws
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    workbook.properties.title = (
        "Reporte dashboard SGPC ULEAM"
    )

    workbook.properties.subject = (
        "Indicadores institucionales "
        "de producción científica"
    )

    workbook.properties.creator = (
        "SGPC ULEAM"
    )

    # --------------------------------------------------------
    # Datos
    # --------------------------------------------------------

    publicaciones_por_tipo = (
        dashboards.get(
            "publicaciones_por_tipo",
            {},
        )
        or {}
    )

    publicaciones_por_anio = (
        dashboards.get(
            "publicaciones_por_anio",
            [],
        )
        or []
    )

    publicaciones_por_mes = (
        dashboards.get(
            "publicaciones_por_mes",
            {},
        )
        or {}
    )

    publicaciones_por_tipo_anual = (
        dashboards.get(
            "publicaciones_por_tipo_anual",
            {},
        )
        or {}
    )

    top_facultades = (
        dashboards.get(
            "top_facultades",
            {},
        )
        or {}
    )

    top_carreras = (
        dashboards.get(
            "top_carreras",
            {},
        )
        or {}
    )

    top_autores_principales = (
        dashboards.get(
            "top_autores_principales"
        )
        or dashboards.get(
            "top_autores"
        )
        or {}
    )

    top_coautores = (
        dashboards.get(
            "top_coautores",
            {},
        )
        or {}
    )

    journals = (
        dashboards.get(
            "journals",
            {},
        )
        or {}
    )

    projects = (
        dashboards.get(
            "projects",
            {},
        )
        or {}
    )

    areas = (
        dashboards.get(
            "areas",
            {},
        )
        or {}
    )

    # ========================================================
    # RESUMEN
    # ========================================================

    _create_sheet(
        workbook,
        "Resumen",
        (
            "Indicadores principales "
            "del panel analítico institucional."
        ),
        [
            "Indicador",
            "Valor",
        ],
        _build_resumen_rows(
            summary,
            filtros,
        ),
    )

    # ========================================================
    # PUBLICACIONES POR TIPO
    # ========================================================

    _create_sheet(
        workbook,
        "Publicaciones por tipo",
        (
            "Distribución de publicaciones "
            "por tipo."
        ),
        [
            "Tipo",
            "Código",
            "Categoría",
            "Total",
            "Porcentaje",
        ],
        [
            [
                item.get(
                    "tipo_nombre"
                ),
                item.get(
                    "tipo_codigo"
                ),
                item.get(
                    "categoria"
                ),
                item.get(
                    "total",
                    0,
                ),
                item.get(
                    "porcentaje",
                    0,
                ),
            ]
            for item in (
                publicaciones_por_tipo
                .get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # PUBLICACIONES POR AÑO
    # ========================================================

    _create_sheet(
        workbook,
        "Publicaciones por año",
        (
            "Serie histórica de "
            "publicaciones registradas."
        ),
        [
            "Año",
            "Total",
        ],
        [
            [
                item.get(
                    "label"
                ),
                item.get(
                    "value",
                    0,
                ),
            ]
            for item in publicaciones_por_anio
        ],
    )

    # ========================================================
    # PUBLICACIONES POR MES
    # ========================================================

    _create_sheet(
        workbook,
        "Publicaciones por mes",
        (
            "Detalle mensual del año "
            f"{publicaciones_por_mes.get('anio_base') or 'sin año base'}."
        ),
        [
            "Mes",
            "Total",
        ],
        [
            [
                item.get(
                    "label"
                ),
                item.get(
                    "value",
                    0,
                ),
            ]
            for item in (
                publicaciones_por_mes
                .get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # TIPO POR AÑO
    # ========================================================

    _create_sheet(
        workbook,
        "Tipo por año",
        (
            "Comparativa anual por "
            "tipo de publicación."
        ),
        [
            "Año",
            "Código",
            "Tipo",
            "Total",
        ],
        _build_tipo_anual_rows(
            publicaciones_por_tipo_anual
        ),
    )

    # ========================================================
    # FACULTADES
    # ========================================================

    _create_sheet(
        workbook,
        "Top facultades",
        (
            "Facultades con más "
            "publicaciones."
        ),
        [
            "Facultad",
            "Total",
        ],
        [
            [
                item.get(
                    "facultad"
                ),
                item.get(
                    "total",
                    0,
                ),
            ]
            for item in (
                top_facultades
                .get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # CARRERAS
    # ========================================================

    _create_sheet(
        workbook,
        "Top carreras",
        (
            "Carreras con más "
            "publicaciones."
        ),
        [
            "Carrera",
            "Total",
        ],
        [
            [
                item.get(
                    "carrera"
                ),
                item.get(
                    "total",
                    0,
                ),
            ]
            for item in (
                top_carreras
                .get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # AUTORES PRINCIPALES
    # ========================================================

    _create_sheet(
        workbook,
        "Autores principales",
        (
            "Autores principales con más "
            "publicaciones lideradas."
        ),
        [
            "Autor principal",
            "Total publicaciones",
        ],
        [
            [
                (
                    item.get(
                        "autor"
                    )
                    or item.get(
                        "label"
                    )
                ),
                item.get(
                    "total_publicaciones",
                    item.get(
                        "total",
                        0,
                    ),
                ),
            ]
            for item in (
                top_autores_principales
                .get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # COAUTORES
    # ========================================================

    _create_sheet(
        workbook,
        "Coautores",
        (
            "Coautores con mayor "
            "participación colaborativa."
        ),
        [
            "Coautor",
            "Total participaciones",
        ],
        [
            [
                (
                    item.get(
                        "autor"
                    )
                    or item.get(
                        "label"
                    )
                ),
                item.get(
                    "total_publicaciones",
                    item.get(
                        "total",
                        0,
                    ),
                ),
            ]
            for item in (
                top_coautores
                .get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # REVISTAS
    # ========================================================

    _create_sheet(
        workbook,
        "Revistas",
        (
            "Revistas con más artículos "
            "registrados."
        ),
        [
            "Revista",
            "Total",
        ],
        [
            [
                item.get(
                    "label"
                ),
                item.get(
                    "total",
                    0,
                ),
            ]
            for item in (
                journals.get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # PROYECTOS
    # ========================================================

    _create_sheet(
        workbook,
        "Proyectos",
        (
            "Proyectos con más "
            "publicaciones asociadas."
        ),
        [
            "Proyecto",
            "Total",
        ],
        [
            [
                item.get(
                    "label"
                ),
                item.get(
                    "total",
                    0,
                ),
            ]
            for item in (
                projects.get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    # ========================================================
    # ÁREAS
    # ========================================================

    _create_sheet(
        workbook,
        "Áreas",
        (
            "Áreas del conocimiento "
            "con más publicaciones."
        ),
        [
            "Área",
            "Total",
        ],
        [
            [
                item.get(
                    "label"
                ),
                item.get(
                    "total",
                    0,
                ),
            ]
            for item in (
                areas.get(
                    "items",
                    [],
                )
                or []
            )
        ],
    )

    return workbook


# ============================================================
# API — REPORTE EXCEL
# ============================================================


class DashboardReporteExcelView(
    APIView
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        payload = (
            _build_dashboard_payload(
                request.query_params
            )
        )

        workbook = (
            _build_report_workbook(
                payload
            )
        )

        output = BytesIO()

        workbook.save(
            output
        )

        file_bytes = (
            output.getvalue()
        )

        filename = (
            _report_filename()
        )

        response = HttpResponse(
            file_bytes,
            content_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="{filename}"'
        )

        response[
            "Content-Length"
        ] = str(
            len(file_bytes)
        )

        response[
            "Cache-Control"
        ] = "private, no-store"

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        return response