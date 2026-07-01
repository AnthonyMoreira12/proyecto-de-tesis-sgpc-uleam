"""
Servicios de reportes para exportación de publicaciones.
Construye la respuesta HTTP lista para descarga del archivo Excel.
"""

from django.http import HttpResponse
from django.utils import timezone

from core.publicaciones.services.publicaciones_excel_services import (
    build_publicaciones_excel,
    workbook_to_bytes,
)


def build_export_publicaciones_response(filters=None):
    filters = filters or {}

    workbook = build_publicaciones_excel(filters)
    file_bytes = workbook_to_bytes(workbook)

    stamp = timezone.localtime().strftime("%Y%m%d_%H%M%S")
    filename = f"reporte_publicaciones_{stamp}.xlsx"

    response = HttpResponse(
        file_bytes,
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response