"""Selectors administrativos para usuarios."""

from django.contrib.auth import get_user_model
from django.db.models import CharField, Count, Prefetch, Q, Value
from django.db.models.functions import Coalesce, Concat

from core.models import PublicacionAutor


User = get_user_model()


def _text(value):
    return str(value or "").strip()


def _positive_int(value):
    if value in (None, "", "null", "None") or isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if parsed > 0 else None


def _bool(value):
    if value is None or isinstance(value, bool):
        return value
    value = _text(value).lower()
    if value in {"1", "true", "yes", "y", "on", "si", "sí"}:
        return True
    if value in {"0", "false", "no", "n", "off"}:
        return False
    return None


def _participations_queryset():
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


def admin_users_base_queryset(*, include_publications=True):
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
                Coalesce("nombres", Value("")),
                Value(" "),
                Coalesce("apellidos", Value("")),
                output_field=CharField(),
            ),
            autor_nombre_completo_busqueda=Concat(
                Coalesce("autor__nombres", Value("")),
                Value(" "),
                Coalesce("autor__apellidos", Value("")),
                output_field=CharField(),
            ),
        )
    )

    if include_publications:
        queryset = queryset.prefetch_related(
            Prefetch(
                "autor__participaciones",
                queryset=_participations_queryset(),
                to_attr="participaciones_admin",
            )
        )

    return queryset.order_by("apellidos", "nombres", "id")


def admin_users_list_queryset():
    return admin_users_base_queryset(include_publications=False)


def admin_users_detail_queryset():
    return admin_users_base_queryset(include_publications=True)


def active_admins_qs():
    return (
        User.objects
        .filter(is_active=True)
        .filter(Q(is_staff=True) | Q(is_superuser=True))
        .order_by("pk")
    )


def filter_admin_users_queryset(
    queryset,
    *,
    q="",
    scope="",
    incompletos=False,
):
    query = _text(q)
    scope = _text(scope).lower()
    incomplete = _bool(incompletos)

    scope_filters = {
        "institucionales": {
            "auth_source": "microsoft",
            "rol": "autor",
        },
        "externos": {
            "rol": "autor_externo",
            "auth_source": "local",
        },
        "pendientes": {
            "rol": "autor_externo",
            "auth_source": "local",
            "is_active": False,
        },
        "activos": {"is_active": True},
        "inactivos": {"is_active": False},
        "completos": {"perfil_completo": True},
        "incompletos": {"perfil_completo": False},
    }

    if scope in scope_filters:
        queryset = queryset.filter(**scope_filters[scope])
    elif scope == "administradores":
        queryset = queryset.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        )

    if incomplete is True:
        queryset = queryset.filter(perfil_completo=False)

    if query:
        search = (
            Q(nombres__icontains=query)
            | Q(apellidos__icontains=query)
            | Q(nombre_completo_busqueda__icontains=query)
            | Q(email__icontains=query)
            | Q(identificacion__icontains=query)
            | Q(carrera__nombre__icontains=query)
            | Q(carrera__facultad__nombre__icontains=query)
            | Q(carrera__facultad__siglas__icontains=query)
            | Q(autor__nombres__icontains=query)
            | Q(autor__apellidos__icontains=query)
            | Q(autor_nombre_completo_busqueda__icontains=query)
            | Q(autor__correo__icontains=query)
            | Q(autor__identificacion__icontains=query)
            | Q(autor__institucion__icontains=query)
            | Q(microsoft_id__icontains=query)
            | Q(ms_graph_id__icontains=query)
            | Q(ms_display_name__icontains=query)
            | Q(ms_mail__icontains=query)
            | Q(ms_user_principal_name__icontains=query)
            | Q(ms_job_title__icontains=query)
            | Q(ms_department__icontains=query)
            | Q(ms_office_location__icontains=query)
            | Q(
                autor__participaciones__publicacion__tipo__nombre__icontains=query
            )
            | Q(
                autor__participaciones__publicacion__tipo__codigo__icontains=query
            )
        )

        numeric = _positive_int(query)
        if numeric is not None:
            search |= (
                Q(
                    autor__participaciones__publicacion__numero=numeric
                )
                | Q(pk=numeric)
                | Q(autor__pk=numeric)
            )

        queryset = queryset.filter(search).distinct()

    return queryset.order_by("apellidos", "nombres", "id")
