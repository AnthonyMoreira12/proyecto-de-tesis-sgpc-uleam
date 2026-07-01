# Archivo selector para consultas administrativas de usuarios:
# centraliza querysets, filtros de búsqueda y clasificación de usuarios del módulo administrativo.
# Complementa la lógica de administración al optimizar relaciones, búsquedas y consultas reutilizables.

"""
Selectors administrativos para consultas de usuarios.
Centraliza querysets y filtros reutilizables del módulo admin.
"""
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch

from core.models import PublicacionAutor

User = get_user_model()


def _safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def admin_users_base_queryset():
    participaciones_qs = (
        PublicacionAutor.objects
        .select_related("publicacion", "publicacion__tipo", "autor")
        .order_by("orden", "id")
    )

    return (
        User.objects
        .select_related("facultad", "carrera", "autor")
        .prefetch_related(
            Prefetch(
                "autor__participaciones",
                queryset=participaciones_qs,
            )
        )
        .all()
    )


def active_admins_qs():
    return User.objects.filter(is_active=True).filter(
        Q(is_superuser=True) | Q(is_staff=True)
    )


def filter_admin_users_queryset(qs, *, q="", scope="", incompletos=False):
    q = (q or "").strip()
    scope = (scope or "").strip().lower()
    incompletos = bool(incompletos)

    if scope == "institucionales":
        qs = qs.filter(auth_source="microsoft")

    elif scope == "externos":
        qs = qs.filter(
            rol="autor_externo",
            auth_source="local",
        )

    elif scope == "pendientes":
        qs = qs.filter(
            rol="autor_externo",
            auth_source="local",
            is_active=False,
        )

    elif scope == "activos":
        qs = qs.filter(is_active=True)

    else:
        qs = qs.all()

    if q:
        search_filter = (
            Q(nombres__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(email__icontains=q)
            | Q(identificacion__icontains=q)
            | Q(facultad__nombre__icontains=q)
            | Q(carrera__nombre__icontains=q)
            | Q(autor__nombres__icontains=q)
            | Q(autor__apellidos__icontains=q)
            | Q(autor__correo__icontains=q)
            | Q(autor__identificacion__icontains=q)
            | Q(autor__institucion__icontains=q)
            | Q(autor__participaciones__publicacion__tipo__nombre__icontains=q)
            | Q(autor__participaciones__publicacion__tipo__codigo__icontains=q)
        )

        numero_q = _safe_int(q)
        if numero_q:
            search_filter = search_filter | Q(
                autor__participaciones__publicacion__numero=numero_q
            )

        qs = qs.filter(search_filter).distinct()

    if incompletos:
        qs = qs.filter(perfil_completo=False)

    return qs.order_by("apellidos", "nombres", "id")