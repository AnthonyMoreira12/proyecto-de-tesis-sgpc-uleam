"""
ViewSet de selects reutilizables para formularios del sistema.

Centraliza endpoints ligeros para consultar:

- Facultades.
- Carreras.
- Proyectos.
- Países.
- Ciudades.
- Áreas de conocimiento.
- Subáreas.
- Autores.

Todos los endpoints requieren autenticación JWT y permiten
únicamente operaciones de lectura.
"""

import logging

from django.db import DatabaseError

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.catalogos.selectors.catalogos_selects_selectors import (
    AUTOR_SELECT_LIMIT,
    _is_admin_user,
    build_areas_select_data,
    build_autores_select_data,
    build_carreras_select_data,
    build_ciudades_select_data,
    build_facultades_select_data,
    build_paises_select_data,
    build_proyectos_select_data,
    build_subareas_select_data,
)


logger = logging.getLogger(__name__)


class SelectsViewSet(ViewSet):
    """
    ViewSet de lectura para selects y autocompletados.

    Este ViewSet se utiliza mediante mapeos manuales en
    core/urls.py, por ejemplo:

        SelectsViewSet.as_view(
            {
                "get": "get_facultades",
            }
        )
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    http_method_names = [
        "get",
        "head",
        "options",
    ]

    # ========================================================
    # RESPUESTA FINAL
    # ========================================================

    def finalize_response(
        self,
        request,
        response,
        *args,
        **kwargs,
    ):
        """
        Evita que el navegador reutilice catálogos desactualizados.
        """
        response = super().finalize_response(
            request,
            response,
            *args,
            **kwargs,
        )

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "max-age=0, private"
        )
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

    # ========================================================
    # UTILIDADES
    # ========================================================

    def _catalog_response(
        self,
        builder,
        *,
        error_context,
        **builder_kwargs,
    ):
        """
        Ejecuta un selector y devuelve una respuesta controlada.

        Los errores de programación no se ocultan. Únicamente
        se controlan fallos temporales de la base de datos.
        """
        try:
            data = builder(
                **builder_kwargs
            )

        except DatabaseError:
            logger.exception(
                error_context
            )

            return Response(
                {
                    "detail": (
                        "El catálogo no está disponible "
                        "temporalmente. Intente nuevamente."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    def _get_first_query_parameter(
        self,
        request,
        aliases,
        *,
        default=None,
    ):
        """
        Obtiene el primer parámetro presente dentro de una lista
        de nombres alternativos.
        """
        for alias in aliases:
            if alias in request.query_params:
                return request.query_params.get(
                    alias
                )

        return default

    def _get_project_include_id(
        self,
        request,
    ):
        """
        Obtiene el proyecto que debe mantenerse visible.

        Alias admitidos:

        - include
        - include_id
        - proyecto_id
        """
        return self._get_first_query_parameter(
            request,
            (
                "include",
                "include_id",
                "proyecto_id",
            ),
            default=None,
        )

    def _get_author_limit(
        self,
        request,
    ):
        """
        Obtiene el límite solicitado para el autocompletado de
        autores.

        La validación definitiva se realiza en el selector.
        """
        return self._get_first_query_parameter(
            request,
            (
                "limit",
                "limite",
            ),
            default=AUTOR_SELECT_LIMIT,
        )

    # ========================================================
    # FACULTADES
    # ========================================================

    def get_facultades(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Devuelve todas las facultades.
        """
        return self._catalog_response(
            build_facultades_select_data,
            error_context=(
                "Error al consultar el select de facultades."
            ),
        )

    # ========================================================
    # CARRERAS
    # ========================================================

    def get_carreras(
        self,
        request,
        facultad_id=None,
        *args,
        **kwargs,
    ):
        """
        Devuelve las carreras correspondientes a una facultad.
        """
        return self._catalog_response(
            build_carreras_select_data,
            facultad_id=facultad_id,
            error_context=(
                "Error al consultar el select de carreras."
            ),
        )

    # ========================================================
    # PROYECTOS
    # ========================================================

    def get_proyectos(
        self,
        request,
        carrera_id=None,
        *args,
        **kwargs,
    ):
        """
        Devuelve los proyectos pertenecientes a una carrera.

        Parámetros opcionales:

        - q:
            Texto de búsqueda.

        - include, include_id o proyecto_id:
            Proyecto previamente seleccionado que debe seguir
            visible aunque se encuentre cerrado.
        """
        include_id = self._get_project_include_id(
            request
        )

        query = request.query_params.get(
            "q",
            "",
        )

        include_closed = _is_admin_user(
            request.user
        )

        return self._catalog_response(
            build_proyectos_select_data,
            carrera_id=carrera_id,
            include_id=include_id,
            q=query,
            incluir_cerrados=include_closed,
            error_context=(
                "Error al consultar el select de proyectos."
            ),
        )

    # ========================================================
    # PAÍSES
    # ========================================================

    def get_paises(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Devuelve el catálogo de países.
        """
        return self._catalog_response(
            build_paises_select_data,
            error_context=(
                "Error al consultar el select de países."
            ),
        )

    # ========================================================
    # CIUDADES
    # ========================================================

    def get_ciudades(
        self,
        request,
        pais_id=None,
        *args,
        **kwargs,
    ):
        """
        Devuelve las ciudades correspondientes a un país.
        """
        return self._catalog_response(
            build_ciudades_select_data,
            pais_id=pais_id,
            error_context=(
                "Error al consultar el select de ciudades."
            ),
        )

    # ========================================================
    # ÁREAS
    # ========================================================

    def get_areas(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Devuelve las áreas de conocimiento.
        """
        return self._catalog_response(
            build_areas_select_data,
            error_context=(
                "Error al consultar el select de áreas."
            ),
        )

    # ========================================================
    # SUBÁREAS
    # ========================================================

    def get_subareas(
        self,
        request,
        area_id=None,
        *args,
        **kwargs,
    ):
        """
        Devuelve las subáreas correspondientes a un área.
        """
        return self._catalog_response(
            build_subareas_select_data,
            area_id=area_id,
            error_context=(
                "Error al consultar el select de subáreas."
            ),
        )

    # ========================================================
    # AUTORES
    # ========================================================

    def get_autores(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Devuelve autores para selects y autocompletados.

        Parámetros opcionales:

        - q:
            Texto de búsqueda.

        - limit o limite:
            Cantidad máxima de autores. El selector restringe
            internamente el valor permitido.
        """
        query = request.query_params.get(
            "q",
            "",
        )

        limit = self._get_author_limit(
            request
        )

        return self._catalog_response(
            build_autores_select_data,
            q=query,
            limit=limit,
            error_context=(
                "Error al consultar el select de autores."
            ),
        )