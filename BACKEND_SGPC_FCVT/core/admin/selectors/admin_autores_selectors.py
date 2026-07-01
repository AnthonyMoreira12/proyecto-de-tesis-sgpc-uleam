# Archivo auxiliar para consultas administrativas de autores:
# construye el queryset base, cuenta publicaciones y aplica filtros por búsqueda, usuario y autor.

from django.db.models import Count, Q

from core.models import Autor


def _safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def admin_autores_base_queryset():
    return (
        Autor.objects.select_related("usuario")
        .annotate(total_publicaciones=Count("participaciones", distinct=True))
        .order_by("apellidos", "nombres", "id")
    )


def filter_admin_autores_queryset(
    qs,
    *,
    q="",
    solo_con_usuario=None,
    autor_id=None,
    usuario_id=None,
):
    q = (q or "").strip()
    autor_id = _safe_int(autor_id)
    usuario_id = _safe_int(usuario_id)

    if autor_id:
        qs = qs.filter(pk=autor_id)

    if usuario_id:
        qs = qs.filter(usuario_id=usuario_id)

    if solo_con_usuario is True:
        qs = qs.filter(usuario__isnull=False)
    elif solo_con_usuario is False:
        qs = qs.filter(usuario__isnull=True)

    if q:
        qs = qs.filter(
            Q(nombres__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(correo__icontains=q)
            | Q(identificacion__icontains=q)
            | Q(institucion__icontains=q)
            | Q(usuario__email__icontains=q)
            | Q(usuario__nombres__icontains=q)
            | Q(usuario__apellidos__icontains=q)
        )

    return qs.order_by("apellidos", "nombres", "id")