"""
Vista para consultar las publicaciones vinculadas al usuario
autenticado.

Incluye:

- publicaciones creadas por el usuario;
- publicaciones donde participa como autor principal;
- publicaciones donde participa como coautor;
- filtros, búsqueda y ordenamiento centralizados.

Endpoints:

    GET /publicaciones/mias/
    GET /publicaciones/mias/anios-disponibles/

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


class MyPublicacionListAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    Devuelve las publicaciones relacionadas con el usuario
    autenticado.

    El alcance de usuario, los filtros, la búsqueda textual y
    el ordenamiento son responsabilidad del servicio centralizado.
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
        # 2. CONSTRUIR QUERYSET DEL USUARIO
        # =====================================================

        publicaciones = build_publicaciones_queryset(
            filters=filters,
            user=request.user,
            solo_mias=True,
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


class MyPublicacionAvailableYearsAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    Devuelve únicamente los años de las publicaciones relacionadas
    con el usuario autenticado.

    Conserva los filtros no temporales y elimina los filtros de año
    antes de construir el catálogo, evitando que el selector se
    reduzca al año que el usuario ya eligió.

    Endpoint:

        GET /publicaciones/mias/anios-disponibles/
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
            solo_mias=True,
        )

        return Response(
            {
                "anios": anios,
            }
        )