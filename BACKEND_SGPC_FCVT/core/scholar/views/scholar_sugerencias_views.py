"""
View pública de sugerencias rápidas para la búsqueda
de investigadores tipo Scholar.

Permite localizar autores mediante:

- nombres y apellidos;
- correo;
- identificación;
- institución;
- ORCID;
- Registro SENESCYT;
- Google Scholar;
- Scopus ID.

La respuesta conserva los aliases históricos:

- suggestions;
- results.
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
    """
    Sugerencias rápidas de perfiles Scholar.

    Este endpoint es público y devuelve como máximo
    MAX_RESULTS coincidencias.
    """

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

        # Evitamos consultas innecesarias con términos
        # demasiado cortos.
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
            )
            .distinct()
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
                )
                .strip()
            )

            if not label:
                label = (
                    str(
                        getattr(
                            author,
                            "correo",
                            "",
                        )
                        or ""
                    )
                    .strip()
                    or "Autor"
                )

            suggestions.append(
                {
                    "kind": "profile",
                    "id": author.id,
                    "label": label,
                }
            )

        # Se mantienen ambos aliases para no romper
        # las interfaces existentes.
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