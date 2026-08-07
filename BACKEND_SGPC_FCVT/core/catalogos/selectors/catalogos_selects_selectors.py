"""

Este módulo centraliza las consultas ligeras utilizadas por:

- APIViews de catálogos.
- ViewSet de selects.
- Formularios de publicaciones.
- Formularios de proyectos.
- Filtros académicos y administrativos.

Los selectores:

- Validan identificadores antes de consultar.
- Mantienen la relación Facultad -> Carrera.
- Derivan la facultad desde Carrera.
- Controlan proyectos activos y cerrados.
- Mantienen visible un proyecto previamente seleccionado.
- Limitan defensivamente los resultados de autores.
"""

import unicodedata

from django.core.exceptions import FieldDoesNotExist
from django.db.models import (
    Case,
    IntegerField,
    Q,
    Value,
    When,
)

from core.models import (
    AreaConocimiento,
    Autor,
    Carrera,
    Ciudad,
    Facultad,
    Pais,
    Proyecto,
    Subarea,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

ESTADOS_PROYECTO_ACTIVOS = {
    "nuevo",
    "arrastre",
}

MAX_SELECT_QUERY_LENGTH = 200

AUTOR_SELECT_LIMIT = 100
AUTOR_SELECT_MAX_LIMIT = 200


# ============================================================
# UTILIDADES DE MODELOS
# ============================================================

def _model_has_field(
    model,
    field_name,
):
    """
    Comprueba si un modelo contiene un campo determinado.
    """
    try:
        model._meta.get_field(
            field_name
        )

        return True

    except FieldDoesNotExist:
        return False


def _existing_value_fields(
    model,
    base_fields,
    optional_fields=None,
):
    """
    Devuelve únicamente los campos que realmente existen en el
    modelo.

    Esto permite conservar compatibilidad con catálogos que
    pueden tener campos adicionales, como iso2, iso3, admin1 o
    geoname_id.
    """
    fields = list(
        base_fields or []
    )

    for field_name in (
        optional_fields or []
    ):
        if _model_has_field(
            model,
            field_name,
        ):
            fields.append(
                field_name
            )

    return fields


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _norm_text(value):
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

    return normalized[
        :MAX_SELECT_QUERY_LENGTH
    ]


def _norm_email(value):
    """
    Normaliza una dirección de correo.
    """
    normalized = str(
        value or ""
    ).strip().lower()

    return normalized or None


def _parse_optional_positive_int(value):
    """
    Analiza un identificador opcional.

    Retorna:

        (fue_proporcionado, valor_normalizado)

    Ejemplos:

        None       -> (False, None)
        ""         -> (False, None)
        "15"       -> (True, 15)
        "abc"      -> (True, None)
        "-2"       -> (True, None)
    """
    if value in (
        None,
        "",
    ):
        return False, None

    if isinstance(
        value,
        bool,
    ):
        return True, None

    try:
        normalized_value = int(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return True, None

    if normalized_value <= 0:
        return True, None

    return True, normalized_value


def _safe_int(value):
    """
    Mantiene compatibilidad con imports existentes.

    Devuelve un entero positivo o None.
    """
    _, normalized_value = (
        _parse_optional_positive_int(
            value
        )
    )

    return normalized_value


def _normalize_limit(
    value,
    *,
    default=AUTOR_SELECT_LIMIT,
    maximum=AUTOR_SELECT_MAX_LIMIT,
):
    """
    Normaliza límites de resultados.
    """
    if isinstance(
        value,
        bool,
    ):
        return int(default)

    try:
        normalized_limit = int(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        normalized_limit = int(
            default
        )

    return max(
        1,
        min(
            normalized_limit,
            int(maximum),
        ),
    )


# ============================================================
# PERMISOS
# ============================================================

def _is_admin_user(user):
    """
    Determina si el usuario posee privilegios administrativos.

    Se conserva este nombre para mantener compatibilidad con las
    vistas actuales del módulo de catálogos.
    """
    if (
        user is None
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        return False

    role = _norm_text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()

    return bool(
        getattr(
            user,
            "is_superuser",
            False,
        )
        or getattr(
            user,
            "is_staff",
            False,
        )
        or getattr(
            user,
            "es_admin",
            False,
        )
        or role in {
            "admin",
            "administrador",
        }
    )


# ============================================================
# FACULTADES
# ============================================================

def build_facultades_select_data():
    """
    Construye el catálogo ligero de facultades.
    """
    return list(
        Facultad.objects
        .values(
            "id",
            "nombre",
        )
        .order_by(
            "nombre",
            "id",
        )
    )


# ============================================================
# CARRERAS
# ============================================================

def build_carreras_select_data(
    *,
    facultad_id=None,
):
    """
    Construye el catálogo de carreras.

    Cuando facultad_id es proporcionado, solo devuelve las
    carreras pertenecientes a dicha facultad.
    """
    was_provided, normalized_faculty_id = (
        _parse_optional_positive_int(
            facultad_id
        )
    )

    if (
        was_provided
        and normalized_faculty_id is None
    ):
        return []

    queryset = (
        Carrera.objects
        .select_related(
            "facultad",
        )
        .all()
    )

    if normalized_faculty_id is not None:
        queryset = queryset.filter(
            facultad_id=normalized_faculty_id
        )

    data = []

    for career in queryset.order_by(
        "nombre",
        "id",
    ):
        faculty = getattr(
            career,
            "facultad",
            None,
        )

        career_name = _norm_text(
            getattr(
                career,
                "nombre",
                "",
            )
        )

        faculty_name = _norm_text(
            getattr(
                faculty,
                "nombre",
                "",
            )
        )

        data.append(
            {
                "id": career.id,
                "nombre": career_name,
                "label": career_name,
                "facultad_id": (
                    career.facultad_id
                ),
                "facultad": faculty_name,
                "facultad_nombre": faculty_name,
            }
        )

    return data


# ============================================================
# PROYECTOS
# ============================================================

def build_proyectos_select_data(
    *,
    carrera_id=None,
    include_id=None,
    q="",
    incluir_cerrados=False,
):
    """
    Construye el catálogo de proyectos dependiente de carrera.

    Reglas:

    - El proyecto se filtra por carrera_id.
    - Los estados activos son nuevo y arrastre.
    - Los administradores pueden consultar proyectos cerrados.
    - include_id conserva visible un proyecto previamente
      seleccionado, aunque se encuentre cerrado.
    - El proyecto incluido debe pertenecer a la carrera
      actualmente seleccionada.
    """
    was_career_provided, normalized_career_id = (
        _parse_optional_positive_int(
            carrera_id
        )
    )

    if (
        was_career_provided
        and normalized_career_id is None
    ):
        return []

    _, normalized_include_id = (
        _parse_optional_positive_int(
            include_id
        )
    )

    normalized_query = _norm_text(
        q
    )

    base_queryset = (
        Proyecto.objects
        .select_related(
            "carrera",
            "carrera__facultad",
        )
        .all()
    )

    if normalized_career_id is not None:
        base_queryset = base_queryset.filter(
            carrera_id=normalized_career_id
        )

    filtered_queryset = base_queryset

    if normalized_query:
        filtered_queryset = (
            filtered_queryset.filter(
                Q(
                    nombre__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    descripcion__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    carrera__nombre__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    carrera__facultad__nombre__icontains=(
                        normalized_query
                    )
                )
            )
        )

    if not incluir_cerrados:
        filtered_queryset = (
            filtered_queryset.filter(
                estado__in=(
                    ESTADOS_PROYECTO_ACTIVOS
                )
            )
        )

    projects = list(
        filtered_queryset
        .distinct()
        .order_by(
            "nombre",
            "id",
        )
    )

    # include_id no depende del texto buscado.
    # Solo respeta el filtro de carrera.
    if normalized_include_id is not None:
        already_included = any(
            project.id
            == normalized_include_id
            for project in projects
        )

        if not already_included:
            included_project = (
                base_queryset
                .filter(
                    pk=normalized_include_id
                )
                .first()
            )

            if included_project is not None:
                projects.append(
                    included_project
                )

                projects.sort(
                    key=lambda item: (
                        _norm_text(
                            getattr(
                                item,
                                "nombre",
                                "",
                            )
                        ).casefold(),
                        getattr(
                            item,
                            "id",
                            0,
                        )
                        or 0,
                    )
                )

    data = []

    for project in projects:
        career = getattr(
            project,
            "carrera",
            None,
        )

        faculty = (
            getattr(
                career,
                "facultad",
                None,
            )
            if career is not None
            else None
        )

        project_name = _norm_text(
            getattr(
                project,
                "nombre",
                "",
            )
        )

        description = _norm_text(
            getattr(
                project,
                "descripcion",
                "",
            )
        )

        career_name = _norm_text(
            getattr(
                career,
                "nombre",
                "",
            )
        )

        faculty_name = _norm_text(
            getattr(
                faculty,
                "nombre",
                "",
            )
        )

        project_status = _norm_text(
            getattr(
                project,
                "estado",
                "",
            )
        ).lower()

        get_status_display = getattr(
            project,
            "get_estado_display",
            None,
        )

        if callable(get_status_display):
            status_label = _norm_text(
                get_status_display()
            )

        else:
            status_label = project_status

        data.append(
            {
                "id": project.id,
                "nombre": project_name,
                "label": project_name,
                "descripcion": description,

                "estado": project_status,
                "estado_label": status_label,
                "es_activo": (
                    project_status
                    in ESTADOS_PROYECTO_ACTIVOS
                ),

                "carrera_id": (
                    getattr(
                        project,
                        "carrera_id",
                        None,
                    )
                ),
                "carrera": career_name,
                "carrera_nombre": career_name,

                "facultad_id": (
                    getattr(
                        faculty,
                        "id",
                        None,
                    )
                ),
                "facultad": faculty_name,
                "facultad_nombre": faculty_name,

                "anio_inicio": getattr(
                    project,
                    "anio_inicio",
                    None,
                ),
                "anio_fin": getattr(
                    project,
                    "anio_fin",
                    None,
                ),

                "fecha_inicio": getattr(
                    project,
                    "fecha_inicio",
                    None,
                ),
                "fecha_fin_planificada": (
                    getattr(
                        project,
                        "fecha_fin_planificada",
                        None,
                    )
                ),
                "fecha_fin_prorrogada": (
                    getattr(
                        project,
                        "fecha_fin_prorrogada",
                        None,
                    )
                ),
                "fecha_cierre": getattr(
                    project,
                    "fecha_cierre",
                    None,
                ),
            }
        )

    return data


# ============================================================
# PAÍSES
# ============================================================

def build_paises_select_data():
    """
    Construye el catálogo de países.

    Incluye iso2 e iso3 únicamente cuando esos campos existen.
    """
    fields = _existing_value_fields(
        Pais,
        base_fields=[
            "id",
            "nombre",
        ],
        optional_fields=[
            "iso2",
            "iso3",
        ],
    )

    return list(
        Pais.objects
        .values(
            *fields
        )
        .order_by(
            "nombre",
            "id",
        )
    )


# ============================================================
# CIUDADES
# ============================================================

def build_ciudades_select_data(
    *,
    pais_id=None,
):
    """
    Construye el catálogo de ciudades dependiente de país.
    """
    was_provided, normalized_country_id = (
        _parse_optional_positive_int(
            pais_id
        )
    )

    if (
        was_provided
        and normalized_country_id is None
    ):
        return []

    queryset = Ciudad.objects.all()

    if normalized_country_id is not None:
        queryset = queryset.filter(
            pais_id=normalized_country_id
        )

    fields = _existing_value_fields(
        Ciudad,
        base_fields=[
            "id",
            "nombre",
            "pais_id",
        ],
        optional_fields=[
            "admin1",
            "geoname_id",
        ],
    )

    return list(
        queryset
        .values(
            *fields
        )
        .order_by(
            "nombre",
            "id",
        )
    )


# ============================================================
# ÁREAS DE CONOCIMIENTO
# ============================================================

def build_areas_select_data():
    """
    Construye el catálogo de áreas de conocimiento.
    """
    return list(
        AreaConocimiento.objects
        .values(
            "id",
            "nombre",
        )
        .order_by(
            "nombre",
            "id",
        )
    )


# ============================================================
# SUBÁREAS
# ============================================================

def build_subareas_select_data(
    *,
    area_id=None,
):
    """
    Construye el catálogo de subáreas dependiente de área.
    """
    was_provided, normalized_area_id = (
        _parse_optional_positive_int(
            area_id
        )
    )

    if (
        was_provided
        and normalized_area_id is None
    ):
        return []

    queryset = Subarea.objects.all()

    if normalized_area_id is not None:
        queryset = queryset.filter(
            area_id=normalized_area_id
        )

    return list(
        queryset
        .values(
            "id",
            "nombre",
        )
        .order_by(
            "nombre",
            "id",
        )
    )


# ============================================================
# AUTORES
# ============================================================

def build_autores_select_data(
    *,
    q="",
    limit=AUTOR_SELECT_LIMIT,
):
    """
    Construye el selector y autocompletado de autores.

    Busca por:

    - Nombres.
    - Apellidos.
    - Identificación.
    - Correo.
    - Institución.
    - ORCID.
    - Registro de investigador SENESCYT.
    - Perfil de Google Scholar.
    - Scopus ID.
    - Datos del usuario vinculado.

    Las coincidencias exactas se muestran antes que las
    coincidencias parciales.
    """
    normalized_query = _norm_text(
        q
    )

    normalized_limit = _normalize_limit(
        limit,
        default=AUTOR_SELECT_LIMIT,
        maximum=AUTOR_SELECT_MAX_LIMIT,
    )

    queryset = (
        Autor.objects
        .select_related(
            "usuario",
        )
        .all()
    )

    if normalized_query:
        queryset = (
            queryset
            .filter(
                Q(
                    nombres__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    apellidos__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    identificacion__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    correo__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    institucion__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    orcid__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    registro_senescyt__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    google_scholar__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    scopus_id__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    usuario__nombres__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    usuario__apellidos__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    usuario__identificacion__icontains=(
                        normalized_query
                    )
                )
                | Q(
                    usuario__email__icontains=(
                        normalized_query
                    )
                )
            )
            .annotate(
                _select_priority=Case(
                    When(
                        orcid__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        registro_senescyt__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        scopus_id__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        identificacion__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        correo__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        usuario__identificacion__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        usuario__email__iexact=(
                            normalized_query
                        ),
                        then=Value(0),
                    ),
                    When(
                        nombres__iexact=(
                            normalized_query
                        ),
                        then=Value(1),
                    ),
                    When(
                        apellidos__iexact=(
                            normalized_query
                        ),
                        then=Value(1),
                    ),
                    When(
                        nombres__istartswith=(
                            normalized_query
                        ),
                        then=Value(2),
                    ),
                    When(
                        apellidos__istartswith=(
                            normalized_query
                        ),
                        then=Value(2),
                    ),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            )
            .distinct()
            .order_by(
                "_select_priority",
                "apellidos",
                "nombres",
                "id",
            )
        )

    else:
        queryset = queryset.order_by(
            "apellidos",
            "nombres",
            "id",
        )

    data = []

    for author in queryset[
        :normalized_limit
    ]:
        linked_user = getattr(
            author,
            "usuario",
            None,
        )

        names = _norm_text(
            getattr(
                author,
                "nombres",
                "",
            )
        )

        surnames = _norm_text(
            getattr(
                author,
                "apellidos",
                "",
            )
        )

        full_name = " ".join(
            value
            for value in [
                names,
                surnames,
            ]
            if value
        )

        author_email = _norm_email(
            getattr(
                author,
                "correo",
                None,
            )
        )

        user_email = _norm_email(
            getattr(
                linked_user,
                "email",
                None,
            )
            if linked_user is not None
            else None
        )

        # El usuario vinculado es la fuente principal.
        resolved_email = (
            user_email
            or author_email
        )

        label = (
            full_name
            or resolved_email
            or _norm_text(
                getattr(
                    author,
                    "identificacion",
                    "",
                )
            )
            or f"Autor {author.id}"
        )

        data.append(
            {
                "id": author.id,
                "nombres": names,
                "apellidos": surnames,

                "identificacion": getattr(
                    author,
                    "identificacion",
                    None,
                ),
                "correo": resolved_email,
                "institucion": getattr(
                    author,
                    "institucion",
                    None,
                ),
                "orcid": getattr(
                    author,
                    "orcid",
                    None,
                ),
                "registro_senescyt": getattr(
                    author,
                    "registro_senescyt",
                    None,
                ),
                "google_scholar": getattr(
                    author,
                    "google_scholar",
                    None,
                ),
                "scopus_id": getattr(
                    author,
                    "scopus_id",
                    None,
                ),
                "es_externo": bool(
                    getattr(
                        author,
                        "es_externo",
                        False,
                    )
                ),

                "usuario_id": (
                    getattr(
                        linked_user,
                        "id",
                        None,
                    )
                ),

                "nombre": full_name,
                "nombre_completo": full_name,
                "label": label,

                "es_admin": bool(
                    linked_user
                    and (
                        getattr(
                            linked_user,
                            "is_staff",
                            False,
                        )
                        or getattr(
                            linked_user,
                            "is_superuser",
                            False,
                        )
                    )
                ),
            }
        )

    return data