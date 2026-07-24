"""
Vista para servir el PDF disponible de una publicación.

Prioridad:
1. Publicacion.archivo_pdf
2. Primer PublicacionArchivo

El PDF se devuelve en modo inline para permitir su
visualización directa en el navegador.
"""

import os

from django.http import (
    FileResponse,
    Http404,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.renderers import (
    BaseRenderer,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import (
    Publicacion,
    PublicacionArchivo,
)


class PDFRenderer(BaseRenderer):
    """
    Renderer binario mínimo.

    Permite que DRF acepte:
        Accept: application/pdf

    El contenido real se entrega mediante FileResponse.
    """

    media_type = "application/pdf"
    format = "pdf"
    charset = None
    render_style = "binary"

    def render(
        self,
        data,
        accepted_media_type=None,
        renderer_context=None,
    ):
        return data


def _user_can_view_publicacion(
    user,
    publicacion,
):
    """
    La vista ya está protegida por IsAuthenticated.

    Por tanto, cualquier usuario autenticado puede
    consultar el PDF de una publicación accesible
    dentro del sistema.

    La edición/eliminación sigue teniendo controles
    de permisos independientes.
    """

    return bool(
        user
        and getattr(
            user,
            "is_authenticated",
            False,
        )
        and publicacion
    )


def _safe_filename(
    file_field,
):
    name = str(
        getattr(
            file_field,
            "name",
            "",
        )
        or ""
    ).strip()

    if not name:
        return "publicacion.pdf"

    filename = os.path.basename(
        name
    )

    return (
        filename
        or "publicacion.pdf"
    )


def _get_pdf_file(
    publicacion,
):
    """
    Obtiene el archivo que debe visualizar la interfaz.

    Prioridad:
    1. PDF principal.
    2. Primer adjunto.
    """

    archivo_pdf = getattr(
        publicacion,
        "archivo_pdf",
        None,
    )

    if (
        archivo_pdf
        and getattr(
            archivo_pdf,
            "name",
            None,
        )
    ):
        return archivo_pdf

    prefetched = getattr(
        publicacion,
        "_prefetched_objects_cache",
        {},
    )

    if "archivos" in prefetched:
        archivos = sorted(
            prefetched["archivos"],
            key=lambda item: (
                getattr(
                    item,
                    "orden",
                    0,
                ),
                getattr(
                    item,
                    "id",
                    0,
                ),
            ),
        )

        for adjunto in archivos:
            archivo = getattr(
                adjunto,
                "archivo",
                None,
            )

            if (
                archivo
                and getattr(
                    archivo,
                    "name",
                    None,
                )
            ):
                return archivo

        return None

    adjunto = (
        PublicacionArchivo.objects
        .filter(
            publicacion=publicacion
        )
        .exclude(
            archivo=""
        )
        .order_by(
            "orden",
            "id",
        )
        .first()
    )

    if not adjunto:
        return None

    archivo = getattr(
        adjunto,
        "archivo",
        None,
    )

    if (
        archivo
        and getattr(
            archivo,
            "name",
            None,
        )
    ):
        return archivo

    return None


class PublicacionPdfInlineAPIView(
    APIView
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    renderer_classes = [
        PDFRenderer
    ]

    def _get_publicacion(
        self,
        publicacion_id,
    ):
        try:
            return (
                Publicacion.objects
                .select_related(
                    "tipo",
                    "usuario_creador",
                    "carrera",
                    "carrera__facultad",
                )
                .prefetch_related(
                    "archivos"
                )
                .get(
                    pk=publicacion_id
                )
            )

        except Publicacion.DoesNotExist:
            raise Http404(
                "Publicación no encontrada."
            )

    def get(
        self,
        request,
        id,
    ):
        publicacion = (
            self._get_publicacion(
                id
            )
        )

        if not _user_can_view_publicacion(
            request.user,
            publicacion,
        ):
            raise Http404(
                "Archivo no encontrado."
            )

        pdf_file = _get_pdf_file(
            publicacion
        )

        if not pdf_file:
            raise Http404(
                "La publicación no tiene "
                "un PDF asociado."
            )

        filename = _safe_filename(
            pdf_file
        )

        try:
            file_handle = (
                pdf_file.open("rb")
            )

        except (
            FileNotFoundError,
            OSError,
            ValueError,
        ):
            raise Http404(
                "El archivo PDF no se encuentra "
                "disponible en el almacenamiento."
            )

        response = FileResponse(
            file_handle,
            content_type=(
                "application/pdf"
            ),
            as_attachment=False,
            filename=filename,
        )

        response[
            "Content-Type"
        ] = "application/pdf"

        response[
            "Content-Disposition"
        ] = (
            f'inline; filename="{filename}"'
        )

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        response[
            "Cache-Control"
        ] = "private, no-store"

        return response