"""
Views de reportes para exportación de publicaciones.

Permite descargar el reporte Excel aplicando los mismos
filtros utilizados por los listados y dashboards del SGPC.
"""

from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.reportes.services.reportes_publicaciones_services import (
    build_export_publicaciones_response,
)


def _first_query_param(
    query_params,
    *names,
    default="",
):
    """
    Obtiene el primer query parameter que contenga
    un valor no vacío.

    Permite conservar compatibilidad entre nombres
    antiguos y nuevos de los filtros.
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


class ExportarPublicacionesExcelView(
    APIView
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def _build_filters(
        self,
        request,
    ):
        params = (
            request.query_params
        )

        return {
            # -------------------------------------------------
            # Tipo de publicación
            # -------------------------------------------------

            "tipo": _first_query_param(
                params,
                "tipo",
                "tipo_publicacion_final",
            ),

            # -------------------------------------------------
            # Año
            # -------------------------------------------------

            "anio": _first_query_param(
                params,
                "anio",
            ),

            "anio_desde": (
                _first_query_param(
                    params,
                    "anio_desde",
                )
            ),

            "anio_hasta": (
                _first_query_param(
                    params,
                    "anio_hasta",
                )
            ),

            # -------------------------------------------------
            # Búsqueda textual
            # -------------------------------------------------

            "texto": _first_query_param(
                params,
                "texto",
                "q",
            ),

            # -------------------------------------------------
            # Facultad
            # -------------------------------------------------

            "facultad": (
                _first_query_param(
                    params,
                    "facultad",
                    "facultad_id",
                )
            ),

            # -------------------------------------------------
            # Carrera
            # -------------------------------------------------

            "carrera": (
                _first_query_param(
                    params,
                    "carrera",
                    "carrera_id",
                )
            ),

            # -------------------------------------------------
            # Proyecto
            # -------------------------------------------------

            "proyecto": (
                _first_query_param(
                    params,
                    "proyecto",
                    "proyecto_id",
                )
            ),

            # -------------------------------------------------
            # PDF
            # -------------------------------------------------

            "solo_con_pdf": (
                _first_query_param(
                    params,
                    "solo_con_pdf",
                    default="",
                )
            ),
        }

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        filters = self._build_filters(
            request
        )

        return (
            build_export_publicaciones_response(
                filters
            )
        )