"""
Selectores del módulo de proyectos.

Este módulo centraliza:

- Queryset base de proyectos.
- Visibilidad según el usuario.
- Búsqueda por texto.
- Filtros por año y estado.
- Cálculo de años disponibles.
- Precarga optimizada del equipo investigador.

Los selectores únicamente contienen operaciones de lectura.
"""

import unicodedata

from django.db.models import (
    Case,
    IntegerField,
    Prefetch,
    Q,
    Value,
    When,
)
from django.db.models.functions import Concat
from django.utils import timezone

from core.models import (
    Proyecto,
    ProyectoAutor,
)
from core.proyectos.services.proyectos_proyecto_services import (
    user_is_project_admin,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

ESTADOS_ACTIVOS = {
    "nuevo",
    "arrastre",
}

ESTADOS_CERRADOS = {
    "cierre",
}

ESTADO_VALUES = {
    "nuevo",
    "arrastre",
    "cierre",
}

ESTADO_ALIASES = {
    "activo": "activo",
    "activos": "activo",
    "vigente": "activo",
    "vigentes": "activo",
    "abierto": "activo",
    "abiertos": "activo",

    "cerrado": "cerrado",
    "cerrados": "cerrado",
    "finalizado": "cerrado",
    "finalizados": "cerrado",

    "nuevo": "nuevo",
    "arrastre": "arrastre",
    "cierre": "cierre",
}

MAX_PROJECT_SEARCH_QUERY_LENGTH = 200

MIN_PROJECT_YEAR = 1900
MAX_PROJECT_FUTURE_YEARS = 50
MAX_EXPANDED_YEAR_SPAN = 100


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _normalize_text(
    value,
    *,
    max_length=MAX_PROJECT_SEARCH_QUERY_LENGTH,
):
    """
    Normaliza Unicode y elimina espacios repetidos.
    """
    normalized = unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )

    normalized = " ".join(
        normalized.split()
    )

    if max_length is not None:
        normalized = normalized[
            :max_length
        ]

    return normalized


def _normalize_state(value):
    """
    Normaliza un estado o alias utilizado en los filtros.
    """
    normalized = _normalize_text(
        value,
        max_length=30,
    ).lower()

    if not normalized:
        return ""

    return ESTADO_ALIASES.get(
        normalized,
        "",
    )


