"""
ViewSet de selects reutilizables para formularios del sistema.

Qué hace:
- Centraliza endpoints ligeros para poblar selects y autocompletados.
- Devuelve catálogos académicos, geográficos y autores.
- Reutiliza selectors para que la lógica no quede duplicada.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.catalogos.selectors.catalogos_selects_selectors import (
    _is_admin_user,
    build_facultades_select_data,
    build_carreras_select_data,
    build_proyectos_select_data,
    build_paises_select_data,
    build_ciudades_select_data,
    build_areas_select_data,
    build_subareas_select_data,
    build_autores_select_data,
)


class SelectsViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_facultades(self, request):
        return Response(build_facultades_select_data())

    def get_carreras(self, request, facultad_id=None, *args, **kwargs):
        return Response(
            build_carreras_select_data(
                facultad_id=facultad_id,
            )
        )

    def get_proyectos(self, request, carrera_id=None, *args, **kwargs):
        include_id = request.query_params.get("include")
        q = request.query_params.get("q", "")

        return Response(
            build_proyectos_select_data(
                carrera_id=carrera_id,
                include_id=include_id,
                q=q,
                incluir_cerrados=_is_admin_user(request.user),
            )
        )

    def get_paises(self, request):
        return Response(build_paises_select_data())

    def get_ciudades(self, request, pais_id=None, *args, **kwargs):
        return Response(
            build_ciudades_select_data(
                pais_id=pais_id,
            )
        )

    def get_areas(self, request):
        return Response(build_areas_select_data())

    def get_subareas(self, request, area_id=None, *args, **kwargs):
        return Response(
            build_subareas_select_data(
                area_id=area_id,
            )
        )

    def get_autores(self, request):
        q = request.query_params.get("q", "")

        return Response(
            build_autores_select_data(
                q=q,
            )
        )