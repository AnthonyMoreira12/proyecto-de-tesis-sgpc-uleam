"""Vistas para reportes de producción científica aprobada."""

import logging

from django.db import DatabaseError
from django.http import HttpResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.permisos.es_admin import EsAdmin
from core.reportes.services.reportes_pdf_services import (
    build_teacher_production_pdf_bytes,
    teacher_pdf_filename,
)
from core.reportes.services.reportes_produccion_services import (
    build_institutional_production_report,
    build_institutional_production_report_file,
    build_teacher_production_report,
    build_teacher_production_report_file,
)


logger = logging.getLogger(__name__)

EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
PDF_CONTENT_TYPE = "application/pdf"


def _download_response(file_bytes, filename, content_type):
    response = HttpResponse(file_bytes, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Content-Length"] = str(len(file_bytes))
    response["Cache-Control"] = "private, no-store, no-cache, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _excel_response(file_bytes, filename):
    return _download_response(file_bytes, filename, EXCEL_CONTENT_TYPE)


def _pdf_response(file_bytes, filename):
    return _download_response(file_bytes, filename, PDF_CONTENT_TYPE)


class ReporteProduccionAdminBaseAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, EsAdmin]


class VistaPreviaReporteProduccionAdminView(ReporteProduccionAdminBaseAPIView):
    """Producción institucional aprobada con filtros multidimensionales."""

    def get(self, request, *args, **kwargs):
        try:
            payload = build_institutional_production_report(request.query_params)
        except DatabaseError:
            logger.exception("Error de BD al construir el reporte de producción institucional.")
            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible preparar el reporte de producción debido "
                        "a un error temporal de la base de datos."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(payload, status=status.HTTP_200_OK)


class ExportarReporteProduccionAdminExcelView(ReporteProduccionAdminBaseAPIView):
    """Excel institucional con los mismos filtros de la vista previa."""

    def get(self, request, *args, **kwargs):
        try:
            file_bytes, filename = build_institutional_production_report_file(
                request.query_params
            )
        except DatabaseError:
            logger.exception("Error de BD al exportar el reporte de producción institucional.")
            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible generar el archivo Excel debido a un "
                        "error temporal de la base de datos."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return _excel_response(file_bytes, filename)


class VistaPreviaMiReporteProduccionView(APIView):
    """Reporte personal. El alcance se determina exclusivamente con request.user."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            payload = build_teacher_production_report(
                request.user,
                request.query_params,
            )
        except DatabaseError:
            logger.exception("Error de BD al construir el reporte personal de producción.")
            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible preparar su reporte de producción debido "
                        "a un error temporal de la base de datos."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(payload, status=status.HTTP_200_OK)


class ExportarMiReporteProduccionExcelView(APIView):
    """Excel de producción del usuario autenticado."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            file_bytes, filename = build_teacher_production_report_file(
                request.user,
                request.query_params,
            )
        except DatabaseError:
            logger.exception("Error de BD al exportar el reporte personal de producción.")
            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible generar su archivo Excel debido a un "
                        "error temporal de la base de datos."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return _excel_response(file_bytes, filename)


class ExportarMiReporteProduccionPdfView(APIView):
    """PDF de producción del usuario autenticado."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            payload = build_teacher_production_report(
                request.user,
                request.query_params,
                full_detail=True,
            )
            file_bytes = build_teacher_production_pdf_bytes(payload)
            filename = teacher_pdf_filename()
        except DatabaseError:
            logger.exception("Error de BD al exportar el reporte personal en PDF.")
            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible generar su archivo PDF debido a un "
                        "error temporal de la base de datos."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except RuntimeError:
            logger.exception("El generador PDF no está disponible.")
            return Response(
                {
                    "ok": False,
                    "detail": "El formato PDF no está disponible temporalmente.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return _pdf_response(file_bytes, filename)

