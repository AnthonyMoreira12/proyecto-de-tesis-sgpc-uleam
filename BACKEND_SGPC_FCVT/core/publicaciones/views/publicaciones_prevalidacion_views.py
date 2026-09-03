"""Endpoint integral de prevalidación de publicaciones."""

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.services.publicaciones_prevalidacion_services import (
    prevalidar_publicacion,
)


class PublicacionPrevalidarAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    POST /publicaciones/prevalidar/

    Ejecuta, sin escribir en la base de datos:
    - validación del PDF si se adjunta;
    - integridad institucional y académica;
    - detección de duplicados fuertes;
    - advertencias por posibles coincidencias.

    Una validación negativa sigue respondiendo HTTP 200 porque el
    endpoint procesó correctamente la consulta. ``valido`` y
    ``puede_continuar`` indican si el formulario puede guardarse.
    """

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    def post(self, request):
        uploaded_file = (
            request.FILES.get("archivo_pdf")
            if hasattr(request, "FILES")
            else None
        )

        payload = prevalidar_publicacion(
            request.data,
            actor=request.user,
            uploaded_file=uploaded_file,
        )

        return Response(
            payload,
            status=status.HTTP_200_OK,
        )