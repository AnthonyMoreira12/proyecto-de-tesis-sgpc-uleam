"""Vistas HTTP para reportes de publicaciones.

Endpoints previstos:

- Descarga del archivo Excel:
    GET /reportes/publicaciones/excel/

- Descarga del archivo PDF:
    GET /reportes/publicaciones/pdf/

- Vista previa del total compartida por ambos formatos:
    GET /reportes/publicaciones/excel/preview/

Las vistas:

- requieren autenticación JWT;
- admiten los mismos filtros;
- reutilizan el mismo queryset centralizado;
- evitan diferencias entre el conteo y el Excel generado.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.reportes.services.reportes_publicaciones_services import (
    build_export_publicaciones_pdf_response,
    build_export_publicaciones_preview,
    build_export_publicaciones_response,
)


# ============================================================
# UTILIDADES
# ============================================================

def _first_query_param(
    query_params,
    *names,
    default=None,
):
    """
    Devuelve el primer parámetro no vacío encontrado.

    Permite mantener compatibilidad entre los nombres antiguos
    y actuales de los filtros enviados por el frontend.

    Ejemplo:

        _first_query_param(
            request.query_params,
            "texto",
            "q",
            "search",
        )
    """

    for name in names:
        value = query_params.get(
            name,
            None,
        )

        if value not in (
            None,
            "",
        ):
            return value

    return default


def build_publicaciones_report_filters(
    request,
):
    """
    Construye el diccionario de filtros compartido por:

    - la descarga Excel;
    - la descarga PDF;
    - la vista previa del conteo.

    La validación definitiva se realiza dentro del servicio
    centralizado de publicaciones.

    Filtros admitidos:

    - tipo;
    - origen_tipo;
    - anio;
    - mes;
    - anio_desde;
    - anio_hasta;
    - texto;
    - sede;
    - facultad;
    - carrera;
    - proyecto;
    - solo_con_pdf;
    - orden.
    """

    params = request.query_params

    return {
        # =====================================================
        # TIPO DE PUBLICACIÓN
        # =====================================================

        "tipo": _first_query_param(
            params,
            "tipo",
            "tipo_publicacion_final",
        ),

        # =====================================================
        # ORIGEN
        # =====================================================

        "origen_tipo": _first_query_param(
            params,
            "origen_tipo",
            "origen",
        ),

        # =====================================================
        # AÑO EXACTO
        # =====================================================

        "anio": _first_query_param(
            params,
            "anio",
        ),

        # =====================================================
        # MES
        # =====================================================

        "mes": _first_query_param(
            params,
            "mes",
            "mes_publicacion",
        ),

        # =====================================================
        # RANGO DE AÑOS
        # =====================================================

        "anio_desde": _first_query_param(
            params,
            "anio_desde",
            "desde",
        ),

        "anio_hasta": _first_query_param(
            params,
            "anio_hasta",
            "hasta",
        ),

        # =====================================================
        # BÚSQUEDA TEXTUAL
        # =====================================================

        "texto": _first_query_param(
            params,
            "texto",
            "q",
            "search",
        ),

        # =====================================================
        # UBICACIÓN ACADÉMICA
        # =====================================================

        "sede": _first_query_param(
            params,
            "sede",
            "sede_id",
        ),

        "facultad": _first_query_param(
            params,
            "facultad",
            "facultad_id",
        ),

        "carrera": _first_query_param(
            params,
            "carrera",
            "carrera_id",
        ),

        # =====================================================
        # PROYECTO
        # =====================================================

        "proyecto": _first_query_param(
            params,
            "proyecto",
            "proyecto_id",
        ),

        # =====================================================
        # PDF
        # =====================================================

        "solo_con_pdf": _first_query_param(
            params,
            "solo_con_pdf",
            "con_pdf",
            default="",
        ),

        # =====================================================
        # ORDENAMIENTO
        # =====================================================

        "orden": _first_query_param(
            params,
            "orden",
            "ordering",
            default="recientes",
        ),
    }


# ============================================================
# CLASE BASE
# ============================================================

class PublicacionesReporteBaseAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    Base compartida para las vistas del reporte.

    Centraliza la extracción de filtros y la configuración
    de autenticación JWT.
    """

    def get_filters(
        self,
        request,
    ):
        return build_publicaciones_report_filters(
            request
        )


# ============================================================
# DESCARGA EXCEL
# ============================================================

class ExportarPublicacionesExcelView(
    PublicacionesReporteBaseAPIView,
):
    """
    Genera y devuelve el archivo Excel de publicaciones.

    Endpoint:

        GET /reportes/publicaciones/excel/
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        filters = self.get_filters(
            request
        )

        return build_export_publicaciones_response(
            filters
        )


# ============================================================
# DESCARGA PDF
# ============================================================

class ExportarPublicacionesPdfView(
    PublicacionesReporteBaseAPIView,
):
    """
    Genera y devuelve el archivo PDF de publicaciones.

    Endpoint:

        GET /reportes/publicaciones/pdf/

    Utiliza los mismos filtros y el mismo queryset que la
    exportación Excel.
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        filters = self.get_filters(
            request
        )

        return build_export_publicaciones_pdf_response(
            filters
        )


# ============================================================
# VISTA PREVIA
# ============================================================

class VistaPreviaPublicacionesExcelView(
    PublicacionesReporteBaseAPIView,
):
    """
    Devuelve la cantidad exacta de publicaciones que contendría
    el archivo Excel con los filtros enviados.

    Endpoint previsto:

        GET /reportes/publicaciones/excel/preview/

    Respuesta:

        {
            "total": 18
        }
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        filters = self.get_filters(
            request
        )

        preview = build_export_publicaciones_preview(
            filters
        )

        return Response(
            preview
        )