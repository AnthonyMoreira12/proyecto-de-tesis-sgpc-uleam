"""
Servicios de reportes de publicaciones.

Construye la respuesta HTTP para descargar el archivo
Excel generado por publicaciones_excel_services.
"""

from django.http import HttpResponse
from django.utils import timezone

from core.publicaciones.services.publicaciones_excel_services import (
    build_publicaciones_excel,
    workbook_to_bytes,
)


EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


def _build_filename():
    """
    Genera un nombre único y seguro para el archivo Excel.
    """

    stamp = timezone.localtime().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        f"reporte_publicaciones_{stamp}.xlsx"
    )


def build_export_publicaciones_response(
    filters=None,
):
    """
    Genera el reporte de publicaciones y devuelve
    una respuesta HTTP lista para descarga.

    Parameters
    ----------
    filters:
        Diccionario opcional con los filtros que serán
        enviados al servicio de generación Excel.

    Returns
    -------
    HttpResponse
        Archivo .xlsx listo para descargar.
    """

    filters = dict(
        filters or {}
    )

    # ---------------------------------------------------------
    # Generar libro Excel
    # ---------------------------------------------------------

    workbook = build_publicaciones_excel(
        filters
    )

    # ---------------------------------------------------------
    # Convertir a bytes
    # ---------------------------------------------------------

    file_bytes = workbook_to_bytes(
        workbook
    )

    filename = _build_filename()

    # ---------------------------------------------------------
    # Respuesta
    # ---------------------------------------------------------

    response = HttpResponse(
        file_bytes,
        content_type=EXCEL_CONTENT_TYPE,
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="{filename}"'
    )

    response[
        "Content-Length"
    ] = str(
        len(file_bytes)
    )

    response[
        "Cache-Control"
    ] = "private, no-store"

    response[
        "X-Content-Type-Options"
    ] = "nosniff"

    return response