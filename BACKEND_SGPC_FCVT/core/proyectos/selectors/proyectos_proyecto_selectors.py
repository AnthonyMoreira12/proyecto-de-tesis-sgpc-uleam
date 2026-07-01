from django.db.models import Q
from django.utils import timezone

from core.models import Proyecto


ESTADOS_ACTIVOS = {"nuevo", "arrastre"}
ESTADOS_CERRADOS = {"cierre"}

ESTADO_VALUES = {
    "nuevo",
    "arrastre",
    "cierre",
}


def _user_is_project_admin_like(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False

    return bool(
        getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
    )


def proyectos_base_queryset():
    return (
        Proyecto.objects
        .select_related("carrera", "carrera__facultad", "creado_por")
        .prefetch_related("participaciones__autor")
        .order_by("-anio_inicio", "nombre", "id")
    )


def proyectos_visible_queryset_for_user(user):
    qs = proyectos_base_queryset()

    if _user_is_project_admin_like(user):
        return qs

    return qs.filter(estado__in=ESTADOS_ACTIVOS)


def _apply_q_filter(qs, q):
    q = (q or "").strip()

    if not q:
        return qs

    return qs.filter(
        Q(nombre__icontains=q)
        | Q(descripcion__icontains=q)
        | Q(carrera__nombre__icontains=q)
        | Q(carrera__facultad__nombre__icontains=q)
        | Q(participaciones__autor__nombres__icontains=q)
        | Q(participaciones__autor__apellidos__icontains=q)
        | Q(participaciones__autor__correo__icontains=q)
    ).distinct()


def _apply_anio_filter(qs, anio):
    anio = (anio or "").strip()

    if not anio.isdigit():
        return qs

    anio = int(anio)
    current_year = timezone.now().year

    query = (
        Q(anio_inicio=anio)
        | Q(anio_fin=anio)
        | Q(anio_inicio__lte=anio, anio_fin__gte=anio)
    )

    if anio <= current_year:
        query |= Q(
            anio_inicio__lte=anio,
            anio_fin__isnull=True,
            estado__in=ESTADOS_ACTIVOS,
        )

    return qs.filter(query)


def _apply_estado_filter(qs, estado, is_admin=False):
    estado = (estado or "").strip().lower()

    if not estado:
        return qs

    if not is_admin:
        return qs

    if estado in ESTADO_VALUES:
        return qs.filter(estado=estado)

    if estado == "activo":
        return qs.filter(estado__in=ESTADOS_ACTIVOS)

    if estado == "cerrado":
        return qs.filter(estado__in=ESTADOS_CERRADOS)

    return qs


def filter_proyectos_queryset(qs, *, q="", anio="", estado="", is_admin=False):
    qs = _apply_q_filter(qs, q)
    qs = _apply_anio_filter(qs, anio)
    qs = _apply_estado_filter(qs, estado, is_admin=is_admin)
    return qs


def get_filtered_proyectos_queryset_for_user(user, *, q="", anio="", estado=""):
    is_admin = _user_is_project_admin_like(user)
    qs = proyectos_visible_queryset_for_user(user)

    return filter_proyectos_queryset(
        qs,
        q=q,
        anio=anio,
        estado=estado,
        is_admin=is_admin,
    )


def _add_year_range(years, start, end):
    if not start and not end:
        return

    if start and not end:
        years.add(start)
        return

    if end and not start:
        years.add(end)
        return

    start = min(start, end)
    end = max(start, end)

    if end - start > 30:
        years.add(start)
        years.add(end)
        return

    for current in range(start, end + 1):
        years.add(current)


def _expand_years_from_queryset(qs):
    years = set()
    current_year = timezone.now().year

    for anio_inicio, anio_fin, estado in qs.values_list(
        "anio_inicio",
        "anio_fin",
        "estado",
    ):
        if not anio_inicio and not anio_fin:
            continue

        if anio_inicio and not anio_fin:
            if estado in ESTADOS_ACTIVOS and anio_inicio <= current_year:
                _add_year_range(years, anio_inicio, current_year)
            else:
                years.add(anio_inicio)
            continue

        _add_year_range(years, anio_inicio, anio_fin)

    return sorted(years, reverse=True)


def get_proyectos_available_years_for_user(user, *, q="", estado=""):
    qs = get_filtered_proyectos_queryset_for_user(
        user,
        q=q,
        anio="",
        estado=estado,
    )

    return _expand_years_from_queryset(qs)