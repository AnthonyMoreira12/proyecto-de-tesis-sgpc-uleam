
"""
View pública de búsqueda académica de publicaciones.

La lógica de consulta está centralizada en:

    core.scholar.services.scholar_publicaciones_services

La vista únicamente:

- recibe parámetros HTTP;
- evita consultas cuando no hay término de búsqueda;
- aplica paginación;
- serializa mediante el servicio;
- adjunta facetas cuando son solicitadas.
"""

from rest_framework import permissions
from rest_framework.pagination import (
    PageNumberPagination,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from core.scholar.services.scholar_publicaciones_services import (
    PublicacionesScholarServicio,
)


def _parse_page_size(
    value,
    default=10,
    maximum=50,
):
    try:
        value = int(
            value or default
        )

    except (
        TypeError,
        ValueError,
    ):
        value = default

    return max(
        1,
        min(
            maximum,
            value,
        ),
    )


class PublicacionesScholarAPIView(
    APIView
):
    """
    Búsqueda pública de publicaciones Scholar.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny
    ]

    def get(
        self,
        request,
    ):
        q = (
            request.query_params
            .get(
                "q",
                "",
            )
            .strip()
        )

        # Se conserva el comportamiento actual de la interfaz:
        # sin término de búsqueda no se recupera todo el catálogo.
        if not q:
            return Response(
                {
                    "count": 0,
                    "total": 0,
                    "next": None,
                    "previous": None,
                    "results": [],
                    "facets": {
                        "years": [],
                        "types": [],
                        "months": [],
                    },
                }
            )

        params = {
            key: request.query_params.get(
                key
            )
            for key
            in request.query_params.keys()
        }

        queryset, metadata = (
            PublicacionesScholarServicio
            .construir_queryset(
                params
            )
        )

        paginator = (
            PageNumberPagination()
        )

        paginator.page_size = (
            _parse_page_size(
                request.query_params.get(
                    "page_size"
                ),
                default=10,
            )
        )

        page = (
            paginator.paginate_queryset(
                queryset,
                request,
            )
        )

        results = [
            PublicacionesScholarServicio
            .serializar_publicacion(
                request=request,
                publication=publication,
            )
            for publication in page
        ]

        response = (
            paginator
            .get_paginated_response(
                results
            )
        )

        # Alias que ya utiliza el servicio y otras interfaces.
        response.data[
            "total"
        ] = response.data[
            "count"
        ]

        facets = str(
            request.query_params.get(
                "facets",
                "1",
            )
            or "1"
        ).strip()

        if facets == "1":
            response.data[
                "facets"
            ] = (
                PublicacionesScholarServicio
                .construir_facetas(
                    metadata=metadata
                )
            )

        return response