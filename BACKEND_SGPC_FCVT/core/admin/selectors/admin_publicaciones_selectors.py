# Archivo auxiliar para consultas administrativas de publicaciones:
# construye el queryset base, precarga relaciones y aplica filtros por búsqueda, tipo, autor, año, facultad, carrera, PDF 
# y ordenamiento.

from django.db.models import Count, Prefetch, Q, Value, CharField
from django.db.models.functions import Coalesce

from core.models import Publicacion, PublicacionAutor
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
)


def _safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def _safe_bool(value):
    if value is None:
        return None

    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return None


def admin_publicaciones_base_queryset():
    participaciones_qs = (
        PublicacionAutor.objects.select_related("autor")
        .order_by("orden", "id")
    )

    qs = (
        Publicacion.objects.select_related(
            "tipo",
            "usuario_creador",
            "admin_registrador",
            "carrera__facultad",
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "pais",
            "ciudad",
            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .prefetch_related(
            Prefetch(
                "participaciones",
                queryset=participaciones_qs,
                to_attr="participaciones_ordenadas",
            ),
            "archivos",
        )
        .annotate(
            adjuntos_total=Count("archivos", distinct=True),
            titulo_admin=Coalesce(
                "articulo__nombre_articulo",
                "ponencia__nombre_ponencia",
                "libro__nombre_libro",
                "capitulo_libro__nombre_capitulo",
                "proyecto__nombre",
                Value("", output_field=CharField()),
            ),
        )
        .order_by("-updated_at", "-id")
    )

    return annotate_tipo_publicacion_final(qs)


def filter_admin_publicaciones_queryset(
    qs,
    *,
    q="",
    tipo="",
    usuario_objetivo_id=None,
    autor_objetivo_id=None,
    admin_registrador_id=None,
    facultad_id=None,
    carrera_id=None,
    anio=None,
    solo_delegadas=None,
    solo_con_pdf=None,
    solo_con_adjuntos=None,
    ordering="",
):
    q = (q or "").strip()
    tipo = (tipo or "").strip().lower()
    ordering = (ordering or "").strip().lower()

    usuario_objetivo_id = _safe_int(usuario_objetivo_id)
    autor_objetivo_id = _safe_int(autor_objetivo_id)
    admin_registrador_id = _safe_int(admin_registrador_id)
    facultad_id = _safe_int(facultad_id)
    carrera_id = _safe_int(carrera_id)
    anio = _safe_int(anio)

    solo_delegadas = _safe_bool(solo_delegadas)
    solo_con_pdf = _safe_bool(solo_con_pdf)
    solo_con_adjuntos = _safe_bool(solo_con_adjuntos)

    if usuario_objetivo_id:
        qs = qs.filter(usuario_creador_id=usuario_objetivo_id)

    if autor_objetivo_id:
        qs = qs.filter(participaciones__autor_id=autor_objetivo_id)

    if admin_registrador_id:
        qs = qs.filter(admin_registrador_id=admin_registrador_id)

    if facultad_id:
        qs = qs.filter(carrera__facultad_id=facultad_id)

    if carrera_id:
        qs = qs.filter(carrera_id=carrera_id)

    if anio:
        qs = qs.filter(anio_publicacion=anio)

    if solo_delegadas is True:
        qs = qs.filter(registrado_por_admin=True)
    elif solo_delegadas is False:
        qs = qs.filter(registrado_por_admin=False)

    if solo_con_pdf is True:
        qs = qs.filter(
            (
                Q(archivo_pdf__isnull=False)
                & ~Q(archivo_pdf="")
            )
            | Q(adjuntos_total__gt=0)
        )
    elif solo_con_pdf is False:
        qs = qs.filter(
            (
                Q(archivo_pdf__isnull=True)
                | Q(archivo_pdf="")
            )
            & Q(adjuntos_total=0)
        )

    if solo_con_adjuntos is True:
        qs = qs.filter(adjuntos_total__gt=0)
    elif solo_con_adjuntos is False:
        qs = qs.filter(adjuntos_total=0)

    if tipo:
        qs = qs.filter(tipo_publicacion_final=tipo)

    if q:
        qs = qs.filter(
            Q(tipo__nombre__icontains=q)
            | Q(tipo__codigo__icontains=q)
            | Q(titulo_admin__icontains=q)
            | Q(proyecto__nombre__icontains=q)
            | Q(carrera__facultad__nombre__icontains=q)
            | Q(carrera__nombre__icontains=q)
            | Q(area__nombre__icontains=q)
            | Q(subarea__nombre__icontains=q)
            | Q(usuario_creador__nombres__icontains=q)
            | Q(usuario_creador__apellidos__icontains=q)
            | Q(usuario_creador__email__icontains=q)
            | Q(admin_registrador__nombres__icontains=q)
            | Q(admin_registrador__apellidos__icontains=q)
            | Q(admin_registrador__email__icontains=q)
            | Q(participaciones__autor__nombres__icontains=q)
            | Q(participaciones__autor__apellidos__icontains=q)
            | Q(participaciones__autor__correo__icontains=q)
            | Q(participaciones__autor__identificacion__icontains=q)
            | Q(participaciones__autor__institucion__icontains=q)
            | Q(articulo__nombre_articulo__icontains=q)
            | Q(articulo__nombre_revista__icontains=q)
            | Q(articulo__codigo_doi__icontains=q)
            | Q(articulo__codigo_issn__icontains=q)
            | Q(ponencia__nombre_evento__icontains=q)
            | Q(ponencia__nombre_ponencia__icontains=q)
            | Q(libro__nombre_libro__icontains=q)
            | Q(libro__codigo_isbn__icontains=q)
            | Q(capitulo_libro__nombre_capitulo__icontains=q)
            | Q(capitulo_libro__nombre_libro__icontains=q)
            | Q(capitulo_libro__codigo_isbn__icontains=q)
        )

    qs = qs.distinct()

    ordering_map = {
        "updated_desc": ("-updated_at", "-id"),
        "updated_asc": ("updated_at", "id"),
        "created_desc": ("-created_at", "-id"),
        "created_asc": ("created_at", "id"),
        "fecha_desc": ("-fecha_publicacion", "-id"),
        "fecha_asc": ("fecha_publicacion", "id"),
        "titulo_asc": ("titulo_admin", "id"),
        "titulo_desc": ("-titulo_admin", "-id"),
        "numero_desc": ("-numero", "-id"),
        "numero_asc": ("numero", "id"),
    }

    selected_ordering = ordering_map.get(ordering, ("-updated_at", "-id"))
    return qs.order_by(*selected_ordering)