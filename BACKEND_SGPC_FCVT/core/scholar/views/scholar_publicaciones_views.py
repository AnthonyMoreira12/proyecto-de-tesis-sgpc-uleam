"""
View pública de búsqueda académica de publicaciones.

Permite:
- búsqueda textual;
- relevancia;
- filtros por año;
- filtros por tipo;
- solo publicaciones con PDF;
- paginación;
- diferentes criterios de orden.
"""

from django.contrib.postgres.search import (
    TrigramSimilarity,
)
from django.db.models import (
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
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

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


def _is_truthy(value):
    return (
        str(
            value or ""
        )
        .strip()
        .lower()
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
    publication,
):
    # ---------------------------------------------------------
    # PDF principal
    # ---------------------------------------------------------

    archivo_pdf = getattr(
        publication,
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

    # ---------------------------------------------------------
    # Adjuntos precargados
    # ---------------------------------------------------------

    prefetched = getattr(
        publication,
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

    return None


def _pub_has_pdf(
    publication,
):
    archivo_pdf = getattr(
        publication,
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

    annotated = getattr(
        publication,
        "tiene_adjuntos_pdf",
        None,
    )

    if annotated is not None:
        return bool(
            has_main_pdf
            or annotated
        )

    return bool(
        _get_pdf_file(
            publication
        )
    )


def _pub_pdf_url(
    request,
    publication,
):
    return _build_absolute_url(
        request,
        _get_pdf_file(
            publication
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
            )
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


def _get_author_relations(
    publication,
):
    relations = getattr(
        publication,
        "participaciones_ordenadas",
        None,
    )

    if relations is not None:
        return relations

    prefetched = getattr(
        publication,
        "_prefetched_objects_cache",
        {},
    )

    if "participaciones" in prefetched:
        return sorted(
            prefetched[
                "participaciones"
            ],
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

    return []


def _build_authors(
    publication,
):
    authors = []
    names = []

    for relation in _get_author_relations(
        publication
    ):
        author = getattr(
            relation,
            "autor",
            None,
        )

        if not author:
            continue

        nombres = str(
            author.nombres
            or ""
        ).strip()

        apellidos = str(
            author.apellidos
            or ""
        ).strip()

        label = (
            f"{nombres} {apellidos}"
        ).strip()

        if not label:
            label = (
                str(
                    author.correo
                    or ""
                ).strip()
                or "—"
            )

        authors.append(
            {
                "id": author.id,
                "name": label,
            }
        )

        if label != "—":
            names.append(
                label
            )

    return (
        authors,
        ", ".join(names)
        if names
        else "—",
    )


# =============================================================
# VIEW
# =============================================================


class PublicacionesScholarAPIView(
    APIView
):
    """
    Búsqueda pública de publicaciones.
    """

    authentication_classes = []
    permission_classes = [
        permissions.AllowAny
    ]

    # =========================================================
    # TIPO
    # =========================================================

    def _apply_tipo_filter(
        self,
        queryset,
        tipo,
    ):
        tipo = str(
            tipo or ""
        ).strip().lower()

        if not tipo:
            return queryset

        if tipo.isdigit():
            return queryset.filter(
                tipo_id=int(tipo)
            )

        tipo_normalizado = (
            normalize_tipo_publicacion_final(
                tipo
            )
        )

        if not tipo_normalizado:
            return queryset

        return queryset.filter(
            tipo_publicacion_final=(
                tipo_normalizado
            )
        )

    # =========================================================
    # PDF
    # =========================================================

    def _apply_pdf_filter(
        self,
        queryset,
        solo_con_pdf,
    ):
        if not solo_con_pdf:
            return queryset

        return (
            queryset.filter(
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

    def _apply_sort(
        self,
        queryset,
        sort,
    ):
        sort = (
            str(
                sort or "relevance"
            )
            .strip()
            .lower()
        )

        if sort == "year_desc":
            return queryset.order_by(
                "-anio_publicacion",
                "-id",
            )

        if sort == "year_asc":
            return queryset.order_by(
                "anio_publicacion",
                "id",
            )

        if sort == "title_asc":
            return queryset.order_by(
                Lower(
                    "titulo_busqueda"
                ),
                "id",
            )

        # relevance
        return queryset.order_by(
            "-sim",
            "-anio_publicacion",
            "-updated_at",
            "-id",
        )

    # =========================================================
    # GET
    # =========================================================

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

        # El estado inicial del buscador no necesita
        # consultar todas las publicaciones.
        if not q:
            return Response(
                {
                    "count": 0,
                    "next": None,
                    "previous": None,
                    "results": [],
                }
            )

        q_norm = q.lower()

        tipo = (
            request.query_params
            .get(
                "type",
                "",
            )
            .strip()
        )

        year = (
            request.query_params
            .get(
                "year",
                "",
            )
            .strip()
        )

        sort = (
            request.query_params
            .get(
                "sort",
                "relevance",
            )
            .strip()
        )

        solo_con_pdf = _is_truthy(
            request.query_params.get(
                "solo_con_pdf"
            )
            or request.query_params.get(
                "solo_pdf"
            )
            or request.query_params.get(
                "con_pdf"
            )
            or request.query_params.get(
                "has_pdf"
            )
            or request.query_params.get(
                "hasPdf"
            )
        )

        # -----------------------------------------------------
        # Expresión de título
        # -----------------------------------------------------

        title_expr = Coalesce(
            "articulo__nombre_articulo",
            "ponencia__nombre_ponencia",
            "libro__nombre_libro",
            "capitulo_libro__nombre_capitulo",
            Value(""),
            output_field=TextField(),
        )

        # -----------------------------------------------------
        # Autores
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # Queryset
        # -----------------------------------------------------

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
                    title_expr
                )
            )
            .annotate(
                sim=TrigramSimilarity(
                    Lower(
                        "titulo_busqueda"
                    ),
                    Value(
                        q_norm
                    ),
                )
            )
        )

        queryset = (
            _with_pdf_annotation(
                queryset
            )
        )

        queryset = (
            annotate_tipo_publicacion_final(
                queryset
            )
            .exclude(
                tipo_publicacion_final=(
                    "sin_clasificar"
                )
            )
        )

        # -----------------------------------------------------
        # Búsqueda
        # -----------------------------------------------------

        queryset = (
            queryset.filter(
                Q(
                    titulo_busqueda__icontains=q
                )
                | Q(
                    tipo__nombre__icontains=q
                )
                | Q(
                    proyecto__nombre__icontains=q
                )
                | Q(
                    usuario_creador__nombres__icontains=q
                )
                | Q(
                    usuario_creador__apellidos__icontains=q
                )
                | Q(
                    participaciones__autor__nombres__icontains=q
                )
                | Q(
                    participaciones__autor__apellidos__icontains=q
                )
                | Q(
                    participaciones__autor__correo__icontains=q
                )
                | Q(
                    articulo__nombre_revista__icontains=q
                )
                | Q(
                    articulo__codigo_doi__icontains=q
                )
                | Q(
                    articulo__codigo_issn__icontains=q
                )
                | Q(
                    ponencia__nombre_evento__icontains=q
                )
                | Q(
                    libro__editorial_compilador__icontains=q
                )
                | Q(
                    capitulo_libro__nombre_libro__icontains=q
                )
                | Q(
                    sim__gte=0.2
                )
            )
            .distinct()
        )

        # -----------------------------------------------------
        # Tipo
        # -----------------------------------------------------

        queryset = (
            self._apply_tipo_filter(
                queryset,
                tipo,
            )
        )

        # -----------------------------------------------------
        # Año
        # -----------------------------------------------------

        if year.isdigit():
            queryset = (
                queryset.filter(
                    anio_publicacion=int(
                        year
                    )
                )
            )

        # -----------------------------------------------------
        # PDF
        # -----------------------------------------------------

        queryset = (
            self._apply_pdf_filter(
                queryset,
                solo_con_pdf,
            )
        )

        # -----------------------------------------------------
        # Orden
        # -----------------------------------------------------

        queryset = (
            self._apply_sort(
                queryset,
                sort,
            )
        )

        # -----------------------------------------------------
        # Paginación
        # -----------------------------------------------------

        paginator = (
            PageNumberPagination()
        )

        paginator.page_size = (
            _parse_page_size(
                request.query_params.get(
                    "page_size"
                ),
                default=10,
            )
        )

        page = (
            paginator.paginate_queryset(
                queryset,
                request,
            )
        )

        # -----------------------------------------------------
        # Respuesta
        # -----------------------------------------------------

        results = []

        for publication in page:
            (
                authors,
                author_names,
            ) = _build_authors(
                publication
            )

            tipo_final = getattr(
                publication,
                "tipo_publicacion_final",
                "sin_clasificar",
            )

            has_pdf = _pub_has_pdf(
                publication
            )

            pdf_url = _pub_pdf_url(
                request,
                publication,
            )

            title = (
                str(
                    publication.titulo_busqueda
                    or ""
                ).strip()
                or "—"
            )

            results.append(
                {
                    "id": (
                        publication.id
                    ),

                    "title": title,
                    "titulo": title,

                    "year": (
                        publication
                        .anio_publicacion
                    ),

                    "anio_publicacion": (
                        publication
                        .anio_publicacion
                    ),

                    "tipo": (
                        publication.tipo.nombre
                        if publication.tipo
                        else None
                    ),

                    "tipo_codigo": (
                        publication.tipo.codigo
                        if publication.tipo
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

                    "authors": authors,

                    "autor": (
                        author_names
                    ),

                    "snippet": None,

                    "sim": float(
                        getattr(
                            publication,
                            "sim",
                            0,
                        )
                        or 0
                    ),

                    "hasPdf": has_pdf,
                    "has_pdf": has_pdf,
                    "tiene_pdf": has_pdf,

                    "pdf_url": pdf_url,

                    "archivo_pdf_url": (
                        pdf_url
                    ),

                    # No existe todavía un sistema
                    # bibliométrico de citas.
                    "citedBy": 0,
                }
            )

        return (
            paginator
            .get_paginated_response(
                results
            )
        )