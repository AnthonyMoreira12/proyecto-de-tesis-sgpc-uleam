"""
Servicios HTTP para reportes de publicaciones.

Responsabilidades:

- generar la respuesta de descarga del archivo Excel;
- construir el nombre seguro del archivo;
- devolver la cantidad exacta de registros que contendría
  una exportación;
- mantener encabezados HTTP seguros para archivos privados.

La construcción del queryset y del libro Excel pertenece a:

    core.publicaciones.services.publicaciones_excel_services
"""

from django.http import HttpResponse
from django.utils import timezone

from core.publicaciones.services.publicaciones_excel_services import (
    build_publicaciones_excel,
    count_publicaciones_excel,
    workbook_to_bytes,
)
from core.reportes.services.reportes_publicaciones_pdf_services import (
    build_publicaciones_pdf_bytes,
    publicaciones_pdf_filename,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)
PDF_CONTENT_TYPE = "application/pdf"


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_filters(
    filters=None,
):
    """
    Devuelve una copia segura del diccionario de filtros.

    La validación y normalización definitiva se realiza dentro
    de publicaciones_excel_services mediante el servicio
    centralizado de listados.
    """

    if filters is None:
        return {}

    try:
        return dict(
            filters
        )

    except (
        TypeError,
        ValueError,
    ):
        return {}


def _build_excel_filename():
    """
    Genera un nombre único y seguro para el archivo Excel.

    Ejemplo:

        reporte_publicaciones_20260804_224500.xlsx
    """

    stamp = timezone.localtime().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        f"reporte_publicaciones_{stamp}.xlsx"
    )


def _build_content_disposition(
    filename,
):
    """
    Construye el encabezado de descarga.

    El nombre generado utiliza únicamente caracteres ASCII,
    por lo que no requiere codificación adicional.
    """

    safe_filename = str(
        filename or "reporte_publicaciones.xlsx"
    ).replace(
        '"',
        "",
    )

    return (
        f'attachment; filename="{safe_filename}"'
    )


# ============================================================
# VISTA PREVIA
# ============================================================

def build_export_publicaciones_preview(
    filters=None,
):
    """
    Devuelve la cantidad exacta de publicaciones que serían
    incluidas en el archivo Excel.

    Esta función usa el mismo queryset que la exportación real,
    evitando diferencias entre el conteo mostrado en Vue y las
    filas finalmente generadas.

    Parameters
    ----------
    filters:
        Diccionario opcional con los filtros enviados desde
        la interfaz.

    Returns
    -------
    dict
        Respuesta lista para ser entregada por una APIView.

    Ejemplo
    -------
    {
        "total": 18
    }
    """

    normalized_filters = _normalize_filters(
        filters
    )

    total = count_publicaciones_excel(
        normalized_filters
    )

    return {
        "total": int(
            total
        ),
    }


# ============================================================
# DESCARGA EXCEL
# ============================================================

def build_export_publicaciones_response(
    filters=None,
):
    """
    Genera el reporte de publicaciones y devuelve una respuesta
    HTTP lista para descargar.

    Parameters
    ----------
    filters:
        Diccionario opcional con los filtros que serán enviados
        al servicio generador del archivo Excel.

    Returns
    -------
    HttpResponse
        Archivo .xlsx listo para descargar.
    """

    normalized_filters = _normalize_filters(
        filters
    )

    # ========================================================
    # 1. GENERAR LIBRO EXCEL
    # ========================================================

    workbook = build_publicaciones_excel(
        normalized_filters
    )

    # ========================================================
    # 2. CONVERTIR EL LIBRO EN BYTES
    # ========================================================

    file_bytes = workbook_to_bytes(
        workbook
    )

    filename = _build_excel_filename()

    # ========================================================
    # 3. CONSTRUIR RESPUESTA HTTP
    # ========================================================

    response = HttpResponse(
        file_bytes,
        content_type=EXCEL_CONTENT_TYPE,
    )

    response[
        "Content-Disposition"
    ] = _build_content_disposition(
        filename
    )

    response[
        "Content-Length"
    ] = str(
        len(file_bytes)
    )

    # El reporte contiene información institucional y no debe
    # almacenarse en cachés compartidas.
    response[
        "Cache-Control"
    ] = (
        "private, no-store, "
        "no-cache, must-revalidate"
    )

    response[
        "Pragma"
    ] = "no-cache"

    response[
        "Expires"
    ] = "0"

    # Evita que el navegador intente interpretar el archivo
    # utilizando un tipo de contenido diferente.
    response[
        "X-Content-Type-Options"
    ] = "nosniff"

    return response

# ============================================================
# DESCARGA PDF
# ============================================================

def build_export_publicaciones_pdf_response(
    filters=None,
):
    """
    Genera el reporte PDF de publicaciones y devuelve una
    respuesta HTTP lista para descargar.

    El PDF reutiliza exactamente el mismo queryset centralizado
    que el Excel, de modo que ambos formatos respetan los mismos
    filtros y la misma regla de visibilidad institucional.
    """

    normalized_filters = _normalize_filters(
        filters
    )

    file_bytes = build_publicaciones_pdf_bytes(
        normalized_filters
    )

    filename = publicaciones_pdf_filename()

    response = HttpResponse(
        file_bytes,
        content_type=PDF_CONTENT_TYPE,
    )

    response[
        "Content-Disposition"
    ] = _build_content_disposition(
        filename
    )

    response[
        "Content-Length"
    ] = str(
        len(file_bytes)
    )

    response[
        "Cache-Control"
    ] = (
        "private, no-store, "
        "no-cache, must-revalidate"
    )

    response[
        "Pragma"
    ] = "no-cache"

    response[
        "Expires"
    ] = "0"

    response[
        "X-Content-Type-Options"
    ] = "nosniff"

    return response
