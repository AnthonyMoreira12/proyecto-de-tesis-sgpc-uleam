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
    AllowAny,
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
from core.publicaciones.utils.publicaciones_visibilidad_utils import (
    apply_user_visible_publicaciones_scope,
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


def _safe_filename(
    value,
):
    if isinstance(value, str):
        name = value
    else:
        name = getattr(
            value,
            "name",
            "",
        )

    name = str(
        name or ""
    ).strip()

    if not name:
        return "publicacion.pdf"

    filename = os.path.basename(
        name
    ).replace(
        "\r",
        "",
    ).replace(
        "\n",
        "",
    ).strip()

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


def _get_pdf_filename(
    publicacion,
    pdf_file,
):
    pdf_name = str(
        getattr(
            pdf_file,
            "name",
            "",
        )
        or ""
    ).strip()

    principal = getattr(
        publicacion,
        "archivo_pdf",
        None,
    )

    principal_name = str(
        getattr(
            principal,
            "name",
            "",
        )
        or ""
    ).strip()

    if (
        pdf_name
        and principal_name
        and pdf_name == principal_name
    ):
        return _safe_filename(
            getattr(
                publicacion,
                "archivo_pdf_nombre_original",
                None,
            )
            or pdf_file
        )

    prefetched = getattr(
        publicacion,
        "_prefetched_objects_cache",
        {},
    )

    if "archivos" in prefetched:
        adjuntos = prefetched["archivos"]
    else:
        adjuntos = (
            PublicacionArchivo.objects
            .filter(
                publicacion=publicacion
            )
            .order_by(
                "orden",
                "id",
            )
        )

    for adjunto in adjuntos:
        archivo = getattr(
            adjunto,
            "archivo",
            None,
        )

        archivo_name = str(
            getattr(
                archivo,
                "name",
                "",
            )
            or ""
        ).strip()

        if (
            not pdf_name
            or archivo_name != pdf_name
        ):
            continue

        return _safe_filename(
            getattr(
                adjunto,
                "nombre_original",
                None,
            )
            or getattr(
                adjunto,
                "nombre",
                None,
            )
            or pdf_file
        )

    return _safe_filename(
        pdf_file
    )


class PublicacionPdfInlineAPIView(
    APIView
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        AllowAny
    ]

    renderer_classes = [
        PDFRenderer
    ]

    def _get_publicacion(
        self,
        publicacion_id,
        *,
        user,
    ):
        try:
            queryset = (
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
            )

            queryset = (
                apply_user_visible_publicaciones_scope(
                    queryset,
                    user=user,
                )
            )

            return queryset.get(
                pk=publicacion_id
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
                id,
                user=request.user,
            )
        )

        pdf_file = _get_pdf_file(
            publicacion
        )

        if not pdf_file:
            raise Http404(
                "La publicación no tiene "
                "un PDF asociado."
            )

        filename = _get_pdf_filename(
            publicacion,
            pdf_file,
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
            "X-Content-Type-Options"
        ] = "nosniff"

        response[
            "Cache-Control"
        ] = "private, no-store"

        return response