"""
APIViews de catálogos académicos y geográficos.

Este módulo expone listados ligeros para poblar selects
dependientes en los formularios del sistema:

- Facultades.
- Carreras por facultad.
- Proyectos por carrera.
- Países.
- Ciudades por país.
- Áreas de conocimiento.
- Subáreas por área.

Todos los endpoints requieren autenticación JWT y únicamente
permiten operaciones de lectura.
"""

import logging

from django.db import DatabaseError

from rest_framework import (
    status,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.catalogos.selectors.catalogos_selects_selectors import (
    _is_admin_user,
    build_areas_select_data,
    build_carreras_select_data,
    build_ciudades_select_data,
    build_facultades_select_data,
    build_paises_select_data,
    build_proyectos_select_data,
    build_subareas_select_data,
)


logger = logging.getLogger(__name__)


# ============================================================
# VISTA BASE
# ============================================================

class AuthenticatedSelectAPIView(APIView):
    """
    Clase base para endpoints autenticados de catálogos.

    Los catálogos deben representar siempre el estado actual de
    la base de datos, por lo que las respuestas no se almacenan
    en caché.
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

    def finalize_response(
        self,
        request,
        response,
        *args,
        **kwargs,
    ):
        """
        Aplica encabezados comunes a todas las respuestas.
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

    def catalog_response(
        self,
        builder,
        *,
        error_detail=(
            "No fue posible consultar el catálogo."
        ),
        **builder_kwargs,
    ):
        """
        Ejecuta un selector y devuelve una respuesta controlada.

        Solo captura errores de base de datos. Los errores de
        programación deben seguir siendo visibles durante el
        desarrollo.
        """
        try:
            data = builder(
                **builder_kwargs
            )

        except DatabaseError:
            logger.exception(
                error_detail
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


# ============================================================
# FACULTADES
# ============================================================

class FacultadesSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve todas las facultades ordenadas alfabéticamente.
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self.catalog_response(
            build_facultades_select_data,
            error_detail=(
                "Error al consultar el catálogo de facultades."
            ),
        )


# ============================================================
# CARRERAS
# ============================================================

class CarrerasByFacultadSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve las carreras pertenecientes a una facultad.
    """

    def get(
        self,
        request,
        fid,
        *args,
        **kwargs,
    ):
        return self.catalog_response(
            build_carreras_select_data,
            facultad_id=fid,
            error_detail=(
                "Error al consultar las carreras "
                "de una facultad."
            ),
        )


# ============================================================
# PROYECTOS
# ============================================================

class ProyectosByCarreraSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve los proyectos asociados a una carrera.

    Parámetros opcionales:

    - q:
        Texto de búsqueda.

    - include / include_id / proyecto_id:
        Proyecto que debe permanecer visible aunque esté cerrado.

    Los administradores pueden visualizar proyectos en estado
    cierre. Los usuarios académicos únicamente visualizan
    proyectos nuevos o de arrastre, salvo el proyecto incluido.
    """

    def _get_include_id(
        self,
        request,
    ):
        """
        Resuelve los alias admitidos para el proyecto incluido.
        """
        aliases = (
            "include",
            "include_id",
            "proyecto_id",
        )

        for alias in aliases:
            if alias in request.query_params:
                return request.query_params.get(
                    alias
                )

        return None

    def get(
        self,
        request,
        cid,
        *args,
        **kwargs,
    ):
        include_id = self._get_include_id(
            request
        )

        query = request.query_params.get(
            "q",
            "",
        )

        return self.catalog_response(
            build_proyectos_select_data,
            carrera_id=cid,
            include_id=include_id,
            q=query,
            incluir_cerrados=_is_admin_user(
                request.user
            ),
            error_detail=(
                "Error al consultar los proyectos "
                "de una carrera."
            ),
        )


# ============================================================
# PAÍSES
# ============================================================

class PaisesSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve el catálogo de países.
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self.catalog_response(
            build_paises_select_data,
            error_detail=(
                "Error al consultar el catálogo de países."
            ),
        )


# ============================================================
# CIUDADES
# ============================================================

class CiudadesByPaisSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve las ciudades pertenecientes a un país.
    """

    def get(
        self,
        request,
        pid,
        *args,
        **kwargs,
    ):
        return self.catalog_response(
            build_ciudades_select_data,
            pais_id=pid,
            error_detail=(
                "Error al consultar las ciudades "
                "de un país."
            ),
        )


# ============================================================
# ÁREAS
# ============================================================

class AreasSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve las áreas de conocimiento.
    """

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self.catalog_response(
            build_areas_select_data,
            error_detail=(
                "Error al consultar las áreas "
                "de conocimiento."
            ),
        )


# ============================================================
# SUBÁREAS
# ============================================================

class SubareasByAreaSelect(
    AuthenticatedSelectAPIView
):
    """
    Devuelve las subáreas pertenecientes a un área.
    """

    def get(
        self,
        request,
        aid,
        *args,
        **kwargs,
    ):
        return self.catalog_response(
            build_subareas_select_data,
            area_id=aid,
            error_detail=(
                "Error al consultar las subáreas "
                "de conocimiento."
            ),
        )