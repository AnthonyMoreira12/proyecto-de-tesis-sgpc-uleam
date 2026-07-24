"""
Vista principal de búsqueda académica.

Permite buscar simultáneamente:

- Investigadores.
- Proyectos.
- Publicaciones.
- Autores.

La búsqueda es pública y únicamente utiliza operaciones de
lectura. Los parámetros recibidos se validan antes de ejecutar
consultas en PostgreSQL.
"""

import unicodedata

from django.db import DatabaseError

from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.busqueda.selectors.busqueda_general_selectors import (
    MAX_SEARCH_LIMIT,
    MAX_SEARCH_QUERY_LENGTH,
    SEARCH_LIMIT,
    buscar_autores,
    buscar_proyectos,
    buscar_publicaciones,
    buscar_usuarios,
)
from core.busqueda.serializers.busqueda_autor_serializers import (
    AutorBusquedaSerializer,
)
from core.busqueda.serializers.busqueda_proyecto_serializers import (
    ProyectoBusquedaSerializer,
)
from core.busqueda.serializers.busqueda_publicacion_serializers import (
    PublicacionBusquedaSerializer,
)
from core.busqueda.serializers.busqueda_usuario_serializers import (
    UsuarioBusquedaSerializer,
)


# ============================================================
# SERIALIZER DE PARÁMETROS
# ============================================================

class BusquedaGeneralQuerySerializer(
    serializers.Serializer
):
    """
    Valida los parámetros de la búsqueda general.
    """

    q = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=MAX_SEARCH_QUERY_LENGTH,
        default="",
        error_messages={
            "max_length": (
                "El término de búsqueda no puede superar "
                f"los {MAX_SEARCH_QUERY_LENGTH} caracteres."
            ),
        },
    )

    limit = serializers.IntegerField(
        required=False,
        default=SEARCH_LIMIT,
        min_value=1,
        max_value=MAX_SEARCH_LIMIT,
        error_messages={
            "invalid": (
                "El límite debe ser un número entero."
            ),
            "min_value": (
                "El límite debe ser mayor que cero."
            ),
            "max_value": (
                "El límite no puede superar "
                f"{MAX_SEARCH_LIMIT} resultados por sección."
            ),
        },
    )

    solo_con_pdf = serializers.BooleanField(
        required=False,
        default=False,
        error_messages={
            "invalid": (
                "El filtro de PDF debe ser verdadero "
                "o falso."
            ),
        },
    )

    def validate_q(
        self,
        value,
    ):
        """
        Normaliza Unicode y elimina espacios repetidos.
        """
        normalized_query = unicodedata.normalize(
            "NFKC",
            str(value or ""),
        )

        normalized_query = " ".join(
            normalized_query.split()
        )

        if (
            len(normalized_query)
            > MAX_SEARCH_QUERY_LENGTH
        ):
            raise serializers.ValidationError(
                (
                    "El término de búsqueda no puede superar "
                    f"los {MAX_SEARCH_QUERY_LENGTH} caracteres."
                )
            )

        return normalized_query


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_boolean_alias(value):
    """
    Convierte los formatos booleanos utilizados por el frontend.

    Valores verdaderos admitidos:

    - 1
    - true
    - t
    - yes
    - y
    - si
    - sí
    - on

    Valores falsos admitidos:

    - 0
    - false
    - f
    - no
    - n
    - off
    """
    if isinstance(
        value,
        bool,
    ):
        return value

    if value in (
        None,
        "",
    ):
        return False

    normalized = str(
        value
    ).strip().lower()

    true_values = {
        "1",
        "true",
        "t",
        "yes",
        "y",
        "si",
        "sí",
        "on",
    }

    false_values = {
        "0",
        "false",
        "f",
        "no",
        "n",
        "off",
    }

    if normalized in true_values:
        return True

    if normalized in false_values:
        return False

    return value


def _get_pdf_filter_value(request):
    """
    Obtiene el filtro de PDF utilizando cualquiera de los alias
    admitidos por el frontend.
    """
    aliases = (
        "solo_con_pdf",
        "solo_pdf",
        "con_pdf",
        "has_pdf",
    )

    for alias in aliases:
        if alias in request.query_params:
            return _normalize_boolean_alias(
                request.query_params.get(
                    alias
                )
            )

    return False


def _empty_search_payload():
    """
    Devuelve la estructura estable utilizada por el frontend.
    """
    return {
        "usuarios": [],
        "proyectos": [],
        "publicaciones": [],
        "autores": [],
    }


def _no_store_response(
    payload,
    *,
    status_code=status.HTTP_200_OK,
):
    """
    Construye una respuesta que no debe almacenarse en caché.
    """
    response = Response(
        payload,
        status=status_code,
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0"
    )

    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


# ============================================================
# VISTA
# ============================================================

class BusquedaGeneralAPIView(APIView):
    """
    Endpoint público de búsqueda académica general.

    Ejemplo:

        GET /api/busqueda/?q=inteligencia&limit=8

    Filtro opcional:

        GET /api/busqueda/?q=software&has_pdf=true
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(
        self,
        request,
    ):
        """
        Valida los parámetros y ejecuta los cuatro selectores.
        """
        query_data = {
            "q": request.query_params.get(
                "q",
                "",
            ),
            "limit": request.query_params.get(
                "limit",
                SEARCH_LIMIT,
            ),
            "solo_con_pdf": (
                _get_pdf_filter_value(
                    request
                )
            ),
        }

        query_serializer = (
            BusquedaGeneralQuerySerializer(
                data=query_data,
                context={
                    "request": request,
                },
            )
        )

        if not query_serializer.is_valid():
            return _no_store_response(
                query_serializer.errors,
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        query = query_serializer.validated_data[
            "q"
        ]

        limit = query_serializer.validated_data[
            "limit"
        ]

        only_with_pdf = (
            query_serializer.validated_data[
                "solo_con_pdf"
            ]
        )

        if not query:
            return _no_store_response(
                _empty_search_payload(),
                status_code=status.HTTP_200_OK,
            )

        try:
            users = buscar_usuarios(
                query,
                limit=limit,
            )

            projects = buscar_proyectos(
                query,
                limit=limit,
            )

            publications = buscar_publicaciones(
                query,
                limit=limit,
                solo_con_pdf=only_with_pdf,
            )

            authors = buscar_autores(
                query,
                limit=limit,
            )

            serializer_context = {
                "request": request,
            }

            payload = {
                "usuarios": (
                    UsuarioBusquedaSerializer(
                        users,
                        many=True,
                        context=serializer_context,
                    ).data
                ),

                "proyectos": (
                    ProyectoBusquedaSerializer(
                        projects,
                        many=True,
                        context=serializer_context,
                    ).data
                ),

                "publicaciones": (
                    PublicacionBusquedaSerializer(
                        publications,
                        many=True,
                        context=serializer_context,
                    ).data
                ),

                "autores": (
                    AutorBusquedaSerializer(
                        authors,
                        many=True,
                        context=serializer_context,
                    ).data
                ),
            }

        except DatabaseError:
            return _no_store_response(
                {
                    "detail": (
                        "La búsqueda no está disponible "
                        "temporalmente debido a un error "
                        "de la base de datos."
                    )
                },
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return _no_store_response(
            payload,
            status_code=status.HTTP_200_OK,
        )