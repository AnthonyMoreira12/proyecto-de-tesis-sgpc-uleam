# core/dashboard.py
# ============================================================
# SGPC ULEAM — Dashboard institucional + reporte Excel
# ============================================================

from calendar import monthrange
from datetime import date
from io import BytesIO
import unicodedata

from django.apps import apps
from django.db.models import Count, F
from django.db.models.functions import (
    ExtractMonth,
    ExtractYear,
)
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date

from openpyxl import Workbook
from openpyxl.chart import BarChart, DoughnutChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import DataPoint
from openpyxl.formatting.rule import DataBarRule
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from rest_framework.exceptions import ValidationError as DRFValidationError
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
    )

    if not normalized:
        return None

    return next(
        (
            item
            for item in CANONICAL_TYPES
            if item["codigo"] == normalized
        ),
        None,
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


def _safe_period_date(
    value,
    *,
    field_name,
    end_of_month=False,
):
    """
    Convierte valores de periodo a una fecha válida.

    Formatos aceptados:

        YYYY-MM-DD
        YYYY-MM

    Cuando recibe YYYY-MM:

        fecha_desde -> primer día del mes
        fecha_hasta -> último día del mes
    """

    raw = str(
        value or ""
    ).strip()

    if not raw:
        return None

    parsed = parse_date(raw)

    if parsed:
        return parsed

    parts = raw.split("-")

    if len(parts) == 2:
        try:
            year = int(parts[0])
            month = int(parts[1])

            if month < 1 or month > 12:
                raise ValueError

            day = (
                monthrange(
                    year,
                    month,
                )[1]
                if end_of_month
                else 1
            )

            return date(
                year,
                month,
                day,
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            pass

    raise DRFValidationError(
        {
            field_name: (
                "Utilice el formato YYYY-MM "
                "o YYYY-MM-DD."
            )
        }
    )


def _resolve_period_filters(
    params,
):
    """
    Resuelve los filtros temporales del dashboard.

    Los filtros por fecha tienen prioridad sobre los filtros
    históricos por año. Esto conserva compatibilidad con el
    frontend anterior mientras se migra a selectores mensuales.
    """

    raw_fecha_desde = (
        params.get("fecha_desde")
        or params.get("mes_desde")
    )

    raw_fecha_hasta = (
        params.get("fecha_hasta")
        or params.get("mes_hasta")
    )

    fecha_desde = _safe_period_date(
        raw_fecha_desde,
        field_name="fecha_desde",
        end_of_month=False,
    )

    fecha_hasta = _safe_period_date(
        raw_fecha_hasta,
        field_name="fecha_hasta",
        end_of_month=True,
    )

    if (
        fecha_desde
        and fecha_hasta
        and fecha_desde > fecha_hasta
    ):
        fecha_desde = _safe_period_date(
            raw_fecha_hasta,
            field_name="fecha_desde",
            end_of_month=False,
        )

        fecha_hasta = _safe_period_date(
            raw_fecha_desde,
            field_name="fecha_hasta",
            end_of_month=True,
        )

    if fecha_desde or fecha_hasta:
        return {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "anio_desde": None,
            "anio_hasta": None,
            "modo": "fecha",
        }

    anio_desde = _safe_int(
        params.get("anio_desde")
    )

    anio_hasta = _safe_int(
        params.get("anio_hasta")
    )

    (
        anio_desde,
        anio_hasta,
    ) = _normalize_year_range(
        anio_desde,
        anio_hasta,
    )

    return {
        "fecha_desde": None,
        "fecha_hasta": None,
        "anio_desde": anio_desde,
        "anio_hasta": anio_hasta,
        "modo": (
            "anio"
            if anio_desde or anio_hasta
            else None
        ),
    }



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

    period = _resolve_period_filters(
        params
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
    # Periodo exacto o mensual
    # --------------------------------------------------------

    if period["fecha_desde"]:
        queryset = queryset.filter(
            fecha_publicacion__gte=(
                period["fecha_desde"]
            )
        )

    if period["fecha_hasta"]:
        queryset = queryset.filter(
            fecha_publicacion__lte=(
                period["fecha_hasta"]
            )
        )

    # --------------------------------------------------------
    # Compatibilidad con filtros históricos por año
    #
    # Solo se aplican cuando no se enviaron fecha_desde ni
    # fecha_hasta.
    # --------------------------------------------------------

    if period["anio_desde"]:
        queryset = queryset.filter(
            anio_publicacion__gte=(
                period["anio_desde"]
            )
        )

    if period["anio_hasta"]:
        queryset = queryset.filter(
            anio_publicacion__lte=(
                period["anio_hasta"]
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

    period = _resolve_period_filters(
        params
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

    fecha_desde = period[
        "fecha_desde"
    ]

    fecha_hasta = period[
        "fecha_hasta"
    ]

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

        "fecha_desde": (
            fecha_desde.isoformat()
            if fecha_desde
            else None
        ),

        "fecha_hasta": (
            fecha_hasta.isoformat()
            if fecha_hasta
            else None
        ),

        "anio_desde": (
            period["anio_desde"]
        ),

        "anio_hasta": (
            period["anio_hasta"]
        ),

        "periodo_modo": (
            period["modo"]
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
    # Queryset general con filtros institucionales/periodo
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

REPORT_COLORS = {
    "navy": "0F172A",
    "primary": "2563EB",
    "primary_dark": "1D4ED8",
    "primary_soft": "EFF6FF",
    "green": "15803D",
    "purple": "7C3AED",
    "orange": "C2410C",
    "teal": "0F766E",
    "text": "172033",
    "muted": "64748B",
    "surface": "FFFFFF",
    "background": "F8FAFC",
    "border": "D8E1EC",
    "border_strong": "CBD5E1",
}

REPORT_TYPE_COLORS = {
    "AAI": "3366CC",
    "AR": "3F7F5A",
    "PON": "7251B5",
    "CAP": "B85C2E",
    "LIB": "1F7A73",
}

REPORT_KPI_COLORS = (
    "2563EB",
    "0F766E",
    "7C3AED",
    "C2410C",
    "0F766E",
    "2563EB",
)


def _safe_excel_value(value):
    return "" if value is None else value


def _report_generated_at():
    return timezone.localtime().strftime("%d/%m/%Y %H:%M")


def _report_filename():
    stamp = timezone.localtime().strftime("%Y-%m-%d_%H-%M-%S")
    return f"reporte-dashboard-sgpc-uleam-{stamp}.xlsx"


def _solid_fill(color):
    return PatternFill("solid", fgColor=color)


def _thin_border(color=None):
    side = Side(style="thin", color=color or REPORT_COLORS["border"])
    return Border(left=side, right=side, top=side, bottom=side)


def _safe_table_name(value):
    normalized = (
        unicodedata.normalize("NFKD", str(value or "Datos"))
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    token = "".join(ch for ch in normalized if ch.isalnum()) or "Datos"
    if token[0].isdigit():
        token = f"T{token}"
    return f"Tbl{token}"[:240]


def _set_range_fill(ws, cell_range, color):
    fill = _solid_fill(color)
    for row in ws[cell_range]:
        for cell in row:
            cell.fill = fill


def _set_range_border(ws, cell_range, color=None):
    border = _thin_border(color)
    for row in ws[cell_range]:
        for cell in row:
            cell.border = border


def _merge_block(
    ws,
    cell_range,
    value,
    *,
    fill=None,
    font=None,
    alignment=None,
    border=None,
):
    if fill:
        _set_range_fill(ws, cell_range, fill)
    if border:
        _set_range_border(ws, cell_range, border)

    ws.merge_cells(cell_range)
    anchor = ws[cell_range.split(":")[0]]
    anchor.value = value

    if font:
        anchor.font = font
    if alignment:
        anchor.alignment = alignment

    return anchor


def _format_periodo(filtros):
    fecha_desde_raw = filtros.get(
        "fecha_desde"
    )

    fecha_hasta_raw = filtros.get(
        "fecha_hasta"
    )

    fecha_desde = (
        parse_date(fecha_desde_raw)
        if fecha_desde_raw
        else None
    )

    fecha_hasta = (
        parse_date(fecha_hasta_raw)
        if fecha_hasta_raw
        else None
    )

    if fecha_desde or fecha_hasta:
        def format_date(value):
            return value.strftime(
                "%d/%m/%Y"
            )

        if fecha_desde and fecha_hasta:
            if fecha_desde == fecha_hasta:
                return format_date(
                    fecha_desde
                )

            return (
                f"{format_date(fecha_desde)} "
                f"– {format_date(fecha_hasta)}"
            )

        if fecha_desde:
            return (
                "Desde "
                f"{format_date(fecha_desde)}"
            )

        return (
            "Hasta "
            f"{format_date(fecha_hasta)}"
        )

    desde = filtros.get(
        "anio_desde"
    )

    hasta = filtros.get(
        "anio_hasta"
    )

    if desde and hasta:
        return (
            str(desde)
            if desde == hasta
            else f"{desde} – {hasta}"
        )

    if desde:
        return f"Desde {desde}"

    if hasta:
        return f"Hasta {hasta}"

    return "Todos los periodos"



def _set_sheet_print_settings(ws, *, print_area=None):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ws.page_margins.left = 0.25
    ws.page_margins.right = 0.25
    ws.page_margins.top = 0.45
    ws.page_margins.bottom = 0.45
    ws.page_margins.header = 0.2
    ws.page_margins.footer = 0.2

    ws.oddHeader.center.text = "SGPC ULEAM"
    ws.oddHeader.center.size = 9
    ws.oddHeader.center.font = "Calibri,Bold"
    ws.oddFooter.left.text = "Producción científica"
    ws.oddFooter.right.text = "Página &[Page] de &N"

    if print_area:
        ws.print_area = print_area


# ============================================================
# ESTILO DE HOJAS DE DATOS
# ============================================================


def _style_report_sheet(ws, headers, *, table_name, tab_color=None):
    max_row = ws.max_row or 1
    max_col = ws.max_column or 1
    last_col = get_column_letter(max_col)

    title_fill = _solid_fill(REPORT_COLORS["navy"])
    subtitle_fill = _solid_fill(REPORT_COLORS["primary"])
    meta_fill = _solid_fill(REPORT_COLORS["primary_soft"])
    header_fill = _solid_fill(REPORT_COLORS["primary_dark"])
    body_border = _thin_border()

    if max_col > 1:
        for row_number in (1, 2, 3):
            ws.merge_cells(
                start_row=row_number,
                start_column=1,
                end_row=row_number,
                end_column=max_col,
            )

    for cell in ws[1]:
        cell.fill = title_fill
    for cell in ws[2]:
        cell.fill = subtitle_fill
    for cell in ws[3]:
        cell.fill = meta_fill

    ws["A1"].font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws["A2"].font = Font(name="Calibri", size=10.5, bold=True, color="FFFFFF")
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center")
    ws["A3"].font = Font(
        name="Calibri", size=9, italic=True, color=REPORT_COLORS["muted"]
    )
    ws["A3"].alignment = Alignment(horizontal="left", vertical="center")

    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 22
    ws.row_dimensions[3].height = 19
    ws.row_dimensions[4].height = 8
    ws.row_dimensions[5].height = 25

    header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    body_font = Font(name="Calibri", size=10, color=REPORT_COLORS["text"])

    for cell in ws[5]:
        cell.fill = header_fill
        cell.font = header_font
        cell.border = body_border
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row in ws.iter_rows(min_row=6, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            cell.font = body_font
            cell.border = body_border
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    if max_row >= 6:
        table = Table(displayName=table_name, ref=f"A5:{last_col}{max_row}")
        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        ws.add_table(table)
    else:
        ws.auto_filter.ref = f"A5:{last_col}5"

    numeric_headers = {"total", "total publicaciones", "total participaciones", "valor"}

    for column_index, header in enumerate(headers, start=1):
        normalized = str(header or "").strip().lower()
        letter = get_column_letter(column_index)

        if max_row < 6:
            continue

        cell_range = f"{letter}6:{letter}{max_row}"
        cells = [row[0] for row in ws[cell_range]]

        if normalized in numeric_headers:
            for cell in cells:
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right", vertical="center")

            ws.conditional_formatting.add(
                cell_range,
                DataBarRule(
                    start_type="num",
                    start_value=0,
                    end_type="max",
                    color=REPORT_COLORS["primary"],
                    showValue=True,
                ),
            )

        elif normalized == "porcentaje":
            for cell in cells:
                cell.number_format = '0.0"%"'
                cell.alignment = Alignment(horizontal="right", vertical="center")

        elif normalized in {"año", "código", "categoría"}:
            for cell in cells:
                cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.freeze_panes = "A6"

    for column_index in range(1, max_col + 1):
        header_value = headers[column_index - 1] if column_index - 1 < len(headers) else ""
        max_length = len(str(header_value or ""))

        for row_index in range(6, max_row + 1):
            value = ws.cell(row=row_index, column=column_index).value
            max_length = max(max_length, len(str(value or "")))

        ws.column_dimensions[get_column_letter(column_index)].width = min(
            max(max_length + 4, 12),
            42,
        )

    for row_index in range(6, max_row + 1):
        ws.row_dimensions[row_index].height = 20

    if tab_color:
        ws.sheet_properties.tabColor = tab_color

    ws.print_title_rows = "1:5"
    _set_sheet_print_settings(ws, print_area=f"A1:{last_col}{max_row}")


# ============================================================
# CREACIÓN DE HOJAS
# ============================================================


def _create_sheet(workbook, title, subtitle, headers, rows, *, tab_color=None):
    ws = workbook.create_sheet(title=title[:31])
    ws.append([title])
    ws.append([subtitle])
    ws.append([f"SGPC ULEAM · Generado el {_report_generated_at()}"])
    ws.append([])
    ws.append(headers)

    for row in rows:
        ws.append([_safe_excel_value(value) for value in row])

    _style_report_sheet(
        ws,
        headers,
        table_name=_safe_table_name(title),
        tab_color=tab_color,
    )
    return ws


def _build_tipo_anual_rows(publicaciones_por_tipo_anual):
    rows = []
    categorias = publicaciones_por_tipo_anual.get("categorias", []) or []

    for serie in publicaciones_por_tipo_anual.get("series", []) or []:
        data = serie.get("data", []) or []
        for index, anio in enumerate(categorias):
            rows.append(
                [
                    anio,
                    serie.get("codigo"),
                    serie.get("label"),
                    data[index] if index < len(data) else 0,
                ]
            )

    return rows


# ============================================================
# DATOS OCULTOS PARA GRÁFICOS
# ============================================================


def _build_chart_data_sheet(workbook, dashboards):
    ws = workbook.create_sheet("_DatosGraficos")

    publicaciones_por_tipo = dashboards.get("publicaciones_por_tipo", {}) or {}
    publicaciones_por_anio = dashboards.get("publicaciones_por_anio", []) or []
    top_facultades = dashboards.get("top_facultades", {}) or {}
    top_autores = (
        dashboards.get("top_autores_principales")
        or dashboards.get("top_autores")
        or {}
    )

    ws.append(["Tipo", "Total", "Código", "", "Año", "Total", "", "Facultad", "Total", "", "Autor", "Total"])

    for row_index, item in enumerate(publicaciones_por_tipo.get("items", []) or [], start=2):
        ws.cell(row=row_index, column=1, value=item.get("tipo_nombre"))
        ws.cell(row=row_index, column=2, value=item.get("total", 0))
        ws.cell(row=row_index, column=3, value=item.get("tipo_codigo"))

    for row_index, item in enumerate(publicaciones_por_anio, start=2):
        ws.cell(row=row_index, column=5, value=item.get("label"))
        ws.cell(row=row_index, column=6, value=item.get("value", 0))

    for row_index, item in enumerate(top_facultades.get("items", []) or [], start=2):
        ws.cell(row=row_index, column=8, value=item.get("facultad"))
        ws.cell(row=row_index, column=9, value=item.get("total", 0))

    for row_index, item in enumerate(top_autores.get("items", []) or [], start=2):
        ws.cell(row=row_index, column=11, value=item.get("autor") or item.get("label"))
        ws.cell(
            row=row_index,
            column=12,
            value=item.get("total_publicaciones", item.get("total", 0)),
        )

    ws.sheet_state = "hidden"
    return ws


# ============================================================
# RESUMEN EJECUTIVO
# ============================================================


def _write_filter_card(ws, label, value, *, label_range, value_range):
    _merge_block(
        ws,
        label_range,
        label,
        fill=REPORT_COLORS["primary_soft"],
        font=Font(name="Calibri", size=8.5, bold=True, color=REPORT_COLORS["primary_dark"]),
        alignment=Alignment(horizontal="left", vertical="center"),
        border=REPORT_COLORS["border"],
    )
    _merge_block(
        ws,
        value_range,
        _safe_excel_value(value),
        fill=REPORT_COLORS["surface"],
        font=Font(name="Calibri", size=10.5, bold=True, color=REPORT_COLORS["text"]),
        alignment=Alignment(horizontal="left", vertical="center", wrap_text=True),
        border=REPORT_COLORS["border"],
    )


def _write_kpi_card(ws, label, value, *, label_range, value_range, accent):
    _merge_block(
        ws,
        label_range,
        label.upper(),
        fill=accent,
        font=Font(name="Calibri", size=8.5, bold=True, color="FFFFFF"),
        alignment=Alignment(horizontal="left", vertical="center"),
        border=accent,
    )
    value_cell = _merge_block(
        ws,
        value_range,
        int(value or 0),
        fill=REPORT_COLORS["surface"],
        font=Font(name="Calibri", size=21, bold=True, color=accent),
        alignment=Alignment(horizontal="left", vertical="center"),
        border=REPORT_COLORS["border_strong"],
    )
    value_cell.number_format = "#,##0"


def _build_summary_sheet(workbook, summary, filtros):
    ws = workbook.create_sheet("Resumen")
    ws.sheet_properties.tabColor = REPORT_COLORS["primary"]
    ws.sheet_view.showGridLines = False

    for column in range(1, 13):
        ws.column_dimensions[get_column_letter(column)].width = 12.5

    _merge_block(
        ws,
        "A1:L2",
        "SGPC ULEAM",
        fill=REPORT_COLORS["navy"],
        font=Font(name="Calibri", size=22, bold=True, color="FFFFFF"),
        alignment=Alignment(horizontal="left", vertical="center"),
    )
    _merge_block(
        ws,
        "A3:L3",
        "REPORTE DEL PANEL ANALÍTICO INSTITUCIONAL",
        fill=REPORT_COLORS["primary"],
        font=Font(name="Calibri", size=12, bold=True, color="FFFFFF"),
        alignment=Alignment(horizontal="left", vertical="center"),
    )
    _merge_block(
        ws,
        "A4:L4",
        (
            "Producción científica · Universidad Laica Eloy Alfaro de Manabí · "
            f"Generado el {_report_generated_at()}"
        ),
        fill=REPORT_COLORS["background"],
        font=Font(name="Calibri", size=9.5, italic=True, color=REPORT_COLORS["muted"]),
        alignment=Alignment(horizontal="left", vertical="center"),
    )

    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 28
    ws.row_dimensions[3].height = 24
    ws.row_dimensions[4].height = 21

    _merge_block(
        ws,
        "A6:L6",
        "FILTROS APLICADOS",
        fill=REPORT_COLORS["primary_soft"],
        font=Font(name="Calibri", size=10, bold=True, color=REPORT_COLORS["primary_dark"]),
        alignment=Alignment(horizontal="left", vertical="center"),
        border=REPORT_COLORS["border"],
    )

    _write_filter_card(
        ws,
        "Facultad",
        filtros.get("facultad_nombre") or "Todas",
        label_range="A7:C7",
        value_range="A8:C9",
    )
    _write_filter_card(
        ws,
        "Carrera",
        filtros.get("carrera_nombre") or "Todas",
        label_range="D7:F7",
        value_range="D8:F9",
    )
    _write_filter_card(
        ws,
        "Tipo de publicación",
        filtros.get("tipo_nombre") or "Todos",
        label_range="G7:I7",
        value_range="G8:I9",
    )
    _write_filter_card(
        ws,
        "Periodo",
        _format_periodo(filtros),
        label_range="J7:L7",
        value_range="J8:L9",
    )
    _write_filter_card(
        ws,
        "Año mensual",
        filtros.get("anio") or filtros.get("anio_base_mensual") or "Automático",
        label_range="A10:C10",
        value_range="A11:C12",
    )
    _write_filter_card(
        ws,
        "Top aplicado",
        filtros.get("top") or TOP_DEFAULT,
        label_range="D10:F10",
        value_range="D11:F12",
    )
    _write_filter_card(
        ws,
        "Cobertura",
        "Datos según filtros activos",
        label_range="G10:I10",
        value_range="G11:I12",
    )
    _write_filter_card(
        ws,
        "Generado",
        _report_generated_at(),
        label_range="J10:L10",
        value_range="J11:L12",
    )

    _merge_block(
        ws,
        "A14:L14",
        "INDICADORES PRINCIPALES",
        fill=REPORT_COLORS["primary_soft"],
        font=Font(name="Calibri", size=10, bold=True, color=REPORT_COLORS["primary_dark"]),
        alignment=Alignment(horizontal="left", vertical="center"),
        border=REPORT_COLORS["border"],
    )

    kpis = (
        ("Publicaciones", summary.get("total_publicaciones", 0)),
        ("Autores", summary.get("total_autores", 0)),
        ("Facultades", summary.get("total_facultades", 0)),
        ("Carreras", summary.get("total_carreras", 0)),
        ("Proyectos", summary.get("total_proyectos", 0)),
        ("Alto impacto", summary.get("articulos_alto_impacto", 0)),
    )
    card_ranges = (
        ("A15:D15", "A16:D18"),
        ("E15:H15", "E16:H18"),
        ("I15:L15", "I16:L18"),
        ("A20:D20", "A21:D23"),
        ("E20:H20", "E21:H23"),
        ("I20:L20", "I21:L23"),
    )

    for index, (label, value) in enumerate(kpis):
        _write_kpi_card(
            ws,
            label,
            value,
            label_range=card_ranges[index][0],
            value_range=card_ranges[index][1],
            accent=REPORT_KPI_COLORS[index],
        )

    _merge_block(
        ws,
        "A25:L25",
        "VISUALIZACIÓN EJECUTIVA",
        fill=REPORT_COLORS["primary_soft"],
        font=Font(name="Calibri", size=10, bold=True, color=REPORT_COLORS["primary_dark"]),
        alignment=Alignment(horizontal="left", vertical="center"),
        border=REPORT_COLORS["border"],
    )

    for chart_range in ("A26:F42", "G26:L42", "A44:F60", "G44:L60"):
        _set_range_fill(ws, chart_range, REPORT_COLORS["surface"])
        _set_range_border(ws, chart_range, REPORT_COLORS["border"])

    _merge_block(
        ws,
        "A62:L63",
        (
            "Artículos regionales: "
            f"{int(summary.get('articulos_regionales', 0) or 0):,} · "
            "Los gráficos y tablas reflejan los filtros activos del dashboard."
        ),
        fill=REPORT_COLORS["background"],
        font=Font(name="Calibri", size=9, color=REPORT_COLORS["muted"]),
        alignment=Alignment(horizontal="left", vertical="center", wrap_text=True),
        border=REPORT_COLORS["border"],
    )

    ws.freeze_panes = "A6"
    _set_sheet_print_settings(ws, print_area="A1:L63")
    return ws


def _add_summary_charts(summary_ws, data_ws, dashboards):
    publicaciones_por_tipo = dashboards.get("publicaciones_por_tipo", {}) or {}
    publicaciones_por_anio = dashboards.get("publicaciones_por_anio", []) or []
    top_facultades = dashboards.get("top_facultades", {}) or {}
    top_autores = (
        dashboards.get("top_autores_principales")
        or dashboards.get("top_autores")
        or {}
    )

    type_items = publicaciones_por_tipo.get("items", []) or []
    if type_items:
        chart = DoughnutChart()
        chart.add_data(
            Reference(data_ws, min_col=2, min_row=1, max_row=len(type_items) + 1),
            titles_from_data=True,
        )
        chart.set_categories(
            Reference(data_ws, min_col=1, min_row=2, max_row=len(type_items) + 1)
        )
        chart.title = "Publicaciones por tipo"
        chart.holeSize = 62
        chart.height = 7.2
        chart.width = 10
        chart.legend.position = "r"
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showPercent = True
        chart.dataLabels.showLeaderLines = True

        if chart.series:
            points = []
            for index, item in enumerate(type_items):
                point = DataPoint(idx=index)
                color = REPORT_TYPE_COLORS.get(
                    item.get("tipo_codigo"),
                    REPORT_COLORS["muted"],
                )
                point.graphicalProperties.solidFill = color
                point.graphicalProperties.line.solidFill = color
                points.append(point)
            chart.series[0].data_points = points

        summary_ws.add_chart(chart, "A26")

    if publicaciones_por_anio:
        chart = BarChart()
        chart.type = "col"
        chart.grouping = "clustered"
        chart.add_data(
            Reference(data_ws, min_col=6, min_row=1, max_row=len(publicaciones_por_anio) + 1),
            titles_from_data=True,
        )
        chart.set_categories(
            Reference(data_ws, min_col=5, min_row=2, max_row=len(publicaciones_por_anio) + 1)
        )
        chart.title = "Producción por año"
        chart.y_axis.title = "Publicaciones"
        chart.height = 7.2
        chart.width = 10
        chart.legend = None
        chart.y_axis.majorGridlines = None
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True

        if chart.series:
            chart.series[0].graphicalProperties.solidFill = REPORT_COLORS["primary"]
            chart.series[0].graphicalProperties.line.solidFill = REPORT_COLORS["primary"]

        summary_ws.add_chart(chart, "G26")

    faculty_items = top_facultades.get("items", []) or []
    if faculty_items:
        chart = BarChart()
        chart.type = "bar"
        chart.grouping = "clustered"
        chart.add_data(
            Reference(data_ws, min_col=9, min_row=1, max_row=len(faculty_items) + 1),
            titles_from_data=True,
        )
        chart.set_categories(
            Reference(data_ws, min_col=8, min_row=2, max_row=len(faculty_items) + 1)
        )
        chart.title = "Top facultades"
        chart.height = 7
        chart.width = 10
        chart.legend = None
        chart.x_axis.majorGridlines = None
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True

        if chart.series:
            chart.series[0].graphicalProperties.solidFill = REPORT_COLORS["teal"]
            chart.series[0].graphicalProperties.line.solidFill = REPORT_COLORS["teal"]

        summary_ws.add_chart(chart, "A44")

    author_items = top_autores.get("items", []) or []
    if author_items:
        chart = BarChart()
        chart.type = "bar"
        chart.grouping = "clustered"
        chart.add_data(
            Reference(data_ws, min_col=12, min_row=1, max_row=len(author_items) + 1),
            titles_from_data=True,
        )
        chart.set_categories(
            Reference(data_ws, min_col=11, min_row=2, max_row=len(author_items) + 1)
        )
        chart.title = "Top autores principales"
        chart.height = 7
        chart.width = 10
        chart.legend = None
        chart.x_axis.majorGridlines = None
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True

        if chart.series:
            chart.series[0].graphicalProperties.solidFill = REPORT_COLORS["purple"]
            chart.series[0].graphicalProperties.line.solidFill = REPORT_COLORS["purple"]

        summary_ws.add_chart(chart, "G44")


# ============================================================
# WORKBOOK
# ============================================================


def _build_report_workbook(payload):
    summary = payload.get("summary", {}) or {}
    dashboards = payload.get("dashboards", {}) or {}
    filtros = payload.get("filtros_aplicados", {}) or {}

    workbook = Workbook()
    workbook.remove(workbook.active)

    workbook.properties.title = "Reporte dashboard SGPC ULEAM"
    workbook.properties.subject = "Indicadores institucionales de producción científica"
    workbook.properties.creator = "SGPC ULEAM"
    workbook.properties.description = "Reporte analítico institucional generado por el SGPC ULEAM."
    workbook.properties.keywords = "SGPC ULEAM, producción científica, dashboard, reporte"

    publicaciones_por_tipo = dashboards.get("publicaciones_por_tipo", {}) or {}
    publicaciones_por_anio = dashboards.get("publicaciones_por_anio", []) or []
    publicaciones_por_mes = dashboards.get("publicaciones_por_mes", {}) or {}
    publicaciones_por_tipo_anual = dashboards.get("publicaciones_por_tipo_anual", {}) or {}
    top_facultades = dashboards.get("top_facultades", {}) or {}
    top_carreras = dashboards.get("top_carreras", {}) or {}
    top_autores_principales = (
        dashboards.get("top_autores_principales")
        or dashboards.get("top_autores")
        or {}
    )
    top_coautores = dashboards.get("top_coautores", {}) or {}
    journals = dashboards.get("journals", {}) or {}
    projects = dashboards.get("projects", {}) or {}
    areas = dashboards.get("areas", {}) or {}

    resumen_ws = _build_summary_sheet(workbook, summary, filtros)

    _create_sheet(
        workbook,
        "Publicaciones por tipo",
        "Distribución de publicaciones por tipo.",
        ["Tipo", "Código", "Categoría", "Total", "Porcentaje"],
        [
            [
                item.get("tipo_nombre"),
                item.get("tipo_codigo"),
                item.get("categoria"),
                item.get("total", 0),
                item.get("porcentaje", 0),
            ]
            for item in publicaciones_por_tipo.get("items", []) or []
        ],
        tab_color=REPORT_COLORS["primary"],
    )

    _create_sheet(
        workbook,
        "Publicaciones por año",
        "Serie histórica de publicaciones registradas.",
        ["Año", "Total"],
        [[item.get("label"), item.get("value", 0)] for item in publicaciones_por_anio],
        tab_color=REPORT_COLORS["green"],
    )

    _create_sheet(
        workbook,
        "Publicaciones por mes",
        f"Detalle mensual del año {publicaciones_por_mes.get('anio_base') or 'sin año base'}.",
        ["Mes", "Total"],
        [
            [item.get("label"), item.get("value", 0)]
            for item in publicaciones_por_mes.get("items", []) or []
        ],
        tab_color=REPORT_COLORS["teal"],
    )

    _create_sheet(
        workbook,
        "Tipo por año",
        "Comparativa anual por tipo de publicación.",
        ["Año", "Código", "Tipo", "Total"],
        _build_tipo_anual_rows(publicaciones_por_tipo_anual),
        tab_color=REPORT_COLORS["purple"],
    )

    _create_sheet(
        workbook,
        "Top facultades",
        "Facultades con más publicaciones.",
        ["Facultad", "Total"],
        [[item.get("facultad"), item.get("total", 0)] for item in top_facultades.get("items", []) or []],
        tab_color=REPORT_COLORS["teal"],
    )

    _create_sheet(
        workbook,
        "Top carreras",
        "Carreras con más publicaciones.",
        ["Carrera", "Total"],
        [[item.get("carrera"), item.get("total", 0)] for item in top_carreras.get("items", []) or []],
        tab_color=REPORT_COLORS["orange"],
    )

    _create_sheet(
        workbook,
        "Autores principales",
        "Autores principales con más publicaciones lideradas.",
        ["Autor principal", "Total publicaciones"],
        [
            [
                item.get("autor") or item.get("label"),
                item.get("total_publicaciones", item.get("total", 0)),
            ]
            for item in top_autores_principales.get("items", []) or []
        ],
        tab_color=REPORT_COLORS["purple"],
    )

    _create_sheet(
        workbook,
        "Coautores",
        "Coautores con mayor participación colaborativa.",
        ["Coautor", "Total participaciones"],
        [
            [
                item.get("autor") or item.get("label"),
                item.get("total_publicaciones", item.get("total", 0)),
            ]
            for item in top_coautores.get("items", []) or []
        ],
        tab_color=REPORT_COLORS["purple"],
    )

    _create_sheet(
        workbook,
        "Revistas",
        "Revistas con más artículos registrados.",
        ["Revista", "Total"],
        [[item.get("label"), item.get("total", 0)] for item in journals.get("items", []) or []],
        tab_color=REPORT_COLORS["primary"],
    )

    _create_sheet(
        workbook,
        "Proyectos",
        "Proyectos con más publicaciones asociadas.",
        ["Proyecto", "Total"],
        [[item.get("label"), item.get("total", 0)] for item in projects.get("items", []) or []],
        tab_color=REPORT_COLORS["green"],
    )

    _create_sheet(
        workbook,
        "Áreas",
        "Áreas del conocimiento con más publicaciones.",
        ["Área", "Total"],
        [[item.get("label"), item.get("total", 0)] for item in areas.get("items", []) or []],
        tab_color=REPORT_COLORS["orange"],
    )

    chart_data_ws = _build_chart_data_sheet(workbook, dashboards)
    _add_summary_charts(resumen_ws, chart_data_ws, dashboards)

    workbook.active = 0
    return workbook


# ============================================================
# API — REPORTE EXCEL
# ============================================================


class DashboardReporteExcelView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        payload = _build_dashboard_payload(request.query_params)
        workbook = _build_report_workbook(payload)

        output = BytesIO()
        workbook.save(output)
        file_bytes = output.getvalue()
        filename = _report_filename()

        response = HttpResponse(
            file_bytes,
            content_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"] = str(len(file_bytes))
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response