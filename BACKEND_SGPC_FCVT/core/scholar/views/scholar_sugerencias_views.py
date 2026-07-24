"""
View pública de sugerencias rápidas para la
búsqueda de investigadores tipo Scholar.
"""

from django.db.models import (
    Q,
    TextField,
    Value,
)
from django.db.models.functions import (
    Coalesce,
    Concat,
)
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Autor


class ScholarSuggestAPIView(
    APIView
):
    authentication_classes = []

    permission_classes = [
        permissions.AllowAny
    ]

    MAX_RESULTS = 8

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

        # Evitamos consultas innecesarias con
        # términos demasiado cortos.
        if len(q) < 2:
            return Response(
                {
                    "suggestions": [],
                    "results": [],
                }
            )

        fullname = Concat(
            Coalesce(
                "nombres",
                Value(""),
            ),
            Value(" "),
            Coalesce(
                "apellidos",
                Value(""),
            ),
            output_field=TextField(),
        )

        queryset = (
            Autor.objects
            .annotate(
                fullname=fullname
            )
            .filter(
                Q(
                    fullname__icontains=q
                )
                | Q(
                    correo__icontains=q
                )
            )
            .order_by(
                "apellidos",
                "nombres",
                "id",
            )[
                : self.MAX_RESULTS
            ]
        )

        suggestions = []

        for author in queryset:
            label = (
                str(
                    getattr(
                        author,
                        "fullname",
                        "",
                    )
                    or ""
                ).strip()
            )

            if not label:
                label = (
                    str(
                        author.correo
                        or ""
                    ).strip()
                    or "Autor"
                )

            suggestions.append(
                {
                    "kind": "profile",
                    "id": author.id,
                    "label": label,
                }
            )

        # Conservamos ambos aliases porque el frontend
        # puede utilizar suggestions o results.
        return Response(
            {
                "suggestions": (
                    suggestions
                ),
                "results": (
                    suggestions
                ),
            }
        )