"""
Vistas HTTP para reportes de publicaciones.

Endpoints previstos:

- Descarga del archivo Excel:
    GET /reportes/publicaciones/excel/

- Vista previa del total:
    GET /reportes/publicaciones/excel/preview/

Las dos vistas:

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
    - la vista previa del conteo.

    La validación definitiva se realiza dentro del servicio
    centralizado de publicaciones.
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