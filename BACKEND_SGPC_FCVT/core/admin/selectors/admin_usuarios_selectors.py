"""Selectors administrativos para usuarios."""

from django.contrib.auth import get_user_model
from django.db.models import (
    CharField,
    Count,
    Prefetch,
    Q,
    Value,
)
from django.db.models.functions import (
    Coalesce,
    Concat,
)

from core.models import PublicacionAutor


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_INSTITUTIONAL = "autor"
ROLE_EXTERNAL = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"


# ============================================================
# FILTROS DE CLASIFICACIÓN
# ============================================================

INSTITUTIONAL_USER_Q = Q(
    rol=ROLE_INSTITUTIONAL,
    auth_source=AUTH_SOURCE_MICROSOFT,
)

EXTERNAL_USER_Q = Q(
    rol=ROLE_EXTERNAL,
    auth_source=AUTH_SOURCE_LOCAL,
)

ACTIVE_ADMIN_Q = (
    Q(is_staff=True)
    | Q(is_superuser=True)
)


# ============================================================
# UTILIDADES
# ============================================================

def _text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _positive_int(value):
    """
    Convierte un valor en entero positivo.

    Retorna None cuando el valor no es válido.
    """
    if (
        value in (
            None,
            "",
            "null",
            "None",
        )
        or isinstance(
            value,
            bool,
        )
    ):
        return None

    try:
        parsed = int(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None

    return (
        parsed
        if parsed > 0
        else None
    )


def _bool(value):
    """
    Convierte valores comunes en booleanos.

    Retorna None cuando el valor no puede interpretarse.
    """
    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return value

    normalized = _text(
        value
    ).lower()

    if normalized in {
        "1",
        "true",
        "yes",
        "y",
        "on",
        "si",
        "sí",
    }:
        return True

    if normalized in {
        "0",
        "false",
        "no",
        "n",
        "off",
    }:
        return False

    return None


# ============================================================
# PUBLICACIONES
# ============================================================

def _participations_queryset():
    """
    Queryset utilizado para precargar las publicaciones
    relacionadas con cada Autor.

    Incluye Publicación y Tipo para evitar consultas adicionales
    durante la serialización administrativa.
    """
    return (
        PublicacionAutor.objects
        .select_related(
            "publicacion",
            "publicacion__tipo",
            "autor",
        )
        .order_by(
            "-publicacion__anio_publicacion",
            "-publicacion_id",
            "orden",
            "id",
        )
    )


# ============================================================
# QUERYSET BASE
# ============================================================

def admin_users_base_queryset(
    *,
    include_publications=True,
):
    """
    Construye el queryset administrativo base.

    Incluye:

    - Carrera.
    - Facultad derivada desde Carrera.
    - Autor vinculado.
    - Conteo de publicaciones.
    - Campos auxiliares para búsqueda.
    - Participaciones precargadas cuando se solicitan.
    """
    queryset = (
        User.objects
        .select_related(
            "carrera",
            "carrera__facultad",
            "autor",
        )
        .annotate(
            total_publicaciones=Count(
                "autor__participaciones",
                distinct=True,
            ),

            nombre_completo_busqueda=Concat(
                Coalesce(
                    "nombres",
                    Value(""),
                ),
                Value(" "),
                Coalesce(
                    "apellidos",
                    Value(""),
                ),
                output_field=CharField(),
            ),

            autor_nombre_completo_busqueda=Concat(
                Coalesce(
                    "autor__nombres",
                    Value(""),
                ),
                Value(" "),
                Coalesce(
                    "autor__apellidos",
                    Value(""),
                ),
                output_field=CharField(),
            ),
        )
    )

    if include_publications:
        queryset = queryset.prefetch_related(
            Prefetch(
                "autor__participaciones",
                queryset=(
                    _participations_queryset()
                ),
                to_attr=(
                    "participaciones_admin"
                ),
            )
        )

    return queryset.order_by(
        "apellidos",
        "nombres",
        "id",
    )


# ============================================================
# QUERYSETS PÚBLICOS DEL SELECTOR
# ============================================================

def admin_users_list_queryset():
    """
    Queryset utilizado por el listado administrativo.

    Se precargan las publicaciones porque el serializer devuelve
    publicaciones_relacionadas incluso dentro del listado.

    Esto evita una consulta adicional por cada usuario.
    """
    return admin_users_base_queryset(
        include_publications=True
    )


def admin_users_detail_queryset():
    """
    Queryset utilizado para detalle, edición y respuestas de las
    acciones administrativas.
    """
    return admin_users_base_queryset(
        include_publications=True
    )


def active_admins_qs():
    """
    Retorna administradores activos.

    Los permisos administrativos dependen únicamente de
    is_staff o is_superuser.
    """
    return (
        User.objects
        .filter(
            is_active=True
        )
        .filter(
            ACTIVE_ADMIN_Q
        )
        .order_by(
            "pk"
        )
    )


# ============================================================
# FILTROS ADMINISTRATIVOS
# ============================================================

def filter_admin_users_queryset(
    queryset,
    *,
    q="",
    scope="",
    incompletos=False,
):
    """
    Aplica filtros de clasificación y búsqueda al queryset.

    Clasificaciones válidas:

    - institucionales:
      rol=autor y auth_source=microsoft.

    - externos:
      rol=autor_externo y auth_source=local.

    - pendientes:
      cuenta externa local e inactiva.

    - administradores:
      is_staff o is_superuser.
    """
    query = _text(
        q
    )

    normalized_scope = _text(
        scope
    ).lower()

    incomplete_filter = _bool(
        incompletos
    )

    # ========================================================
    # CLASIFICACIÓN
    # ========================================================

    if normalized_scope == "institucionales":
        queryset = queryset.filter(
            INSTITUTIONAL_USER_Q
        )

    elif normalized_scope == "externos":
        queryset = queryset.filter(
            EXTERNAL_USER_Q
        )

    elif normalized_scope == "pendientes":
        queryset = queryset.filter(
            EXTERNAL_USER_Q,
            is_active=False,
        )

    elif normalized_scope == "activos":
        queryset = queryset.filter(
            is_active=True
        )

    elif normalized_scope == "inactivos":
        queryset = queryset.filter(
            is_active=False
        )

    elif normalized_scope == "administradores":
        queryset = queryset.filter(
            ACTIVE_ADMIN_Q
        )

    elif normalized_scope == "completos":
        queryset = queryset.filter(
            perfil_completo=True
        )

    elif normalized_scope == "incompletos":
        queryset = queryset.filter(
            perfil_completo=False
        )

    elif normalized_scope in {
        "sin-clasificacion",
        "sin_clasificacion",
        "inconsistentes",
    }:
        queryset = queryset.exclude(
            INSTITUTIONAL_USER_Q
            | EXTERNAL_USER_Q
        )

    if incomplete_filter is True:
        queryset = queryset.filter(
            perfil_completo=False
        )

    # ========================================================
    # BÚSQUEDA
    # ========================================================

    if query:
        search = (
            # Usuario
            Q(
                nombres__icontains=query
            )
            | Q(
                apellidos__icontains=query
            )
            | Q(
                nombre_completo_busqueda__icontains=query
            )
            | Q(
                email__icontains=query
            )
            | Q(
                identificacion__icontains=query
            )

            # Carrera y Facultad
            | Q(
                carrera__nombre__icontains=query
            )
            | Q(
                carrera__facultad__nombre__icontains=query
            )
            | Q(
                carrera__facultad__siglas__icontains=query
            )

            # Autor
            | Q(
                autor__nombres__icontains=query
            )
            | Q(
                autor__apellidos__icontains=query
            )
            | Q(
                autor_nombre_completo_busqueda__icontains=query
            )
            | Q(
                autor__correo__icontains=query
            )
            | Q(
                autor__identificacion__icontains=query
            )
            | Q(
                autor__institucion__icontains=query
            )

            # Microsoft
            | Q(
                microsoft_id__icontains=query
            )
            | Q(
                ms_graph_id__icontains=query
            )
            | Q(
                ms_display_name__icontains=query
            )
            | Q(
                ms_mail__icontains=query
            )
            | Q(
                ms_user_principal_name__icontains=query
            )
            | Q(
                ms_job_title__icontains=query
            )
            | Q(
                ms_department__icontains=query
            )
            | Q(
                ms_office_location__icontains=query
            )

            # Publicaciones
            | Q(
                autor__participaciones__publicacion__titulo__icontains=query
            )
            | Q(
                autor__participaciones__publicacion__tipo__nombre__icontains=query
            )
            | Q(
                autor__participaciones__publicacion__tipo__codigo__icontains=query
            )
        )

        numeric_value = _positive_int(
            query
        )

        if numeric_value is not None:
            search |= (
                Q(
                    autor__participaciones__publicacion__numero=(
                        numeric_value
                    )
                )
                | Q(
                    pk=numeric_value
                )
                | Q(
                    autor__pk=numeric_value
                )
            )

        queryset = (
            queryset
            .filter(
                search
            )
            .distinct()
        )

    return queryset.order_by(
        "apellidos",
        "nombres",
        "id",
    )