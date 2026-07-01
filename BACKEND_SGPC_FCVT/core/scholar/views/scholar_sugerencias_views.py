"""
View de sugerencias rápidas para búsqueda de autores tipo Scholar.
"""

from django.db.models import TextField, Value
from django.db.models.functions import Coalesce, Concat
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Autor


class ScholarSuggestAPIView(APIView):
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response({"suggestions": [], "results": []})

        fullname = Concat(
            Coalesce("nombres", Value("")),
            Value(" "),
            Coalesce("apellidos", Value("")),
            output_field=TextField(),
        )

        qs = (
            Autor.objects
            .annotate(fullname=fullname)
            .filter(fullname__icontains=q)
            .order_by("apellidos", "nombres", "id")[:8]
        )

        suggestions = [
            {
                "kind": "profile",
                "id": author.id,
                "label": (getattr(author, "fullname", "") or "").strip() or "—",
            }
            for author in qs
        ]

        return Response(
            {
                "suggestions": suggestions,
                "results": suggestions,
            }
        )