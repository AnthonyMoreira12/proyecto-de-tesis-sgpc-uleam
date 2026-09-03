"""
Views para perfiles tipo Scholar de autores.

Endpoints públicos:

- listado/búsqueda de investigadores;
- detalle de perfil.

Endpoint autenticado:

- perfil Scholar del usuario actual;
- actualización de sus identificadores académicos.

Los identificadores académicos pertenecen al modelo Autor:

- ORCID;
- Registro SENESCYT;
- Google Scholar;
- Scopus ID.
"""

from django.contrib.postgres.search import (
    TrigramSimilarity,
)
from django.db.models import (
    Count,
    Q,
    Value,
)
from django.db.models.functions import (
    Lower,
)
from rest_framework import (
    permissions,
    status,
)
from rest_framework.pagination import (
    PageNumberPagination,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import Autor
from core.scholar.serializers.scholar_perfiles_serializers import (
    PerfilAcademicoAutorSerializer,
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
    Usa el serializer compacto y conserva los campos adicionales
    que ya expone la API Scholar.

    Los identificadores académicos no se incluyen en las tarjetas
    del listado; se muestran en el detalle del perfil.
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


def _get_author_by_user(
    user,
):
    """
    Obtiene el Autor asociado al usuario autenticado.
    """

    return (
        Autor.objects
        .select_related(
            "usuario",
            "usuario__sede",
            "usuario__carrera",
            "usuario__carrera__facultad",
        )
        .filter(
            usuario=user
        )
        .first()
    )


def _autor_not_found_response():
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


# =============================================================
# LISTADO / BÚSQUEDA PÚBLICA
# =============================================================


class PerfilesScholarAPIView(
    APIView
):
    """
    Lista y busca investigadores.

    El endpoint es público porque forma parte de la búsqueda
    académica institucional.

    La búsqueda contempla:

    - nombres y apellidos;
    - correo;
    - identificación;
    - institución;
    - ORCID;
    - Registro SENESCYT;
    - URL de Google Scholar;
    - Scopus ID.
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
                "usuario__sede",
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
        # SIN BÚSQUEDA
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
        # CON BÚSQUEDA
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
                        orcid__icontains=q
                    )
                    | Q(
                        registro_senescyt__icontains=q
                    )
                    | Q(
                        google_scholar__icontains=q
                    )
                    | Q(
                        scopus_id__icontains=q
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
        # PAGINACIÓN
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
                "usuario__sede",
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
    """
    Perfil Scholar del usuario autenticado.

    GET
        Consulta el perfil académico.

    PATCH
        Actualiza parcialmente los identificadores académicos.

    PUT
        Mantiene compatibilidad con clientes que utilicen PUT.
        Como los cuatro identificadores son opcionales, se procesa
        de forma parcial para no borrar datos no enviados.

    Los campos editables son exclusivamente:

        orcid
        registro_senescyt
        google_scholar
        scopus_id

    No se modifica el modelo Usuario ni su perfil_completo.
    """

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
        author = _get_author_by_user(
            request.user
        )

        if not author:
            return (
                _autor_not_found_response()
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

    def _update_academic_profile(
        self,
        request,
    ):
        author = _get_author_by_user(
            request.user
        )

        if not author:
            return (
                _autor_not_found_response()
            )

        serializer = (
            PerfilAcademicoAutorSerializer(
                author,
                data=request.data,
                partial=True,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        # Se vuelve a construir el perfil completo para que la
        # respuesta tenga exactamente el mismo contrato que GET.
        author = _get_author_by_user(
            request.user
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

    def patch(
        self,
        request,
    ):
        return (
            self._update_academic_profile(
                request
            )
        )

    def put(
        self,
        request,
    ):
        return (
            self._update_academic_profile(
                request
            )
        )