def _parse_year(value):
    """
    Convierte un año en entero y valida un rango razonable.
    """
    if value in (
        None,
        "",
    ):
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    try:
        year = int(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None

    maximum_year = (
        timezone.localdate().year
        + MAX_PROJECT_FUTURE_YEARS
    )

    if not (
        MIN_PROJECT_YEAR
        <= year
        <= maximum_year
    ):
        return None

    return year


# ============================================================
# PERMISOS
# ============================================================

def user_is_project_admin_like(user):
    """
    Alias compatible con importaciones anteriores.

    La regla real se encuentra centralizada en
    user_is_project_admin() para evitar diferencias entre:

    - Visibilidad de proyectos.
    - Permisos del ViewSet.
    - Operaciones de escritura.
    """
    return user_is_project_admin(
        user
    )


# Alias histórico mantenido para no romper imports existentes.
_user_is_project_admin_like = (
    user_is_project_admin_like
)


# ============================================================
# QUERYSET BASE
# ============================================================

def proyectos_base_queryset():
    """
    Construye el queryset base optimizado de proyectos.

    Precarga las participaciones en el orden utilizado para
    representar el equipo investigador.
    """
    participations_queryset = (
        ProyectoAutor.objects
        .select_related(
            "autor",
            "autor__usuario",
        )
        .order_by(
            "orden",
            "id",
        )
    )

    return (
        Proyecto.objects
        .select_related(
            "carrera",
            "carrera__facultad",
            "creado_por",
        )
        .prefetch_related(
            Prefetch(
                "participaciones",
                queryset=(
                    participations_queryset
                ),
            )
        )
        .annotate(
            _project_year_order=Case(
                When(
                    anio_inicio__isnull=True,
                    then=Value(0),
                ),
                default="anio_inicio",
                output_field=IntegerField(),
            )
        )
        .order_by(
            "-_project_year_order",
            "nombre",
            "id",
        )
    )


# ============================================================
# VISIBILIDAD
# ============================================================

def proyectos_visible_queryset_for_user(user):
    """
    Los administradores pueden consultar todos los proyectos.

    Los usuarios académicos únicamente pueden consultar
    proyectos en estado nuevo o arrastre.
    """
    queryset = proyectos_base_queryset()

    if user_is_project_admin_like(
        user
    ):
        return queryset

    return queryset.filter(
        estado__in=ESTADOS_ACTIVOS
    )


# ============================================================
# FILTRO DE TEXTO
# ============================================================

def _apply_q_filter(
    queryset,
    query,
    *,
    is_admin=False,
):
    """
    Busca proyectos por información institucional y equipo.

    La consulta se divide en palabras. Cada palabra debe
    coincidir en al menos uno de los campos admitidos, lo que
    permite buscar correctamente nombres completos como:

        Juan Martín Mero Ávila

    Los datos sensibles del equipo —correo e identificación—
    únicamente se utilizan como criterio para administradores.
    El usuario creador no se considera parte del equipo
    investigador.
    """
    normalized_query = _normalize_text(
        query
    )

    if not normalized_query:
        return queryset

    search_terms = [
        term
        for term in normalized_query.split()
        if term
    ]

    queryset = queryset.annotate(
        _participant_full_name=Concat(
            "participaciones__autor__nombres",
            Value(" "),
            "participaciones__autor__apellidos",
        )
    )

    combined_query = Q()

    for term in search_terms:
        term_query = (
            Q(
                nombre__icontains=term
            )
            | Q(
                descripcion__icontains=term
            )
            | Q(
                carrera__nombre__icontains=term
            )
            | Q(
                carrera__facultad__nombre__icontains=term
            )
            | Q(
                participaciones__autor__nombres__icontains=term
            )
            | Q(
                participaciones__autor__apellidos__icontains=term
            )
            | Q(
                _participant_full_name__icontains=term
            )
            | Q(
                participaciones__autor__institucion__icontains=term
            )
        )

        if is_admin:
            term_query |= (
                Q(
                    participaciones__autor__correo__icontains=term
                )
                | Q(
                    participaciones__autor__identificacion__icontains=term
                )
                | Q(
                    participaciones__autor__usuario__email__icontains=term
                )
            )

        combined_query &= term_query

    return (
        queryset
        .filter(
            combined_query
        )
        .annotate(
            _project_search_priority=Case(
                When(
                    nombre__iexact=normalized_query,
                    then=Value(0),
                ),
                When(
                    nombre__istartswith=normalized_query,
                    then=Value(1),
                ),
                When(
                    carrera__nombre__iexact=normalized_query,
                    then=Value(2),
                ),
                When(
                    carrera__facultad__nombre__iexact=normalized_query,
                    then=Value(2),
                ),
                default=Value(3),
                output_field=IntegerField(),
            )
        )
        .distinct()
        .order_by(
            "_project_search_priority",
            "-anio_inicio",
            "nombre",
            "id",
        )
    )


# ============================================================
# FILTRO DE AÑO
# ============================================================

def _apply_anio_filter(
    queryset,
    year,
):
    """
    Devuelve proyectos activos durante el año solicitado.

    Un proyecto pertenece al año cuando:

    - Inició en dicho año.
    - Finalizó en dicho año.
    - El año está dentro de su rango.
    - Sigue activo y no tiene año final registrado.
    """
    normalized_year = _parse_year(
        year
    )

    if normalized_year is None:
        return queryset

    current_year = (
        timezone.localdate().year
    )

    year_query = (
        Q(
            anio_inicio=normalized_year
        )
        | Q(
            anio_fin=normalized_year
        )
        | Q(
            anio_inicio__lte=normalized_year,
            anio_fin__gte=normalized_year,
        )
    )

    if normalized_year <= current_year:
        year_query |= Q(
            anio_inicio__lte=normalized_year,
            anio_fin__isnull=True,
            estado__in=ESTADOS_ACTIVOS,
        )

    return queryset.filter(
        year_query
    )


# ============================================================
# FILTRO DE ESTADO
# ============================================================

def _apply_estado_filter(
    queryset,
    state,
    *,
    is_admin=False,
):
    """
    Aplica el filtro de estado únicamente a administradores.

    Para usuarios académicos, la visibilidad ya está restringida
    previamente a proyectos activos.
    """
    if not is_admin:
        return queryset

    normalized_state = _normalize_state(
        state
    )

    if not normalized_state:
        return queryset

    if normalized_state in ESTADO_VALUES:
        return queryset.filter(
            estado=normalized_state
        )

    if normalized_state == "activo":
        return queryset.filter(
            estado__in=ESTADOS_ACTIVOS
        )

    if normalized_state == "cerrado":
        return queryset.filter(
            estado__in=ESTADOS_CERRADOS
        )

    return queryset


# ============================================================
# APLICACIÓN CONJUNTA DE FILTROS
# ============================================================

def filter_proyectos_queryset(
    queryset,
    *,
    q="",
    anio="",
    estado="",
    is_admin=False,
):
    """
    Aplica los filtros disponibles al queryset recibido.
    """
    queryset = _apply_q_filter(
        queryset,
        q,
        is_admin=is_admin,
    )

    queryset = _apply_anio_filter(
        queryset,
        anio,
    )

    queryset = _apply_estado_filter(
        queryset,
        estado,
        is_admin=is_admin,
    )

    return queryset


def get_filtered_proyectos_queryset_for_user(
    user,
    *,
    q="",
    anio="",
    estado="",
):
    """
    Construye el queryset visible y aplica los filtros.
    """
    is_admin = user_is_project_admin_like(
        user
    )

    queryset = (
        proyectos_visible_queryset_for_user(
            user
        )
    )

    return filter_proyectos_queryset(
        queryset,
        q=q,
        anio=anio,
        estado=estado,
        is_admin=is_admin,
    )


# ============================================================
# AÑOS DISPONIBLES
# ============================================================

def _add_year_range(
    years,
    start,
    end,
):
    """
    Agrega un rango de años al conjunto recibido.

    Corrige rangos invertidos sin perder ninguno de sus extremos.
    """
    normalized_start = _parse_year(
        start
    )

    normalized_end = _parse_year(
        end
    )

    if (
        normalized_start is None
        and normalized_end is None
    ):
        return

    if normalized_start is None:
        years.add(
            normalized_end
        )
        return

    if normalized_end is None:
        years.add(
            normalized_start
        )
        return

    range_start, range_end = sorted(
        (
            normalized_start,
            normalized_end,
        )
    )

    if (
        range_end - range_start
        > MAX_EXPANDED_YEAR_SPAN
    ):
        years.add(
            range_start
        )
        years.add(
            range_end
        )
        return

    years.update(
        range(
            range_start,
            range_end + 1,
        )
    )


def _expand_years_from_queryset(
    queryset,
):
    """
    Calcula todos los años representados por los proyectos.
    """
    years = set()

    current_year = (
        timezone.localdate().year
    )

    project_ranges = (
        queryset
        .order_by()
        .values_list(
            "anio_inicio",
            "anio_fin",
            "estado",
        )
        .distinct()
    )

    for (
        start_year,
        end_year,
        project_state,
    ) in project_ranges:
        normalized_state = _normalize_state(
            project_state
        )

        if (
            start_year is None
            and end_year is None
        ):
            continue

        if (
            start_year is not None
            and end_year is None
        ):
            if (
                normalized_state
                in ESTADOS_ACTIVOS
                and start_year <= current_year
            ):
                _add_year_range(
                    years,
                    start_year,
                    current_year,
                )

            else:
                normalized_start = _parse_year(
                    start_year
                )

                if normalized_start is not None:
                    years.add(
                        normalized_start
                    )

            continue

        _add_year_range(
            years,
            start_year,
            end_year,
        )

    return sorted(
        years,
        reverse=True,
    )


def get_proyectos_available_years_for_user(
    user,
    *,
    q="",
    estado="",
):
    """
    Devuelve los años disponibles según la visibilidad del
    usuario y los filtros actuales.
    """
    queryset = (
        get_filtered_proyectos_queryset_for_user(
            user,
            q=q,
            anio="",
            estado=estado,
        )
    )

    return _expand_years_from_queryset(
        queryset
    )


__all__ = [
    "ESTADOS_ACTIVOS",
    "ESTADOS_CERRADOS",
    "ESTADO_VALUES",
    "ESTADO_ALIASES",
    "MAX_PROJECT_SEARCH_QUERY_LENGTH",
    "user_is_project_admin_like",
    "proyectos_base_queryset",
    "proyectos_visible_queryset_for_user",
    "filter_proyectos_queryset",
    "get_filtered_proyectos_queryset_for_user",
    "get_proyectos_available_years_for_user",
]