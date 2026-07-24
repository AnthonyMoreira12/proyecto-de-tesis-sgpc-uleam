"""
Servicio de búsqueda de publicaciones tipo Scholar.

Gestiona:
- búsqueda textual;
- relevancia;
- año;
- tipo;
- PDF;
- orden;
- facetas;
- autores;
- URLs de PDF.
"""

from django.contrib.postgres.search import (
    TrigramSimilarity,
)
from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Q,
    TextField,
    Value,
)
from django.db.models.functions import (
    Coalesce,
    Lower,
)

from core.models import (
    Publicacion,
    PublicacionArchivo,
    PublicacionAutor,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
    normalize_tipo_publicacion_final,
    tipo_publicacion_label,
)


# =============================================================
# HELPERS
# =============================================================


def _to_str(value):
    return str(
        value or ""
    ).strip()


def parsear_anio(
    year_str: str,
):
    raw = _to_str(
        year_str
    )

    if not raw:
        return None

    if (
        raw.isdigit()
        and len(raw) == 4
    ):
        year = int(raw)

        return (
            year,
            year,
        )

    if "-" not in raw:
        return None

    start, end = raw.split(
        "-",
        1,
    )

    start = start.strip()
    end = end.strip()

    if not (
        start.isdigit()
        and end.isdigit()
        and len(start) == 4
        and len(end) == 4
    ):
        return None

    start_year = int(start)
    end_year = int(end)

    if start_year > end_year:
        (
            start_year,
            end_year,
        ) = (
            end_year,
            start_year,
        )

    return (
        start_year,
        end_year,
    )


def _is_truthy(value):
    return (
        _to_str(
            value
        ).lower()
        in {
            "1",
            "true",
            "t",
            "yes",
            "y",
            "si",
            "sí",
            "on",
        }
    )


# =============================================================
# PDF
# =============================================================


def _build_absolute_url(
    request,
    file_field,
):
    try:
        if (
            not file_field
            or not getattr(
                file_field,
                "name",
                None,
            )
        ):
            return None

        url = file_field.url

    except (
        AttributeError,
        ValueError,
    ):
        return None

    if request:
        try:
            return (
                request.build_absolute_uri(
                    url
                )
            )
        except Exception:
            pass

    return url


def _get_pdf_file(
    pub,
):
    archivo_pdf = getattr(
        pub,
        "archivo_pdf",
        None,
    )

    if (
        archivo_pdf
        and getattr(
            archivo_pdf,
            "name",
            None,
        )
    ):
        return archivo_pdf

    prefetched = getattr(
        pub,
        "_prefetched_objects_cache",
        {},
    )

    if "archivos" in prefetched:
        archivos = sorted(
            prefetched["archivos"],
            key=lambda item: (
                getattr(
                    item,
                    "orden",
                    0,
                ),
                getattr(
                    item,
                    "id",
                    0,
                ),
            ),
        )

        for adjunto in archivos:
            archivo = getattr(
                adjunto,
                "archivo",
                None,
            )

            if (
                archivo
                and getattr(
                    archivo,
                    "name",
                    None,
                )
            ):
                return archivo

        return None

    try:
        adjunto = (
            pub.archivos
            .exclude(
                archivo=""
            )
            .order_by(
                "orden",
                "id",
            )
            .first()
        )

    except Exception:
        return None

    if not adjunto:
        return None

    archivo = getattr(
        adjunto,
        "archivo",
        None,
    )

    if (
        archivo
        and getattr(
            archivo,
            "name",
            None,
        )
    ):
        return archivo

    return None


def _pub_has_pdf(
    pub,
):
    annotated = getattr(
        pub,
        "tiene_adjuntos_pdf",
        None,
    )

    archivo_pdf = getattr(
        pub,
        "archivo_pdf",
        None,
    )

    has_main_pdf = bool(
        archivo_pdf
        and getattr(
            archivo_pdf,
            "name",
            None,
        )
    )

    if annotated is not None:
        return bool(
            has_main_pdf
            or annotated
        )

    return bool(
        _get_pdf_file(
            pub
        )
    )


def _pub_pdf_url(
    request,
    pub,
):
    return _build_absolute_url(
        request,
        _get_pdf_file(
            pub
        ),
    )


def _with_pdf_annotation(
    queryset,
):
    adjuntos_pdf = (
        PublicacionArchivo.objects
        .filter(
            publicacion_id=(
                OuterRef("pk")
            ),
        )
        .exclude(
            archivo=""
        )
    )

    return queryset.annotate(
        tiene_adjuntos_pdf=Exists(
            adjuntos_pdf
        )
    )


