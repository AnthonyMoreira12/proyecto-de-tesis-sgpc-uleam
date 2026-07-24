"""Selectors administrativos para autores."""

from django.db.models import CharField, Count, Q, Value
from django.db.models.functions import Coalesce, Concat

from core.models import Autor


DEFAULT_ORDERING = ("apellidos", "nombres", "id")

ORDERING_MAP = {
    "nombre_asc": DEFAULT_ORDERING,
    "nombre_desc": ("-apellidos", "-nombres", "-id"),
    "publicaciones_desc": (
        "-total_publicaciones",
        "apellidos",
        "nombres",
        "id",
    ),
    "publicaciones_asc": (
        "total_publicaciones",
        "apellidos",
        "nombres",
        "id",
    ),
    "id_desc": ("-id",),
    "id_asc": ("id",),
}


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


def admin_autores_base_queryset():
    return (
        Autor.objects
        .select_related(
            "usuario",
            "usuario__carrera",
            "usuario__carrera__facultad",
        )
        .annotate(
            total_publicaciones=Count(
                "participaciones",
                distinct=True,
            ),
            nombre_completo_busqueda=Concat(
                Coalesce("nombres", Value("")),
                Value(" "),
                Coalesce("apellidos", Value("")),
                output_field=CharField(),
            ),
            usuario_nombre_completo_busqueda=Concat(
                Coalesce("usuario__nombres", Value("")),
                Value(" "),
                Coalesce("usuario__apellidos", Value("")),
                output_field=CharField(),
            ),
        )
        .order_by(*DEFAULT_ORDERING)
    )


def filter_admin_autores_queryset(
    queryset,
    *,
    q="",
    solo_con_usuario=None,
    autor_id=None,
    usuario_id=None,
    es_externo=None,
    usuario_activo=None,
    ordering="",
):
    query = _text(q)
    author_id = _positive_int(autor_id)
    user_id = _positive_int(usuario_id)
    linked = _bool(solo_con_usuario)
    external = _bool(es_externo)
    active = _bool(usuario_activo)

    if author_id is not None:
        queryset = queryset.filter(pk=author_id)

    if user_id is not None:
        queryset = queryset.filter(usuario_id=user_id)

    if linked is True:
        queryset = queryset.filter(usuario__isnull=False)
    elif linked is False:
        queryset = queryset.filter(usuario__isnull=True)

    if external is True:
        queryset = queryset.filter(es_externo=True)
    elif external is False:
        queryset = queryset.filter(es_externo=False)

    if active is True:
        queryset = queryset.filter(
            usuario__isnull=False,
            usuario__is_active=True,
        )
    elif active is False:
        queryset = queryset.filter(
            usuario__isnull=False,
            usuario__is_active=False,
        )

    if query:
        search = (
            Q(nombres__icontains=query)
            | Q(apellidos__icontains=query)
            | Q(nombre_completo_busqueda__icontains=query)
            | Q(correo__icontains=query)
            | Q(identificacion__icontains=query)
            | Q(institucion__icontains=query)
            | Q(usuario__email__icontains=query)
            | Q(usuario__nombres__icontains=query)
            | Q(usuario__apellidos__icontains=query)
            | Q(usuario_nombre_completo_busqueda__icontains=query)
            | Q(usuario__identificacion__icontains=query)
            | Q(usuario__carrera__nombre__icontains=query)
            | Q(usuario__carrera__facultad__nombre__icontains=query)
            | Q(usuario__carrera__facultad__siglas__icontains=query)
            | Q(usuario__ms_display_name__icontains=query)
            | Q(usuario__ms_mail__icontains=query)
            | Q(usuario__ms_user_principal_name__icontains=query)
        )

        numeric = _positive_int(query)
        if numeric is not None:
            search |= Q(pk=numeric) | Q(usuario_id=numeric)

        queryset = queryset.filter(search)

    fields = ORDERING_MAP.get(
        _text(ordering).lower(),
        DEFAULT_ORDERING,
    )
    return queryset.order_by(*fields)
