"""
Vista para consultar el listado institucional de publicaciones.

La construcción del queryset, la validación de parámetros,
los filtros, la búsqueda y el ordenamiento se delegan al
servicio centralizado de listados.

Endpoint:

    GET /publicaciones/

Filtros admitidos:

    tipo
    origen_tipo
    anio
    anio_desde
    anio_hasta
    texto
    facultad
    carrera
    proyecto
    orden
    solo_con_pdf
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)
from core.publicaciones.services.publicaciones_listado_services import (
    build_publicaciones_queryset,
    extract_publicaciones_filters,
    get_publicaciones_available_years,
)


class PublicacionListAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    Devuelve publicaciones institucionales aplicando los
    criterios recibidos mediante query parameters.

    La vista no contiene reglas propias de filtrado. Esto evita
    diferencias entre el listado institucional, Mis publicaciones
    y la exportación Excel.
    """

    def get(
        self,
        request,
    ):
        # =====================================================
        # 1. VALIDAR Y NORMALIZAR FILTROS
        # =====================================================

        filters = extract_publicaciones_filters(
            request.query_params
        )

        # =====================================================
        # 2. CONSTRUIR QUERYSET INSTITUCIONAL
        # =====================================================

        publicaciones = build_publicaciones_queryset(
            filters=filters,
            user=request.user,
            solo_mias=False,
        )

        # =====================================================
        # 3. SERIALIZAR RESPUESTA
        # =====================================================

        serializer = PublicacionListadoSerializer(
            publicaciones,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data
        )


class PublicacionAvailableYearsAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    Devuelve los años existentes en el listado institucional.

    Los filtros no temporales recibidos en la URL se conservan.
    Los parámetros anio, anio_desde y anio_hasta se ignoran para
    impedir que el catálogo quede limitado por su propia selección.

    Endpoint:

        GET /publicaciones/anios-disponibles/
    """

    def get(
        self,
        request,
    ):
        filters = extract_publicaciones_filters(
            request.query_params
        )

        anios = get_publicaciones_available_years(
            filters=filters,
            user=request.user,
            solo_mias=False,
        )

        return Response(
            {
                "anios": anios,
            }
        )