# =============================================================
# PUBLICACIONES
# =============================================================


def _title_expression():
    return Coalesce(
        "articulo__nombre_articulo",
        "ponencia__nombre_ponencia",
        "libro__nombre_libro",
        "capitulo_libro__nombre_capitulo",
        Value(""),
        output_field=TextField(),
    )


def _get_autor_rels(
    pub,
):
    participaciones = getattr(
        pub,
        "participaciones_ordenadas",
        None,
    )

    if participaciones is not None:
        return participaciones

    return (
        PublicacionAutor.objects
        .select_related(
            "autor"
        )
        .filter(
            publicacion=pub
        )
        .order_by(
            "orden",
            "id",
        )
    )


def _cadena_autores(
    pub,
) -> str:
    names = []

    for rel in _get_autor_rels(
        pub
    ):
        autor = getattr(
            rel,
            "autor",
            None,
        )

        if not autor:
            continue

        label = (
            f"{_to_str(autor.nombres)} "
            f"{_to_str(autor.apellidos)}"
        ).strip()

        if not label:
            label = (
                _to_str(
                    autor.correo
                )
                or "—"
            )

        if label != "—":
            names.append(
                label
            )

    return (
        ", ".join(names)
        if names
        else "—"
    )


class PublicacionesScholarServicio:
    """
    Servicio principal de búsqueda Scholar.
    """

    # =========================================================
    # QUERYSET BASE
    # =========================================================

    @staticmethod
    def _base_queryset():
        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects
                .select_related(
                    "autor"
                )
                .order_by(
                    "orden",
                    "id",
                )
            ),
            to_attr=(
                "participaciones_ordenadas"
            ),
        )

        queryset = (
            Publicacion.objects
            .select_related(
                "tipo",
                "proyecto",
                "usuario_creador",

                "carrera",
                "carrera__facultad",

                "area",
                "subarea",

                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related(
                autores_prefetch,
                "archivos",
            )
            .annotate(
                titulo_busqueda=(
                    _title_expression()
                )
            )
        )

        queryset = (
            _with_pdf_annotation(
                queryset
            )
        )

        return (
            annotate_tipo_publicacion_final(
                queryset
            )
            .exclude(
                tipo_publicacion_final=(
                    "sin_clasificar"
                )
            )
        )

    # =========================================================
    # TÍTULO / SEDE
    # =========================================================

    @staticmethod
    def _construir_titulo_y_sede(
        pub,
    ):
        articulo = getattr(
            pub,
            "articulo",
            None,
        )

        if articulo:
            return (
                _to_str(
                    articulo.nombre_articulo
                )
                or "—",
                _to_str(
                    articulo.nombre_revista
                )
                or None,
            )

        ponencia = getattr(
            pub,
            "ponencia",
            None,
        )

        if ponencia:
            return (
                _to_str(
                    ponencia.nombre_ponencia
                )
                or "—",
                _to_str(
                    ponencia.nombre_evento
                )
                or None,
            )

        libro = getattr(
            pub,
            "libro",
            None,
        )

        if libro:
            return (
                _to_str(
                    libro.nombre_libro
                )
                or "—",
                _to_str(
                    libro.editorial_compilador
                )
                or None,
            )

        capitulo = getattr(
            pub,
            "capitulo_libro",
            None,
        )

        if capitulo:
            return (
                _to_str(
                    capitulo.nombre_capitulo
                )
                or "—",
                _to_str(
                    capitulo.nombre_libro
                )
                or None,
            )

        tipo_nombre = (
            pub.tipo.nombre
            if pub.tipo
            else "Publicación"
        )

        numero = (
            pub.numero
            or pub.id
        )

        return (
            f"{tipo_nombre} #{numero}",
            None,
        )

    # =========================================================
    # FILTRO Q
    # =========================================================

    @staticmethod
    def _aplicar_filtro_q(
        qs,
        q_norm,
    ):
        if not q_norm:
            return qs

        qs = qs.annotate(
            sim=TrigramSimilarity(
                "titulo_busqueda",
                Value(q_norm),
            )
        )

        return (
            qs.filter(
                Q(
                    titulo_busqueda__icontains=(
                        q_norm
                    )
                )
                | Q(
                    tipo__nombre__icontains=(
                        q_norm
                    )
                )
                | Q(
                    proyecto__nombre__icontains=(
                        q_norm
                    )
                )
                | Q(
                    usuario_creador__nombres__icontains=(
                        q_norm
                    )
                )
                | Q(
                    usuario_creador__apellidos__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__nombres__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__apellidos__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__correo__icontains=(
                        q_norm
                    )
                )
                | Q(
                    articulo__nombre_revista__icontains=(
                        q_norm
                    )
                )
                | Q(
                    articulo__codigo_doi__icontains=(
                        q_norm
                    )
                )
                | Q(
                    ponencia__nombre_evento__icontains=(
                        q_norm
                    )
                )
                | Q(
                    libro__editorial_compilador__icontains=(
                        q_norm
                    )
                )
                | Q(
                    capitulo_libro__nombre_libro__icontains=(
                        q_norm
                    )
                )
                | Q(
                    sim__gte=0.2
                )
            )
            .distinct()
        )

    # =========================================================
    # AÑO
    # =========================================================

    @staticmethod
    def _aplicar_filtro_anio(
        qs,
        year_str,
    ):
        year_range = parsear_anio(
            year_str
        )

        if not year_range:
            return (
                qs,
                None,
            )

        return (
            qs.filter(
                anio_publicacion__gte=(
                    year_range[0]
                ),
                anio_publicacion__lte=(
                    year_range[1]
                ),
            ),
            year_range,
        )

    # =========================================================
    # TIPO
    # =========================================================

    @staticmethod
    def _aplicar_filtro_tipo(
        qs,
        tipo,
    ):
        raw = _to_str(
            tipo
        ).lower()

        if not raw:
            return qs

        if raw.isdigit():
            return qs.filter(
                tipo_id=int(raw)
            )

        tipo_normalizado = (
            normalize_tipo_publicacion_final(
                raw
            )
        )

        if not tipo_normalizado:
            return qs

        return qs.filter(
            tipo_publicacion_final=(
                tipo_normalizado
            )
        )

    # =========================================================
    # PDF
    # =========================================================

    @staticmethod
    def _aplicar_filtro_pdf(
        qs,
        solo_con_pdf,
    ):
        if not solo_con_pdf:
            return qs

        return (
            qs.filter(
                (
                    Q(
                        archivo_pdf__isnull=False
                    )
                    & ~Q(
                        archivo_pdf=""
                    )
                )
                | Q(
                    tiene_adjuntos_pdf=True
                )
            )
            .distinct()
        )

    # =========================================================
    # ORDEN
    # =========================================================

    @staticmethod
    def _aplicar_orden(
        qs,
        sort,
        *,
        has_query=False,
    ):
        sort = (
            _to_str(sort)
            or "relevance"
        )

        if sort == "year_desc":
            return qs.order_by(
                "-anio_publicacion",
                "-id",
            )

        if sort == "year_asc":
            return qs.order_by(
                "anio_publicacion",
                "id",
            )

        if sort == "title_asc":
            return qs.order_by(
                Lower(
                    "titulo_busqueda"
                ),
                "id",
            )

        # -----------------------------------------------------
        # Relevancia
        # -----------------------------------------------------

        if (
            sort == "relevance"
            and has_query
        ):
            return qs.order_by(
                "-sim",
                "-anio_publicacion",
                "-id",
            )

        return qs.order_by(
            "-anio_publicacion",
            "-id",
        )

    # =========================================================
    # BÚSQUEDA
    # =========================================================

    @staticmethod
    def buscar(
        *,
        request,
        params,
    ):
        params = params or {}

        q = _to_str(
            params.get("q")
        )

        q_norm = q.lower()

        year = _to_str(
            params.get("year")
        )

        tipo = _to_str(
            params.get("type")
        )

        sort = (
            _to_str(
                params.get("sort")
            )
            or "relevance"
        )

        facets = (
            _to_str(
                params.get("facets")
            )
            or "1"
        )

        solo_con_pdf = _is_truthy(
            params.get(
                "solo_con_pdf"
            )
            or params.get(
                "solo_pdf"
            )
            or params.get(
                "con_pdf"
            )
            or params.get(
                "has_pdf"
            )
            or params.get(
                "hasPdf"
            )
        )

        # -----------------------------------------------------
        # Query principal
        # -----------------------------------------------------

        qs = (
            PublicacionesScholarServicio
            ._base_queryset()
        )

        qs = (
            PublicacionesScholarServicio
            ._aplicar_filtro_q(
                qs,
                q_norm,
            )
        )

        (
            qs,
            year_range,
        ) = (
            PublicacionesScholarServicio
            ._aplicar_filtro_anio(
                qs,
                year,
            )
        )

        qs = (
            PublicacionesScholarServicio
            ._aplicar_filtro_tipo(
                qs,
                tipo,
            )
        )

        qs = (
            PublicacionesScholarServicio
            ._aplicar_filtro_pdf(
                qs,
                solo_con_pdf,
            )
        )

        qs = (
            PublicacionesScholarServicio
            ._aplicar_orden(
                qs,
                sort,
                has_query=bool(
                    q_norm
                ),
            )
        )

        total = qs.count()

        results = []

        for pub in qs[:50]:
            (
                title,
                venue,
            ) = (
                PublicacionesScholarServicio
                ._construir_titulo_y_sede(
                    pub
                )
            )

            authors = (
                _cadena_autores(
                    pub
                )
            )

            tipo_final = getattr(
                pub,
                "tipo_publicacion_final",
                "sin_clasificar",
            )

            has_pdf = _pub_has_pdf(
                pub
            )

            pdf_url = _pub_pdf_url(
                request,
                pub,
            )

            results.append(
                {
                    "id": pub.id,

                    "title": title,
                    "titulo": title,

                    "authors": authors,
                    "autor": authors,

                    "venue": venue,

                    "year": (
                        pub.anio_publicacion
                    ),

                    "anio_publicacion": (
                        pub.anio_publicacion
                    ),

                    "type": (
                        {
                            "id": (
                                pub.tipo_id
                            ),
                            "nombre": (
                                pub.tipo.nombre
                            ),
                            "codigo": (
                                pub.tipo.codigo
                            ),
                        }
                        if pub.tipo
                        else None
                    ),

                    "tipo_publicacion_final": (
                        tipo_final
                    ),

                    "tipo_publicacion_final_label": (
                        tipo_publicacion_label(
                            tipo_final
                        )
                    ),

                    "hasPdf": has_pdf,
                    "has_pdf": has_pdf,
                    "tiene_pdf": has_pdf,

                    "pdf_url": pdf_url,

                    "archivo_pdf_url": (
                        pdf_url
                    ),

                    # No existe todavía un modelo
                    # bibliométrico de citas.
                    "citedBy": 0,
                }
            )

        payload = {
            "results": results,
            "total": total,
        }

        # =====================================================
        # FACETAS
        # =====================================================

        if facets == "1":
            base = (
                PublicacionesScholarServicio
                ._base_queryset()
            )

            base = (
                PublicacionesScholarServicio
                ._aplicar_filtro_q(
                    base,
                    q_norm,
                )
            )

            base = (
                PublicacionesScholarServicio
                ._aplicar_filtro_pdf(
                    base,
                    solo_con_pdf,
                )
            )

            # -------------------------------------------------
            # Faceta de años:
            # respeta el filtro de tipo.
            # -------------------------------------------------

            base_years = base

            if tipo:
                base_years = (
                    PublicacionesScholarServicio
                    ._aplicar_filtro_tipo(
                        base_years,
                        tipo,
                    )
                )

            years_qs = (
                base_years
                .exclude(
                    anio_publicacion__isnull=True
                )
                .values(
                    "anio_publicacion"
                )
                .annotate(
                    c=Count(
                        "id",
                        distinct=True,
                    )
                )
                .order_by(
                    "-anio_publicacion"
                )
            )

            # -------------------------------------------------
            # Faceta de tipos:
            # respeta el filtro de año.
            # -------------------------------------------------

            base_types = base

            if year_range:
                base_types = (
                    base_types.filter(
                        anio_publicacion__gte=(
                            year_range[0]
                        ),
                        anio_publicacion__lte=(
                            year_range[1]
                        ),
                    )
                )

            types_qs = (
                base_types
                .values(
                    "tipo_publicacion_final"
                )
                .annotate(
                    c=Count(
                        "id",
                        distinct=True,
                    )
                )
                .order_by(
                    "tipo_publicacion_final"
                )
            )

            payload["facets"] = {
                "years": [
                    {
                        "value": row[
                            "anio_publicacion"
                        ],
                        "count": row["c"],
                    }
                    for row in years_qs
                    if row[
                        "anio_publicacion"
                    ]
                ],

                "types": [
                    {
                        "codigo": row[
                            "tipo_publicacion_final"
                        ],

                        "nombre": (
                            tipo_publicacion_label(
                                row[
                                    "tipo_publicacion_final"
                                ]
                            )
                        ),

                        "count": row["c"],
                    }

                    for row in types_qs

                    if row[
                        "tipo_publicacion_final"
                    ]
                ],
            }

        return payload