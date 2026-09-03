"""
Vistas del reporte institucional de gestión científica.

Endpoints:

    GET /reportes/gestion/preview/
    GET /reportes/gestion/excel/

Ambos requieren autenticación JWT y privilegios administrativos.
"""

import logging

from django.db import DatabaseError
from django.http import HttpResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.dashboard_gestion import (
    IsManagementDashboardAdministrator,
)
from core.reportes.services.reportes_gestion_services import (
    build_institutional_report_file,
    build_institutional_report_preview,
)


logger = logging.getLogger(__name__)


class ReporteGestionBaseAPIView(
    APIView
):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
        IsManagementDashboardAdministrator,
    ]

    def get_params(
        self,
        request,
    ):
        return request.query_params


class VistaPreviaReporteGestionView(
    ReporteGestionBaseAPIView
):
    """
    Devuelve los principales indicadores que formarán parte
    del reporte, sin generar todavía el archivo Excel.
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        try:
            preview = (
                build_institutional_report_preview(
                    self.get_params(
                        request
                    )
                )
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al construir "
                    "la vista previa del reporte de gestión."
                )
            )

            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible preparar la vista previa "
                        "del reporte debido a un error temporal "
                        "de la base de datos."
                    ),
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return Response(
            preview,
            status=status.HTTP_200_OK,
        )


class ExportarReporteGestionExcelView(
    ReporteGestionBaseAPIView
):
    """
    Genera el reporte institucional de gestión científica.
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        try:
            (
                file_bytes,
                filename,
            ) = build_institutional_report_file(
                self.get_params(
                    request
                )
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al generar "
                    "el reporte institucional de gestión."
                )
            )

            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible generar el reporte "
                        "debido a un error temporal de la "
                        "base de datos."
                    ),
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        response = HttpResponse(
            file_bytes,
            content_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="{filename}"'
        )

        response[
            "Content-Length"
        ] = str(
            len(
                file_bytes
            )
        )

        response[
            "Cache-Control"
        ] = "private, no-store"

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        return response