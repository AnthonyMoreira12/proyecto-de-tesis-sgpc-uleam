"""
Views de selects académicos y geográficos para formularios del sistema.

Qué hace:
- Devuelve listados ligeros para poblar selects dependientes.
- Reutiliza selectors para evitar duplicación con el ViewSet de selects.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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
)


class AuthenticatedSelectAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class FacultadesSelect(AuthenticatedSelectAPIView):
    def get(self, request):
        return Response(build_facultades_select_data())


class CarrerasByFacultadSelect(AuthenticatedSelectAPIView):
    def get(self, request, fid):
        return Response(
            build_carreras_select_data(
                facultad_id=fid,
            )
        )


class ProyectosByCarreraSelect(AuthenticatedSelectAPIView):
    def get(self, request, cid):
        include_id = request.query_params.get("include")
        q = request.query_params.get("q", "")

        return Response(
            build_proyectos_select_data(
                carrera_id=cid,
                include_id=include_id,
                q=q,
                incluir_cerrados=_is_admin_user(request.user),
            )
        )


class PaisesSelect(AuthenticatedSelectAPIView):
    def get(self, request):
        return Response(build_paises_select_data())


class CiudadesByPaisSelect(AuthenticatedSelectAPIView):
    def get(self, request, pid):
        return Response(
            build_ciudades_select_data(
                pais_id=pid,
            )
        )


class AreasSelect(AuthenticatedSelectAPIView):
    def get(self, request):
        return Response(build_areas_select_data())


class SubareasByAreaSelect(AuthenticatedSelectAPIView):
    def get(self, request, aid):
        return Response(
            build_subareas_select_data(
                area_id=aid,
            )
        )