from django.db.models import Q

from core.models import Autor, Proyecto, Publicacion, Usuario
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
)

SEARCH_LIMIT = 8


def buscar_usuarios(q, *, limit=SEARCH_LIMIT):
    q = (q or "").strip()
    if not q:
        return Usuario.objects.none()

    return (
        Usuario.objects.select_related("carrera", "carrera__facultad")
        .filter(
            Q(nombres__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(email__icontains=q)
            | Q(carrera__nombre__icontains=q)
            | Q(carrera__facultad__nombre__icontains=q)
        )
        .order_by("apellidos", "nombres", "id")[:limit]
    )


def buscar_proyectos(q, *, limit=SEARCH_LIMIT):
    q = (q or "").strip()
    if not q:
        return Proyecto.objects.none()

    return (
        Proyecto.objects.select_related("carrera", "carrera__facultad")
        .filter(
            Q(nombre__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(carrera__nombre__icontains=q)
            | Q(carrera__facultad__nombre__icontains=q)
        )
        .order_by("nombre", "id")[:limit]
    )


def buscar_publicaciones(q, *, limit=SEARCH_LIMIT, solo_con_pdf=False):
    q = (q or "").strip()
    if not q:
        return Publicacion.objects.none()

    publicaciones = (
        Publicacion.objects.select_related(
            "tipo",
            "usuario_creador",
            "proyecto",
            "carrera",
            "carrera__facultad",
            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .filter(
            Q(titulo__icontains=q)
            | Q(tipo__nombre__icontains=q)
            | Q(tipo__codigo__icontains=q)
            | Q(proyecto__nombre__icontains=q)
            | Q(usuario_creador__nombres__icontains=q)
            | Q(usuario_creador__apellidos__icontains=q)
            | Q(carrera__facultad__nombre__icontains=q)
            | Q(carrera__nombre__icontains=q)
        )
        .distinct()
    )

    publicaciones = annotate_tipo_publicacion_final(publicaciones).exclude(
        tipo_publicacion_final="sin_clasificar"
    )

    if solo_con_pdf:
        publicaciones = publicaciones.exclude(
            archivo_pdf__isnull=True,
        ).exclude(
            archivo_pdf="",
        )

    return publicaciones.order_by("-fecha_publicacion", "-id")[:limit]


def buscar_autores(q, *, limit=SEARCH_LIMIT):
    q = (q or "").strip()
    if not q:
        return Autor.objects.none()

    return (
        Autor.objects.select_related("usuario")
        .filter(
            Q(nombres__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(correo__icontains=q)
            | Q(identificacion__icontains=q)
        )
        .order_by("apellidos", "nombres", "id")[:limit]
    )