"""
Servicio para buscar publicaciones con filtros, orden y facetas para la vista tipo Scholar.
"""

from django.db.models import Count, Exists, OuterRef, Q

from core.models import Publicacion, PublicacionArchivo, PublicacionAutor
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
    annotate_tipo_publicacion_final,
    tipo_publicacion_label,
)


def parsear_anio(year_str: str):
    if not year_str:
        return None

    year_str = str(year_str).strip()

    if year_str.isdigit() and len(year_str) == 4:
        year = int(year_str)
        return (year, year)

    if "-" in year_str:
        start, end = year_str.split("-", 1)
        start = start.strip()
        end = end.strip()

        if start.isdigit() and end.isdigit() and len(start) == 4 and len(end) == 4:
            return (int(start), int(end))

    return None


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


class PublicacionesScholarServicio:
    @staticmethod
    def _construir_titulo_y_sede(pub):
        codigo = (pub.tipo.codigo or "").lower() if pub.tipo else ""

        title = None
        venue = None

        if codigo in {"articulo", "articulo_regional", "articulo_alto_impacto"} and getattr(pub, "articulo", None):
            title = (pub.articulo.nombre_articulo or "").strip() or None
            venue = (pub.articulo.nombre_revista or "").strip() or None

        elif codigo == "ponencia" and getattr(pub, "ponencia", None):
            title = (pub.ponencia.nombre_ponencia or "").strip() or None
            venue = (pub.ponencia.nombre_evento or "").strip() or None

        elif codigo == "libro" and getattr(pub, "libro", None):
            title = (pub.libro.nombre_libro or "").strip() or None
            venue = (pub.libro.editorial_compilador or "").strip() or None

        elif codigo in {"capitulo_libro", "capitulo"} and getattr(pub, "capitulo_libro", None):
            title = (pub.capitulo_libro.nombre_capitulo or "").strip() or None
            venue = (pub.capitulo_libro.nombre_libro or "").strip() or None

        if not title:
            tipo_nombre = pub.tipo.nombre if pub.tipo else "Publicación"
            title = (
                f"{tipo_nombre} #{pub.numero}"
                if getattr(pub, "numero", None)
                else f"{tipo_nombre} #{pub.id}"
            )

        return title, venue

    @staticmethod
    def _cadena_autores(pub_id: int) -> str:
        rels = (
            PublicacionAutor.objects
            .select_related("autor")
            .filter(publicacion_id=pub_id)
            .order_by("orden", "id")
        )

        names = []
        for rel in rels:
            autor = getattr(rel, "autor", None)
            if not autor:
                continue

            label = f"{autor.nombres or ''} {autor.apellidos or ''}".strip()
            if label:
                names.append(label)

        return ", ".join(names) if names else "—"

    @staticmethod
    def _aplicar_filtro_q(qs, q_norm: str):
        if not q_norm:
            return qs

        return (
            qs.filter(
                Q(tipo__nombre__icontains=q_norm)
                | Q(proyecto__nombre__icontains=q_norm)
                | Q(usuario_creador__nombres__icontains=q_norm)
                | Q(usuario_creador__apellidos__icontains=q_norm)
                | Q(participaciones__autor__nombres__icontains=q_norm)
                | Q(participaciones__autor__apellidos__icontains=q_norm)
                | Q(participaciones__autor__correo__icontains=q_norm)
                | Q(articulo__nombre_articulo__icontains=q_norm)
                | Q(articulo__nombre_revista__icontains=q_norm)
                | Q(ponencia__nombre_ponencia__icontains=q_norm)
                | Q(ponencia__nombre_evento__icontains=q_norm)
                | Q(libro__nombre_libro__icontains=q_norm)
                | Q(capitulo_libro__nombre_capitulo__icontains=q_norm)
                | Q(capitulo_libro__nombre_libro__icontains=q_norm)
            )
            .distinct()
        )

    @staticmethod
    def _aplicar_filtro_anio(qs, year_str: str):
        year_range = parsear_anio(year_str)
        if not year_range:
            return qs, None

        return (
            qs.filter(
                anio_publicacion__gte=year_range[0],
                anio_publicacion__lte=year_range[1],
            ),
            year_range,
        )

    @staticmethod
    def _aplicar_filtro_tipo(qs, tipo: str):
        if not tipo:
            return qs

        tipo = str(tipo).strip().lower()
        if not tipo:
            return qs

        if tipo.isdigit():
            return qs.filter(tipo_id=int(tipo))

        if tipo in TIPOS_PUBLICACION_FINALES:
            return qs.filter(tipo_publicacion_final=tipo)

        return qs

    @staticmethod
    def _aplicar_filtro_pdf(qs, solo_con_pdf: bool):
        if not solo_con_pdf:
            return qs

        return qs.filter(
            Q(archivo_pdf__isnull=False) & ~Q(archivo_pdf="")
            | Q(tiene_adjuntos_pdf=True)
        ).distinct()

    @staticmethod
    def _aplicar_orden(qs, sort: str):
        sort = (sort or "relevance").strip()

        if sort == "year_desc":
            return qs.order_by("-anio_publicacion", "-id")
        if sort == "year_asc":
            return qs.order_by("anio_publicacion", "id")

        return qs.order_by("-anio_publicacion", "-id")

    @staticmethod
    def buscar(*, request, params: dict):
        q = (params.get("q") or "").strip()
        q_norm = q.lower()

        year = (params.get("year") or "").strip()
        tipo = (params.get("type") or "").strip()
        sort = (params.get("sort") or "relevance").strip()
        facets = (params.get("facets") or "1").strip()

        solo_con_pdf = _is_truthy(
            params.get("solo_con_pdf")
            or params.get("solo_pdf")
            or params.get("con_pdf")
            or params.get("has_pdf")
            or params.get("hasPdf")
        )

        qs = (
            Publicacion.objects
            .select_related(
                "tipo",
                "proyecto",
                "usuario_creador",
                "carrera",
                "carrera__facultad",
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related("archivos")
        )

        qs = _with_pdf_annotation(qs)

        qs = annotate_tipo_publicacion_final(qs).exclude(
            tipo_publicacion_final="sin_clasificar"
        )
        qs = PublicacionesScholarServicio._aplicar_filtro_q(qs, q_norm)
        qs, year_range = PublicacionesScholarServicio._aplicar_filtro_anio(qs, year)
        qs = PublicacionesScholarServicio._aplicar_filtro_tipo(qs, tipo)
        qs = PublicacionesScholarServicio._aplicar_filtro_pdf(qs, solo_con_pdf)
        qs = PublicacionesScholarServicio._aplicar_orden(qs, sort)

        results = []
        for pub in qs[:50]:
            title, venue = PublicacionesScholarServicio._construir_titulo_y_sede(pub)
            authors = PublicacionesScholarServicio._cadena_autores(pub.id)
            tipo_final = getattr(pub, "tipo_publicacion_final", "sin_clasificar")
            has_pdf = _pub_has_pdf(pub)
            pdf_url = _pub_pdf_url(request, pub)

            results.append(
                {
                    "id": pub.id,
                    "title": title,
                    "titulo": title,
                    "authors": authors,
                    "autor": authors,
                    "venue": venue,
                    "year": pub.anio_publicacion,
                    "anio_publicacion": pub.anio_publicacion,
                    "type": {
                        "id": pub.tipo_id,
                        "nombre": pub.tipo.nombre if pub.tipo else None,
                        "codigo": pub.tipo.codigo if pub.tipo else None,
                    }
                    if pub.tipo
                    else None,
                    "tipo_publicacion_final": tipo_final,
                    "tipo_publicacion_final_label": tipo_publicacion_label(tipo_final),
                    "hasPdf": has_pdf,
                    "has_pdf": has_pdf,
                    "tiene_pdf": has_pdf,
                    "pdf_url": pdf_url,
                    "archivo_pdf_url": pdf_url,
                    "citedBy": 0,
                }
            )

        payload = {
            "results": results,
            "total": qs.count(),
        }

        if facets == "1":
            base = (
                Publicacion.objects
                .select_related(
                    "tipo",
                    "proyecto",
                    "usuario_creador",
                    "carrera",
                    "carrera__facultad",
                    "articulo",
                    "ponencia",
                    "libro",
                    "capitulo_libro",
                )
            )

            base = _with_pdf_annotation(base)

            base = annotate_tipo_publicacion_final(base).exclude(
                tipo_publicacion_final="sin_clasificar"
            )
            base = PublicacionesScholarServicio._aplicar_filtro_q(base, q_norm)
            base = PublicacionesScholarServicio._aplicar_filtro_pdf(base, solo_con_pdf)

            base_years = base
            if tipo:
                base_years = PublicacionesScholarServicio._aplicar_filtro_tipo(
                    base_years,
                    tipo,
                )

            years_qs = (
                base_years.exclude(anio_publicacion__isnull=True)
                .values("anio_publicacion")
                .annotate(c=Count("id"))
                .order_by("-anio_publicacion")
            )

            base_types = base
            if year_range:
                base_types = base_types.filter(
                    anio_publicacion__gte=year_range[0],
                    anio_publicacion__lte=year_range[1],
                )

            types_qs = (
                base_types.values("tipo_publicacion_final")
                .annotate(c=Count("id"))
                .order_by("tipo_publicacion_final")
            )

            payload["facets"] = {
                "years": [
                    {
                        "value": row["anio_publicacion"],
                        "count": row["c"],
                    }
                    for row in years_qs
                    if row["anio_publicacion"]
                ],
                "types": [
                    {
                        "codigo": row["tipo_publicacion_final"],
                        "nombre": tipo_publicacion_label(row["tipo_publicacion_final"]),
                        "count": row["c"],
                    }
                    for row in types_qs
                    if row["tipo_publicacion_final"]
                ],
            }

        return payload