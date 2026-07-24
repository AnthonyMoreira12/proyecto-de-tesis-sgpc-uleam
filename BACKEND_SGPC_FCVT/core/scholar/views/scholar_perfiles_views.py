"""
Views para perfiles tipo Scholar de autores.

Endpoints públicos:
- listado/búsqueda de investigadores;
- detalle de perfil.

Endpoint autenticado:
- perfil Scholar del usuario actual.
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count, Q, Value
from django.db.models.functions import Lower
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Autor
from core.scholar.serializers.scholar_perfiles_serializers import (
    PerfilAutorListSerializer,
)
from core.scholar.services.scholar_perfiles_services import (
    build_fullname_expression,
    build_public_profile_payload,
)


# =============================================================
# HELPERS
# =============================================================


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


def _build_author_payload(
    *,
    request,
    author,
):
    """
    Usa el serializer base y conserva los campos
    adicionales que ya expone la API Scholar.
    """

    base = PerfilAutorListSerializer(
        author,
        context={
            "request": request,
        },
    ).data

    return {
        **base,

        "verified": None,
        "citedBy": 0,
        "tags": [],

        "sim": float(
            getattr(
                author,
                "sim",
                0,
            )
            or 0
        ),

        "es_externo": bool(
            getattr(
                author,
                "es_externo",
                False,
            )
        ),

        "nombres": (
            getattr(
                author,
                "nombres",
                "",
            )
            or ""
        ),

        "apellidos": (
            getattr(
                author,
                "apellidos",
                "",
            )
            or ""
        ),
    }


# =============================================================
# LISTADO / BÚSQUEDA PÚBLICA
# =============================================================


class PerfilesScholarAPIView(
    APIView
):
    """
    Lista y busca investigadores.

    Este endpoint es público porque forma parte
    de la búsqueda académica institucional.
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

        page_size = _parse_page_size(
            request.query_params.get(
                "page_size"
            ),
            default=10,
        )

        fullname = (
            build_fullname_expression()
        )

        queryset = (
            Autor.objects
            .select_related(
                "usuario",
                "usuario__carrera",
                "usuario__carrera__facultad",
            )
            .annotate(
                fullname=fullname
            )
            .annotate(
                publications=Count(
                    "publicaciones",
                    distinct=True,
                )
            )
        )

        # -----------------------------------------------------
        # Sin búsqueda
        # -----------------------------------------------------

        if not q:
            queryset = (
                queryset.order_by(
                    "apellidos",
                    "nombres",
                    "id",
                )
            )

        # -----------------------------------------------------
        # Con búsqueda
        # -----------------------------------------------------

        else:
            q_norm = q.lower()

            queryset = (
                queryset.annotate(
                    sim=TrigramSimilarity(
                        Lower(
                            "fullname"
                        ),
                        Value(
                            q_norm
                        ),
                    )
                )
                .filter(
                    Q(
                        fullname__icontains=q
                    )
                    | Q(
                        correo__icontains=q
                    )
                    | Q(
                        identificacion__icontains=q
                    )
                    | Q(
                        institucion__icontains=q
                    )
                    | Q(
                        sim__gte=0.2
                    )
                )
                .distinct()
                .order_by(
                    "-sim",
                    "apellidos",
                    "nombres",
                    "id",
                )
            )

        # -----------------------------------------------------
        # Paginación
        # -----------------------------------------------------

        paginator = (
            PageNumberPagination()
        )

        paginator.page_size = (
            page_size
        )

        page = (
            paginator.paginate_queryset(
                queryset,
                request,
            )
        )

        results = [
            _build_author_payload(
                request=request,
                author=author,
            )
            for author in page
        ]

        return (
            paginator
            .get_paginated_response(
                results
            )
        )


# =============================================================
# PERFIL PÚBLICO
# =============================================================


class PerfilScholarDetailAPIView(
    APIView
):
    """
    Perfil público de un investigador.
    """

    authentication_classes = []
    permission_classes = [
        permissions.AllowAny
    ]

    def get(
        self,
        request,
        id: int,
    ):
        author = (
            Autor.objects
            .select_related(
                "usuario",
                "usuario__carrera",
                "usuario__carrera__facultad",
            )
            .filter(
                id=id
            )
            .first()
        )

        if not author:
            return Response(
                {
                    "detail": (
                        "Perfil de autor "
                        "no encontrado."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        payload = (
            build_public_profile_payload(
                request=request,
                author=author,
                is_me=False,
            )
        )

        return Response(
            payload,
            status=status.HTTP_200_OK,
        )


# =============================================================
# MI PERFIL
# =============================================================


class PerfilScholarMeAPIView(
    APIView
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(
        self,
        request,
    ):
        author = (
            Autor.objects
            .select_related(
                "usuario",
                "usuario__carrera",
                "usuario__carrera__facultad",
            )
            .filter(
                usuario=request.user
            )
            .first()
        )

        if not author:
            return Response(
                {
                    "detail": (
                        "No existe un perfil "
                        "de autor asociado a tu cuenta."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        payload = (
            build_public_profile_payload(
                request=request,
                author=author,
                is_me=True,
            )
        )

        return Response(
            payload,
            status=status.HTTP_200_OK,
        )