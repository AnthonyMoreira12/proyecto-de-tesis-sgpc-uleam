"""
Vista para servir el PDF de una publicación en modo inline.
Permite que el navegador lo previsualice en lugar de forzar descarga.
Compatible con peticiones Axios que envían Accept: application/pdf.
"""

import mimetypes
import os

from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Publicacion, PublicacionArchivo
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
    is_admin_user,
    resolve_user_autor_id,
)


class PDFRenderer(BaseRenderer):
    """
    Renderer mínimo para que DRF acepte solicitudes con:
    Accept: application/pdf

    El contenido real lo devuelve FileResponse.
    """
    media_type = "application/pdf"
    format = "pdf"
    charset = None
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


def _user_can_view_publicacion(user, publicacion):
    """
    Permiso de lectura del PDF.

    Admin: puede ver todo.
    Creador: puede ver.
    Autor vinculado: puede ver.
    Usuario autenticado: puede ver registros visibles del sistema.
    """
    if not user or not user.is_authenticated:
        return False

    if is_admin_user(user):
        return True

    if getattr(publicacion, "usuario_creador_id", None) == getattr(user, "id", None):
        return True

    if can_edit_publicacion(user, publicacion):
        return True

    autor_id = resolve_user_autor_id(user)

    if autor_id:
        return publicacion.participaciones.filter(autor_id=autor_id).exists()

    return True


def _safe_filename(file_field):
    try:
        name = getattr(file_field, "name", "") or ""
        filename = os.path.basename(name)
        return filename or "publicacion.pdf"
    except Exception:
        return "publicacion.pdf"


def _get_pdf_file(publicacion):
    """
    Prioridad:
    1. PDF principal Publicacion.archivo_pdf.
    2. Primer adjunto PublicacionArchivo.
    """
    if publicacion.archivo_pdf and getattr(publicacion.archivo_pdf, "name", None):
        return publicacion.archivo_pdf

    adjunto = (
        PublicacionArchivo.objects
        .filter(publicacion=publicacion)
        .order_by("orden", "id")
        .first()
    )

    if adjunto and adjunto.archivo and getattr(adjunto.archivo, "name", None):
        return adjunto.archivo

    return None


class PublicacionPdfInlineAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [PDFRenderer]

    def get(self, request, id):
        try:
            publicacion = (
                Publicacion.objects
                .select_related("usuario_creador", "tipo")
                .get(id=id)
            )
        except Publicacion.DoesNotExist:
            raise Http404("Publicación no encontrada.")

        if not _user_can_view_publicacion(request.user, publicacion):
            raise Http404("Archivo no encontrado.")

        pdf_file = _get_pdf_file(publicacion)

        if not pdf_file:
            raise Http404("La publicación no tiene PDF asociado.")

        filename = _safe_filename(pdf_file)
        content_type = mimetypes.guess_type(filename)[0] or "application/pdf"

        response = FileResponse(
            pdf_file.open("rb"),
            content_type=content_type,
            as_attachment=False,
            filename=filename,
        )

        response["Content-Type"] = "application/pdf"
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        response["X-Content-Type-Options"] = "nosniff"

        return response