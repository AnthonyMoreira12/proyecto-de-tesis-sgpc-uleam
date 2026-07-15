"""
View para búsqueda tipo Scholar de publicaciones.
"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Exists, OuterRef, Q, TextField, Value
from django.db.models.functions import Coalesce, Lower
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Publicacion, PublicacionArchivo, PublicacionAutor
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


def _is_truthy(value):
    return str(value or "").strip().lower() in {
        "1",
        "true",
        "t",
        "yes",
        "y",
        "si",
        "sí",
        "on",
    }


def _build_absolute_url(request, file_field):
    try:
        if not file_field:
            return None
        url = file_field.url
    except Exception:
        return None

    if request:
        try:
            return request.build_absolute_uri(url)
        except Exception:
            return url

    return url


def _get_pdf_file(pub):
    archivo_pdf = getattr(pub, "archivo_pdf", None)

    if archivo_pdf and getattr(archivo_pdf, "name", None):
        return archivo_pdf

    prefetched = getattr(pub, "_prefetched_objects_cache", {})

    if "archivos" in prefetched:
        for adjunto in prefetched["archivos"]:
            archivo = getattr(adjunto, "archivo", None)
            if archivo and getattr(archivo, "name", None):
                return archivo
        return None

    try:
        adjunto = (
            pub.archivos.filter(archivo__isnull=False)
            .exclude(archivo="")
            .order_by("orden", "id")
            .first()
        )
    except Exception:
        return None

    if adjunto and adjunto.archivo and getattr(adjunto.archivo, "name", None):
        return adjunto.archivo

    return None


def _pub_has_pdf(pub):
    annotated = getattr(pub, "tiene_adjuntos_pdf", None)

    archivo_pdf = getattr(pub, "archivo_pdf", None)
    has_main_pdf = bool(archivo_pdf and getattr(archivo_pdf, "name", None))

    if annotated is not None:
        return bool(has_main_pdf or annotated)

    return bool(_get_pdf_file(pub))


def _pub_pdf_url(request, pub):
    return _build_absolute_url(request, _get_pdf_file(pub))


def _with_pdf_annotation(qs):
    adjuntos_pdf = (
        PublicacionArchivo.objects.filter(
            publicacion_id=OuterRef("pk"),
            archivo__isnull=False,
        )
        .exclude(archivo="")
    )

    return qs.annotate(tiene_adjuntos_pdf=Exists(adjuntos_pdf))


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

    def _apply_pdf_filter(self, qs, solo_con_pdf: bool):
        if not solo_con_pdf:
            return qs

        return qs.filter(
            Q(archivo_pdf__isnull=False) & ~Q(archivo_pdf="")
            | Q(tiene_adjuntos_pdf=True)
        ).distinct()

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"count": 0, "results": []})

        q_norm = q.lower()
        tipo = (request.query_params.get("type") or "").strip()
        year = (request.query_params.get("year") or "").strip()

        solo_con_pdf = _is_truthy(
            request.query_params.get("solo_con_pdf")
            or request.query_params.get("solo_pdf")
            or request.query_params.get("con_pdf")
            or request.query_params.get("has_pdf")
            or request.query_params.get("hasPdf")
        )

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
            .select_related(
                "tipo",
                "carrera",
                "carrera__facultad",
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related("archivos")
            .annotate(titulo_busqueda=title_expr)
            .annotate(
                sim=TrigramSimilarity(
                    Lower("titulo_busqueda"),
                    Lower(Value(q_norm)),
                )
            )
        )

        base = _with_pdf_annotation(base)

        base = annotate_tipo_publicacion_final(base).exclude(
            tipo_publicacion_final="sin_clasificar"
        )

        qs = (
            base.filter(titulo_busqueda__icontains=q_norm)
            | base.filter(tipo__nombre__icontains=q_norm)
            | base.filter(proyecto__nombre__icontains=q_norm)
            | base.filter(participaciones__autor__nombres__icontains=q_norm)
            | base.filter(participaciones__autor__apellidos__icontains=q_norm)
            | base.filter(sim__gte=0.2)
        ).distinct()

        qs = self._apply_tipo_filter(qs, tipo)

        if year.isdigit():
            qs = qs.filter(anio_publicacion=int(year))

        qs = self._apply_pdf_filter(qs, solo_con_pdf)

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
            author_names = []

            for rel in rels:
                author = rel.autor
                if not author:
                    continue

                label = f"{author.nombres or ''} {author.apellidos or ''}".strip()
                label = label or "—"

                authors.append(
                    {
                        "id": author.id,
                        "name": label,
                    }
                )
                author_names.append(label)

            tipo_final = getattr(pub, "tipo_publicacion_final", "sin_clasificar")
            has_pdf = _pub_has_pdf(pub)
            pdf_url = _pub_pdf_url(request, pub)

            results.append(
                {
                    "id": pub.id,
                    "title": (pub.titulo_busqueda or "").strip() or "—",
                    "titulo": (pub.titulo_busqueda or "").strip() or "—",
                    "year": pub.anio_publicacion,
                    "anio_publicacion": pub.anio_publicacion,
                    "tipo": pub.tipo.nombre if pub.tipo else None,
                    "tipo_codigo": pub.tipo.codigo if pub.tipo else None,
                    "tipo_publicacion_final": tipo_final,
                    "tipo_publicacion_final_label": tipo_publicacion_label(tipo_final),
                    "authors": authors,
                    "autor": ", ".join(author_names) if author_names else "—",
                    "snippet": None,
                    "sim": float(pub.sim or 0),
                    "hasPdf": has_pdf,
                    "has_pdf": has_pdf,
                    "tiene_pdf": has_pdf,
                    "pdf_url": pdf_url,
                    "archivo_pdf_url": pdf_url,
                    "citedBy": 0,
                }
            )

        return paginator.get_paginated_response(results)