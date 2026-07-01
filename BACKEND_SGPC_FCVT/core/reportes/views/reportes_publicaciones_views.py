"""
Views de reportes para exportación de publicaciones.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.reportes.services.reportes_publicaciones_services import (
    build_export_publicaciones_response,
)


class ExportarPublicacionesExcelView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filters = {
            "tipo": request.query_params.get("tipo", ""),
            "anio": request.query_params.get("anio", ""),
            "anio_desde": request.query_params.get("anio_desde", ""),
            "anio_hasta": request.query_params.get("anio_hasta", ""),
            "texto": request.query_params.get("texto", ""),
            "facultad": request.query_params.get("facultad", ""),
            "carrera": request.query_params.get("carrera", ""),
            "proyecto": request.query_params.get("proyecto", ""),
        }

        return build_export_publicaciones_response(filters)