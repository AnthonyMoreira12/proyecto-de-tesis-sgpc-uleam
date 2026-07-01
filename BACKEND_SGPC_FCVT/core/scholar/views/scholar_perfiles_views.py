"""
Views para perfiles tipo Scholar de autores.
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count, Value
from django.db.models.functions import Lower
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Autor
from core.scholar.services.scholar_perfiles_services import (
    build_fullname_expression,
    build_public_profile_payload,
    get_author_org_label,
    get_user_avatar_absolute_url,
)


def _parse_page_size(value, default=10, maximum=50):
    try:
        value = int(value or default)
    except Exception:
        value = default

    return max(1, min(maximum, value))


class PerfilesScholarAPIView(APIView):
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        page_size = _parse_page_size(request.query_params.get("page_size"), default=10)

        fullname = build_fullname_expression()

        qs = (
            Autor.objects
            .select_related("usuario")
            .annotate(fullname=fullname)
            .annotate(publications=Count("publicaciones", distinct=True))
        )

        paginator = PageNumberPagination()
        paginator.page_size = page_size

        if not q:
            qs = qs.order_by("apellidos", "nombres", "id")
            page = paginator.paginate_queryset(qs, request)

            results = []
            for author in page:
                user = getattr(author, "usuario", None)
                name = (
                    (getattr(author, "fullname", "") or "").strip()
                    or f"{author.nombres or ''} {author.apellidos or ''}".strip()
                    or "—"
                )

                results.append(
                    {
                        "id": author.id,
                        "name": name,
                        "org": get_author_org_label(author),
                        "avatar": get_user_avatar_absolute_url(request, user),
                        "verified": None,
                        "citedBy": 0,
                        "tags": [],
                        "sim": 0.0,
                        "es_externo": bool(getattr(author, "es_externo", False)),
                        "nombres": author.nombres or "",
                        "apellidos": author.apellidos or "",
                        "publications": int(getattr(author, "publications", 0) or 0),
                    }
                )

            return paginator.get_paginated_response(results)

        q_norm = q.lower()
        qs = qs.annotate(
            sim=TrigramSimilarity(Lower("fullname"), Lower(Value(q_norm)))
        )
        qs = (qs.filter(fullname__icontains=q_norm) | qs.filter(sim__gte=0.2)).distinct()
        qs = qs.order_by("-sim", "apellidos", "nombres", "id")

        page = paginator.paginate_queryset(qs, request)

        results = []
        for author in page:
            user = getattr(author, "usuario", None)
            name = (
                (getattr(author, "fullname", "") or "").strip()
                or f"{author.nombres or ''} {author.apellidos or ''}".strip()
                or "—"
            )

            results.append(
                {
                    "id": author.id,
                    "name": name,
                    "org": get_author_org_label(author),
                    "avatar": get_user_avatar_absolute_url(request, user),
                    "verified": None,
                    "citedBy": 0,
                    "tags": [],
                    "sim": float(getattr(author, "sim", 0) or 0),
                    "es_externo": bool(getattr(author, "es_externo", False)),
                    "nombres": author.nombres or "",
                    "apellidos": author.apellidos or "",
                    "publications": int(getattr(author, "publications", 0) or 0),
                }
            )

        return paginator.get_paginated_response(results)


class PerfilScholarDetailAPIView(APIView):
    def get(self, request, id: int):
        author = Autor.objects.select_related("usuario").filter(id=id).first()
        if not author:
            return Response(
                {"detail": "No encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = build_public_profile_payload(
            request=request,
            author=author,
            is_me=False,
        )
        return Response(payload, status=status.HTTP_200_OK)


class PerfilScholarMeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        author = (
            Autor.objects
            .select_related("usuario")
            .filter(usuario=request.user)
            .first()
        )

        if not author:
            return Response(
                {"detail": "No existe un perfil de autor asociado a tu cuenta."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = build_public_profile_payload(
            request=request,
            author=author,
            is_me=True,
        )
        return Response(payload, status=status.HTTP_200_OK)