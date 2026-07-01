"""
View para búsqueda tipo Scholar de publicaciones.
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import TextField, Value
from django.db.models.functions import Coalesce, Lower
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Publicacion, PublicacionAutor
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
    annotate_tipo_publicacion_final,
    tipo_publicacion_label,
)


def _parse_page_size(value, default=10, maximum=50):
    try:
        value = int(value or default)
    except Exception:
        value = default

    return max(1, min(maximum, value))


class PublicacionesScholarAPIView(APIView):
    def _apply_tipo_filter(self, qs, tipo: str):
        if not tipo:
            return qs

        tipo = str(tipo).strip().lower()

        if tipo.isdigit():
            return qs.filter(tipo_id=int(tipo))

        if tipo in TIPOS_PUBLICACION_FINALES:
            return qs.filter(tipo_publicacion_final=tipo)

        name_map = {
            "artículo de alto impacto": "articulo_alto_impacto",
            "articulo de alto impacto": "articulo_alto_impacto",
            "artículo regional": "articulo_regional",
            "articulo regional": "articulo_regional",
            "ponencia": "ponencia",
            "libro": "libro",
            "capítulo": "capitulo_libro",
            "capitulo": "capitulo_libro",
            "capítulo de libro": "capitulo_libro",
            "capitulo de libro": "capitulo_libro",
        }

        tipo_norm = name_map.get(tipo, tipo)
        if tipo_norm in TIPOS_PUBLICACION_FINALES:
            return qs.filter(tipo_publicacion_final=tipo_norm)

        return qs

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"count": 0, "results": []})

        q_norm = q.lower()
        tipo = (request.query_params.get("type") or "").strip()
        year = (request.query_params.get("year") or "").strip()

        title_expr = Coalesce(
            "articulo__nombre_articulo",
            "ponencia__nombre_ponencia",
            "libro__nombre_libro",
            "capitulo_libro__nombre_capitulo",
            Value(""),
            output_field=TextField(),
        )

        base = (
            Publicacion.objects
            .select_related("tipo", "articulo", "ponencia", "libro", "capitulo_libro")
            .annotate(titulo_busqueda=title_expr)
            .annotate(sim=TrigramSimilarity(Lower("titulo_busqueda"), Lower(Value(q_norm))))
        )

        base = annotate_tipo_publicacion_final(base).exclude(
            tipo_publicacion_final="sin_clasificar"
        )

        qs = (
            base.filter(titulo_busqueda__icontains=q_norm)
            | base.filter(sim__gte=0.2)
        ).distinct()

        qs = self._apply_tipo_filter(qs, tipo)

        if year.isdigit():
            qs = qs.filter(anio_publicacion=int(year))

        qs = qs.order_by("-sim", "-updated_at", "-id")

        paginator = PageNumberPagination()
        paginator.page_size = _parse_page_size(
            request.query_params.get("page_size"),
            default=10,
        )
        page = paginator.paginate_queryset(qs, request)

        results = []
        for pub in page:
            rels = (
                PublicacionAutor.objects
                .select_related("autor")
                .filter(publicacion_id=pub.id)
                .order_by("orden", "id")
            )

            authors = []
            for rel in rels:
                author = rel.autor
                if not author:
                    continue

                label = f"{author.nombres or ''} {author.apellidos or ''}".strip()
                authors.append(
                    {
                        "id": author.id,
                        "name": label or "—",
                    }
                )

            tipo_final = getattr(pub, "tipo_publicacion_final", "sin_clasificar")

            results.append(
                {
                    "id": pub.id,
                    "title": (pub.titulo_busqueda or "").strip() or "—",
                    "year": pub.anio_publicacion,
                    "tipo": pub.tipo.nombre if pub.tipo else None,
                    "tipo_codigo": pub.tipo.codigo if pub.tipo else None,
                    "tipo_publicacion_final": tipo_final,
                    "tipo_publicacion_final_label": tipo_publicacion_label(tipo_final),
                    "authors": authors,
                    "snippet": None,
                    "sim": float(pub.sim or 0),
                    "citedBy": 0,
                }
            )

        return paginator.get_paginated_response(results)