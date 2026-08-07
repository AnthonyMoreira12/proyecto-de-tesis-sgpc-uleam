"""
Servicio centralizado para la búsqueda pública de publicaciones
tipo Scholar.

Responsabilidades:

- construir el queryset base;
- búsqueda textual;
- búsqueda por autores e identificadores académicos;
- filtros por año, mes, tipo y disponibilidad de PDF;
- ordenamiento;
- construcción de facetas;
- serialización de resultados.

La vista HTTP debe delegar en este servicio para evitar mantener
dos implementaciones diferentes de la búsqueda Scholar.
"""

from django.contrib.postgres.search import (
    TrigramSimilarity,
)
from django.db.models import (
    Count,
    Exists,
    F,
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


MESES_PUBLICACION = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


# =============================================================
# NORMALIZACIÓN
# =============================================================


def _to_str(
    value,
):
    return str(
        value or ""
    ).strip()


def _is_truthy(
    value,
):
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


def parsear_anio(
    year_str,
):
    """
    Admite:

        2026
        2020-2026

    Retorna:

        (2026, 2026)
        (2020, 2026)

    Si el valor no es válido, retorna None.
    """

    raw = _to_str(
        year_str
    )

    if not raw:
        return None

    if (
        raw.isdigit()
        and len(raw) == 4
    ):
        year = int(
            raw
        )

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

    start_year = int(
        start
    )
    end_year = int(
        end
    )

    if start_year > end_year:
        start_year, end_year = (
            end_year,
            start_year,
        )

    return (
        start_year,
        end_year,
    )


def parsear_mes(
    month_value,
):
    """
    Convierte el mes a entero entre 1 y 12.

    Un valor vacío o inválido no aplica filtro.
    """

    raw = _to_str(
        month_value
    )

    if not raw:
        return None

    try:
        month = int(
            raw
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    if not 1 <= month <= 12:
        return None

    return month


def _month_label(
    publication,
):
    month = getattr(
        publication,
        "mes_publicacion",
        None,
    )

    if month in (
        None,
        "",
    ):
        return None

    display = getattr(
        publication,
        "get_mes_publicacion_display",
        None,
    )

    if callable(display):
        try:
            label = _to_str(
                display()
            )

            if label:
                return label

        except Exception:
            pass

    try:
        return MESES_PUBLICACION.get(
            int(month)
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


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
    publication,
):
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

    prefetched = getattr(
        publication,
        "_prefetched_objects_cache",
        {},
    )

    if "archivos" in prefetched:
        archivos = sorted(
            prefetched[
                "archivos"
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
            publication.archivos
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


def _publication_has_pdf(
    publication,
):
    annotated = getattr(
        publication,
        "tiene_adjuntos_pdf",
        None,
    )

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


def _publication_pdf_url(
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
                OuterRef(
                    "pk"
                )
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
# PUBLICACIÓN / AUTORES
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

    return (
        PublicacionAutor.objects
        .select_related(
            "autor"
        )
        .filter(
            publicacion=publication
        )
        .order_by(
            "orden",
            "id",
        )
    )


def _build_authors(
    publication,
):
    """
    Construye autores respetando PublicacionAutor.orden.

    No existe diferenciación entre autor principal y coautor.
    """

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

        nombres = _to_str(
            getattr(
                author,
                "nombres",
                "",
            )
        )

        apellidos = _to_str(
            getattr(
                author,
                "apellidos",
                "",
            )
        )

        label = (
            f"{nombres} {apellidos}"
        ).strip()

        if not label:
            label = (
                _to_str(
                    getattr(
                        author,
                        "correo",
                        "",
                    )
                )
                or "—"
            )

        order = getattr(
            relation,
            "orden",
            None,
        )

        authors.append(
            {
                "id": author.id,
                "autor_id": author.id,
                "name": label,
                "nombre_completo": label,
                "order": order,
                "orden": order,
            }
        )

        if label != "—":
            names.append(
                label
            )

    return (
        authors,
        ", ".join(
            names
        )
        if names
        else "—",
    )


# =============================================================
# SERVICIO
# =============================================================


class PublicacionesScholarServicio:
    """
    Servicio central de búsqueda Scholar.
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
    # BÚSQUEDA TEXTUAL
    # =========================================================

    @staticmethod
    def _aplicar_filtro_q(
        queryset,
        q_norm,
    ):
        if not q_norm:
            return queryset

        queryset = queryset.annotate(
            sim=TrigramSimilarity(
                Lower(
                    "titulo_busqueda"
                ),
                Value(
                    q_norm
                ),
            )
        )

        return (
            queryset.filter(
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
                    participaciones__autor__identificacion__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__orcid__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__registro_senescyt__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__google_scholar__icontains=(
                        q_norm
                    )
                )
                | Q(
                    participaciones__autor__scopus_id__icontains=(
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
                    articulo__codigo_issn__icontains=(
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
    # PERÍODO
    # =========================================================

    @staticmethod
    def _aplicar_filtro_anio(
        queryset,
        year_value,
    ):
        year_range = parsear_anio(
            year_value
        )

        if not year_range:
            return (
                queryset,
                None,
            )

        return (
            queryset.filter(
                anio_publicacion__gte=(
                    year_range[0]
                ),
                anio_publicacion__lte=(
                    year_range[1]
                ),
            ),
            year_range,
        )

    @staticmethod
    def _aplicar_filtro_mes(
        queryset,
        month_value,
    ):
        month = parsear_mes(
            month_value
        )

        if month is None:
            return (
                queryset,
                None,
            )

        return (
            queryset.filter(
                mes_publicacion=month
            ),
            month,
        )

    # =========================================================
    # TIPO
    # =========================================================

    @staticmethod
    def _aplicar_filtro_tipo(
        queryset,
        tipo,
    ):
        raw = _to_str(
            tipo
        ).lower()

        if not raw:
            return queryset

        if raw.isdigit():
            return queryset.filter(
                tipo_id=int(
                    raw
                )
            )

        tipo_normalizado = (
            normalize_tipo_publicacion_final(
                raw
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

    @staticmethod
    def _aplicar_filtro_pdf(
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

    @staticmethod
    def _aplicar_orden(
        queryset,
        sort,
        *,
        has_query=False,
    ):
        sort = (
            _to_str(
                sort
            ).lower()
            or "relevance"
        )

        if sort == "year_desc":
            return queryset.order_by(
                F(
                    "anio_publicacion"
                ).desc(
                    nulls_last=True
                ),
                F(
                    "mes_publicacion"
                ).desc(
                    nulls_last=True
                ),
                "-id",
            )

        if sort == "year_asc":
            return queryset.order_by(
                F(
                    "anio_publicacion"
                ).asc(
                    nulls_last=True
                ),
                F(
                    "mes_publicacion"
                ).asc(
                    nulls_last=True
                ),
                "id",
            )

        if sort == "title_asc":
            return queryset.order_by(
                Lower(
                    "titulo_busqueda"
                ),
                "id",
            )

        if (
            sort == "relevance"
            and has_query
        ):
            return queryset.order_by(
                "-sim",
                F(
                    "anio_publicacion"
                ).desc(
                    nulls_last=True
                ),
                F(
                    "mes_publicacion"
                ).desc(
                    nulls_last=True
                ),
                "-id",
            )

        return queryset.order_by(
            F(
                "anio_publicacion"
            ).desc(
                nulls_last=True
            ),
            F(
                "mes_publicacion"
            ).desc(
                nulls_last=True
            ),
            "-id",
        )

    # =========================================================
    # QUERYSET PÚBLICO
    # =========================================================

    @classmethod
    def construir_queryset(
        cls,
        params=None,
    ):
        """
        Construye el queryset final y devuelve además los valores
        normalizados que se necesitan para las facetas.
        """

        params = params or {}

        q = _to_str(
            params.get(
                "q"
            )
        )

        q_norm = q.lower()

        year = (
            params.get(
                "year"
            )
            or params.get(
                "anio"
            )
        )

        month = (
            params.get(
                "month"
            )
            or params.get(
                "mes"
            )
            or params.get(
                "mes_publicacion"
            )
        )

        tipo = (
            params.get(
                "type"
            )
            or params.get(
                "tipo"
            )
        )

        sort = (
            params.get(
                "sort"
            )
            or "relevance"
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

        queryset = (
            cls._base_queryset()
        )

        queryset = (
            cls._aplicar_filtro_q(
                queryset,
                q_norm,
            )
        )

        (
            queryset,
            year_range,
        ) = (
            cls._aplicar_filtro_anio(
                queryset,
                year,
            )
        )

        (
            queryset,
            month_value,
        ) = (
            cls._aplicar_filtro_mes(
                queryset,
                month,
            )
        )

        queryset = (
            cls._aplicar_filtro_tipo(
                queryset,
                tipo,
            )
        )

        queryset = (
            cls._aplicar_filtro_pdf(
                queryset,
                solo_con_pdf,
            )
        )

        queryset = (
            cls._aplicar_orden(
                queryset,
                sort,
                has_query=bool(
                    q_norm
                ),
            )
        )

        metadata = {
            "q": q,
            "q_norm": q_norm,
            "year_range": (
                year_range
            ),
            "month": (
                month_value
            ),
            "type": _to_str(
                tipo
            ),
            "solo_con_pdf": (
                solo_con_pdf
            ),
            "sort": _to_str(
                sort
            )
            or "relevance",
        }

        return (
            queryset,
            metadata,
        )

    # =========================================================
    # SERIALIZACIÓN
    # =========================================================

    @staticmethod
    def serializar_publicacion(
        *,
        request,
        publication,
    ):
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

        has_pdf = _publication_has_pdf(
            publication
        )

        pdf_url = _publication_pdf_url(
            request,
            publication,
        )

        title = (
            _to_str(
                getattr(
                    publication,
                    "titulo_busqueda",
                    "",
                )
            )
            or "—"
        )

        month = getattr(
            publication,
            "mes_publicacion",
            None,
        )

        return {
            "id": publication.id,

            "title": title,
            "titulo": title,

            "year": (
                publication.anio_publicacion
            ),
            "anio_publicacion": (
                publication.anio_publicacion
            ),

            "month": month,
            "mes_publicacion": month,
            "mes_publicacion_label": (
                _month_label(
                    publication
                )
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

            "type": (
                {
                    "id": (
                        publication.tipo_id
                    ),
                    "nombre": (
                        publication.tipo.nombre
                    ),
                    "codigo": (
                        publication.tipo.codigo
                    ),
                }
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
            "autor": author_names,

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

            # El dominio todavía no posee un modelo
            # bibliométrico de citas.
            "citedBy": 0,
        }

    # =========================================================
    # FACETAS
    # =========================================================

    @classmethod
    def construir_facetas(
        cls,
        *,
        metadata,
    ):
        """
        Construye facetas con la misma búsqueda textual/PDF.

        - años respetan tipo y mes;
        - tipos respetan año y mes;
        - meses respetan año y tipo.
        """

        base = cls._base_queryset()

        base = cls._aplicar_filtro_q(
            base,
            metadata.get(
                "q_norm"
            ),
        )

        base = cls._aplicar_filtro_pdf(
            base,
            metadata.get(
                "solo_con_pdf",
                False,
            ),
        )

        tipo = metadata.get(
            "type"
        )

        year_range = metadata.get(
            "year_range"
        )

        month = metadata.get(
            "month"
        )

        # -----------------------------------------------------
        # AÑOS
        # -----------------------------------------------------

        base_years = base

        if tipo:
            base_years = (
                cls._aplicar_filtro_tipo(
                    base_years,
                    tipo,
                )
            )

        if month:
            base_years = (
                base_years.filter(
                    mes_publicacion=month
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

        # -----------------------------------------------------
        # TIPOS
        # -----------------------------------------------------

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

        if month:
            base_types = (
                base_types.filter(
                    mes_publicacion=month
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

        # -----------------------------------------------------
        # MESES
        # -----------------------------------------------------

        base_months = base

        if tipo:
            base_months = (
                cls._aplicar_filtro_tipo(
                    base_months,
                    tipo,
                )
            )

        if year_range:
            base_months = (
                base_months.filter(
                    anio_publicacion__gte=(
                        year_range[0]
                    ),
                    anio_publicacion__lte=(
                        year_range[1]
                    ),
                )
            )

        months_qs = (
            base_months
            .exclude(
                mes_publicacion__isnull=True
            )
            .values(
                "mes_publicacion"
            )
            .annotate(
                c=Count(
                    "id",
                    distinct=True,
                )
            )
            .order_by(
                "mes_publicacion"
            )
        )

        return {
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

            "months": [
                {
                    "value": row[
                        "mes_publicacion"
                    ],
                    "nombre": (
                        MESES_PUBLICACION.get(
                            row[
                                "mes_publicacion"
                            ]
                        )
                    ),
                    "count": row["c"],
                }
                for row in months_qs
                if row[
                    "mes_publicacion"
                ]
            ],
        }

    # =========================================================
    # COMPATIBILIDAD DEL SERVICIO
    # =========================================================

    @classmethod
    def buscar(
        cls,
        *,
        request,
        params=None,
    ):
        """
        Mantiene un punto de entrada de servicio independiente
        de la APIView.

        Por compatibilidad limita esta respuesta directa a los
        primeros 50 resultados. La vista pública utiliza
        paginación real.
        """

        params = params or {}

        queryset, metadata = (
            cls.construir_queryset(
                params
            )
        )

        total = queryset.count()

        results = [
            cls.serializar_publicacion(
                request=request,
                publication=publication,
            )
            for publication in queryset[
                :50
            ]
        ]

        payload = {
            "results": results,
            "total": total,
            "count": total,
        }

        facets = _to_str(
            params.get(
                "facets",
                "1",
            )
        )

        if facets == "1":
            payload["facets"] = (
                cls.construir_facetas(
                    metadata=metadata
                )
            )

        return payload