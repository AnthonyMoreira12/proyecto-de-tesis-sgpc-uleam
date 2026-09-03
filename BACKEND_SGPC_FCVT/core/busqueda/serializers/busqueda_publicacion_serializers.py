"""
Serializer para resultados rápidos de búsqueda de publicaciones.

Expone:

- Título resuelto desde el subtipo correspondiente.
- Tipo general y tipo final.
- Sede, proyecto, carrera y facultad.
- Área y subárea.
- Autores científicos obtenidos desde PublicacionAutor.
- Primer autor como alias de compatibilidad, sin jerarquía de autoría.
- Mes opcional y año obligatorio de publicación.
- Revista, evento, editorial o libro contenedor.
- DOI y enlace externo.
- Disponibilidad y URL absoluta del PDF.

Se mantienen alias utilizados por el frontend:

- title
- authors
- year
- area_label
- source
- venue
- snippet
- has_pdf
- hasPdf
- pdf_url
"""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.models import Publicacion
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    tipo_publicacion_label,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

UNCLASSIFIED_PUBLICATION_TYPE = "sin_clasificar"

FINAL_TYPE_ARTICLE_HIGH_IMPACT = (
    "articulo_alto_impacto"
)

FINAL_TYPE_ARTICLE_REGIONAL = (
    "articulo_regional"
)

FINAL_TYPE_CONFERENCE = "ponencia"
FINAL_TYPE_BOOK = "libro"
FINAL_TYPE_BOOK_CHAPTER = "capitulo_libro"

SNIPPET_MAX_LENGTH = 320


# ============================================================
# UTILIDADES DE TEXTO
# ============================================================

def _normalize_text(value):
    """
    Normaliza un texto eliminando espacios repetidos.
    """
    return " ".join(
        str(value or "").split()
    )


def _optional_text(value):
    """
    Devuelve texto normalizado o None.
    """
    normalized = _normalize_text(value)

    return normalized or None


def _truncate_text(
    value,
    *,
    max_length=SNIPPET_MAX_LENGTH,
):
    """
    Limita un texto sin cortar palabras innecesariamente.
    """
    normalized = _optional_text(value)

    if not normalized:
        return None

    if len(normalized) <= max_length:
        return normalized

    shortened = normalized[
        : max_length + 1
    ].rsplit(
        " ",
        1,
    )[0].strip()

    if not shortened:
        shortened = normalized[:max_length].strip()

    return f"{shortened}…"


# ============================================================
# UTILIDADES DE RELACIONES
# ============================================================

def _get_related_object(
    instance,
    relation_name,
):
    """
    Obtiene de forma segura una relación OneToOne.

    Django puede lanzar RelatedObjectDoesNotExist cuando una
    publicación todavía no tiene creado su subtipo.
    """
    try:
        return getattr(
            instance,
            relation_name,
        )

    except (
        ObjectDoesNotExist,
        AttributeError,
    ):
        return None


def _get_participations(publication):
    """
    Obtiene las autorías científicas en el orden registrado.

    El selector general precarga la relación en el atributo
    _busqueda_participaciones. Se conserva un respaldo para los
    casos en que el serializer se utilice desde otra vista.
    """
    prefetched = getattr(
        publication,
        "_busqueda_participaciones",
        None,
    )

    if isinstance(prefetched, list):
        return prefetched

    manager = getattr(
        publication,
        "participaciones",
        None,
    )

    if manager is None:
        return []

    try:
        return list(
            manager
            .select_related(
                "autor",
                "autor__usuario",
            )
            .order_by(
                "orden",
                "pk",
            )
        )

    except (
        AttributeError,
        TypeError,
        ObjectDoesNotExist,
    ):
        return []


def _build_author_name(author):
    """
    Construye el nombre público de un Autor.
    """
    if author is None:
        return None

    model_full_name = getattr(
        author,
        "nombre_completo",
        None,
    )

    if callable(model_full_name):
        resolved_name = _optional_text(
            model_full_name()
        )

        if resolved_name:
            return resolved_name

    if isinstance(model_full_name, str):
        resolved_name = _optional_text(
            model_full_name
        )

        if resolved_name:
            return resolved_name

    names = _optional_text(
        getattr(
            author,
            "nombres",
            None,
        )
    )

    surnames = _optional_text(
        getattr(
            author,
            "apellidos",
            None,
        )
    )

    full_name = " ".join(
        value
        for value in [
            names,
            surnames,
        ]
        if value
    )

    return full_name or None


def _resolve_first_participation(publication):
    """
    Obtiene la primera participación según PublicacionAutor.orden.

    El orden conserva la secuencia bibliográfica de los autores,
    pero no representa una jerarquía ni un nivel de contribución.
    """
    participations = _get_participations(publication)

    return participations[0] if participations else None


# ============================================================
# UTILIDADES DE ARCHIVOS
# ============================================================

def _safe_file_url(
    file_field,
    *,
    request=None,
):
    """
    Obtiene la URL de un archivo almacenado.

    Cuando existe una petición, intenta construir una URL
    absoluta.
    """
    if not file_field:
        return None

    file_name = getattr(
        file_field,
        "name",
        None,
    )

    if not file_name:
        return None

    try:
        file_url = file_field.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return file_url

    try:
        return request.build_absolute_uri(
            file_url
        )

    except (
        ValueError,
        TypeError,
    ):
        return file_url


# ============================================================
# RESOLUCIÓN DEL SUBTIPO
# ============================================================

def _resolve_specific_title(publication):
    """
    Obtiene el título desde el registro específico relacionado.
    """
    relation_fields = (
        (
            "articulo",
            "nombre_articulo",
        ),
        (
            "ponencia",
            "nombre_ponencia",
        ),
        (
            "libro",
            "nombre_libro",
        ),
        (
            "capitulo_libro",
            "nombre_capitulo",
        ),
    )

    for relation_name, field_name in relation_fields:
        related_object = _get_related_object(
            publication,
            relation_name,
        )

        if related_object is None:
            continue

        resolved_title = _optional_text(
            getattr(
                related_object,
                field_name,
                None,
            )
        )

        if resolved_title:
            return resolved_title

    return None


def _resolve_publication_title(publication):
    """
    Resuelve el título utilizando el siguiente orden:

    1. Publicacion.titulo.
    2. Articulo.nombre_articulo.
    3. Ponencia.nombre_ponencia.
    4. Libro.nombre_libro.
    5. CapituloLibro.nombre_capitulo.
    """
    direct_title = _optional_text(
        getattr(
            publication,
            "titulo",
            None,
        )
    )

    if direct_title:
        return direct_title

    specific_title = _resolve_specific_title(
        publication
    )

    return specific_title or "—"


def _resolve_final_publication_type(publication):
    """
    Obtiene el tipo final.

    Prioriza la anotación generada por
    annotate_tipo_publicacion_final(). Cuando la anotación no
    existe, deriva el valor desde TipoPublicacion y el subtipo.
    """
    annotated_type = _optional_text(
        getattr(
            publication,
            "tipo_publicacion_final",
            None,
        )
    )

    if annotated_type:
        return annotated_type.lower()

    publication_type = getattr(
        publication,
        "tipo",
        None,
    )

    category = _optional_text(
        getattr(
            publication_type,
            "categoria",
            None,
        )
    )

    category = (
        category.lower()
        if category
        else None
    )

    if category == "articulo":
        article = _get_related_object(
            publication,
            "articulo",
        )

        article_type = _optional_text(
            getattr(
                article,
                "tipo_articulo",
                None,
            )
            if article is not None
            else None
        )

        article_type = (
            article_type.lower()
            if article_type
            else None
        )

        if article_type == "alto_impacto":
            return FINAL_TYPE_ARTICLE_HIGH_IMPACT

        if article_type == "regional":
            return FINAL_TYPE_ARTICLE_REGIONAL

    if category == "ponencia":
        return FINAL_TYPE_CONFERENCE

    if category == "libro":
        return FINAL_TYPE_BOOK

    if category == "capitulo":
        return FINAL_TYPE_BOOK_CHAPTER

    return UNCLASSIFIED_PUBLICATION_TYPE


def _resolve_external_link(publication):
    """
    Obtiene el enlace externo más apropiado según el subtipo.
    """
    relation_fields = (
        (
            "articulo",
            (
                "link_publicacion",
                "link_revista",
            ),
        ),
        (
            "ponencia",
            (
                "link_evento",
            ),
        ),
        (
            "libro",
            (
                "link_libro",
            ),
        ),
        (
            "capitulo_libro",
            (
                "link_capitulo",
            ),
        ),
    )

    for relation_name, field_names in relation_fields:
        related_object = _get_related_object(
            publication,
            relation_name,
        )

        if related_object is None:
            continue

        for field_name in field_names:
            link = _optional_text(
                getattr(
                    related_object,
                    field_name,
                    None,
                )
            )

            if link:
                return link

    return None


def _resolve_doi(publication):
    """
    Obtiene el DOI cuando la publicación corresponde a un
    artículo.
    """
    article = _get_related_object(
        publication,
        "articulo",
    )

    if article is None:
        return None

    return _optional_text(
        getattr(
            article,
            "codigo_doi",
            None,
        )
    )


def _resolve_venue(publication):
    """
    Obtiene el medio académico de publicación o presentación.
    """
    relation_fields = (
        (
            "articulo",
            "nombre_revista",
        ),
        (
            "ponencia",
            "nombre_evento",
        ),
        (
            "libro",
            "editorial_compilador",
        ),
        (
            "capitulo_libro",
            "nombre_libro",
        ),
    )

    for relation_name, field_name in relation_fields:
        related_object = _get_related_object(
            publication,
            relation_name,
        )

        if related_object is None:
            continue

        value = _optional_text(
            getattr(
                related_object,
                field_name,
                None,
            )
        )

        if value:
            return value

    return None


def _resolve_source(publication):
    """
    Utiliza el proyecto relacionado como fuente contextual.

    La carrera y facultad se exponen en campos independientes y
    el store puede combinarlas para construir la línea visual.
    """
    project = getattr(
        publication,
        "proyecto",
        None,
    )

    if project is None:
        return None

    return _optional_text(
        getattr(
            project,
            "nombre",
            None,
        )
    )


def _resolve_snippet(publication):
    """
    Obtiene un resumen breve cuando alguno de los modelos lo
    proporciona.

    Se consultan nombres compatibles sin asumir que todos los
    subtipos poseen los mismos campos.
    """
    candidate_fields = (
        "resumen",
        "descripcion",
        "abstract",
        "detalle",
    )

    for field_name in candidate_fields:
        value = _truncate_text(
            getattr(
                publication,
                field_name,
                None,
            )
        )

        if value:
            return value

    for relation_name in (
        "articulo",
        "ponencia",
        "libro",
        "capitulo_libro",
    ):
        related_object = _get_related_object(
            publication,
            relation_name,
        )

        if related_object is None:
            continue

        for field_name in candidate_fields:
            value = _truncate_text(
                getattr(
                    related_object,
                    field_name,
                    None,
                )
            )

            if value:
                return value

    return None


def _resolve_specific_alias(
    publication,
    relation_name,
    field_name,
):
    """
    Obtiene un campo textual específico para aliases públicos.
    """
    related_object = _get_related_object(
        publication,
        relation_name,
    )

    if related_object is None:
        return None

    return _optional_text(
        getattr(
            related_object,
            field_name,
            None,
        )
    )


# ============================================================
# SERIALIZER
# ============================================================

class PublicacionBusquedaSerializer(
    serializers.ModelSerializer
):
    """
    Representación resumida de una publicación para búsqueda
    general y autocompletado.
    """

    # --------------------------------------------------------
    # Títulos
    # --------------------------------------------------------

    titulo = serializers.SerializerMethodField(
        read_only=True,
    )

    title = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Tipo
    # --------------------------------------------------------

    tipo_id = serializers.IntegerField(
        read_only=True,
    )

    tipo = serializers.SerializerMethodField(
        read_only=True,
    )

    tipo_codigo = serializers.SerializerMethodField(
        read_only=True,
    )

    tipo_publicacion_final = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    tipo_publicacion_final_label = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    tipo_label = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Proyecto, fuente y medio
    # --------------------------------------------------------

    proyecto_id = serializers.IntegerField(
        read_only=True,
    )

    proyecto = serializers.SerializerMethodField(
        read_only=True,
    )

    source = serializers.SerializerMethodField(
        read_only=True,
    )

    venue = serializers.SerializerMethodField(
        read_only=True,
    )

    revista = serializers.SerializerMethodField(
        read_only=True,
    )

    evento = serializers.SerializerMethodField(
        read_only=True,
    )

    snippet = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Sede, carrera y facultad
    # --------------------------------------------------------

    sede_id = serializers.IntegerField(
        read_only=True,
    )

    carrera_id = serializers.IntegerField(
        read_only=True,
    )

    sede = serializers.SerializerMethodField(
        read_only=True,
    )

    carrera = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad_id = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Área y subárea
    # --------------------------------------------------------

    area_id = serializers.IntegerField(
        read_only=True,
    )

    area = serializers.SerializerMethodField(
        read_only=True,
    )

    area_label = serializers.SerializerMethodField(
        read_only=True,
    )

    subarea_id = serializers.IntegerField(
        read_only=True,
    )

    subarea = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Autorías científicas
    # --------------------------------------------------------

    usuario_creador_id = serializers.IntegerField(
        read_only=True,
    )

    autor_id = serializers.SerializerMethodField(
        read_only=True,
    )

    autor = serializers.SerializerMethodField(
        read_only=True,
    )

    authors = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Fecha
    # --------------------------------------------------------

    year = serializers.SerializerMethodField(
        read_only=True,
    )

    month = serializers.SerializerMethodField(
        read_only=True,
    )

    mes_publicacion_label = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    tiene_pdf = serializers.SerializerMethodField(
        read_only=True,
    )

    has_pdf = serializers.SerializerMethodField(
        read_only=True,
    )

    hasPdf = serializers.SerializerMethodField(
        read_only=True,
    )

    archivo_pdf_url = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    pdf_url = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Metadatos específicos
    # --------------------------------------------------------

    doi = serializers.SerializerMethodField(
        read_only=True,
    )

    external_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Publicacion

        fields = [
            "id",

            # Título
            "titulo",
            "title",

            # Tipo
            "tipo_id",
            "tipo",
            "tipo_codigo",
            "tipo_label",
            "tipo_publicacion_final",
            "tipo_publicacion_final_label",

            # Proyecto, fuente y medio
            "proyecto_id",
            "proyecto",
            "source",
            "venue",
            "revista",
            "evento",
            "snippet",

            # Sede, carrera y facultad
            "sede_id",
            "sede",
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",

            # Área y subárea
            "area_id",
            "area",
            "area_label",
            "subarea_id",
            "subarea",

            # Autorías
            "usuario_creador_id",
            "autor_id",
            "autor",
            "authors",

            # Periodo de publicación
            "anio_publicacion",
            "mes_publicacion",
            "mes_publicacion_label",
            "year",
            "month",

            # PDF
            "tiene_pdf",
            "has_pdf",
            "hasPdf",
            "archivo_pdf_url",
            "pdf_url",

            # Metadatos
            "doi",
            "external_url",
        ]

        read_only_fields = fields

    # ========================================================
    # TÍTULOS
    # ========================================================

    def get_titulo(
        self,
        obj,
    ):
        return _resolve_publication_title(obj)

    def get_title(
        self,
        obj,
    ):
        return self.get_titulo(obj)

    # ========================================================
    # TIPO
    # ========================================================

    def get_tipo(
        self,
        obj,
    ):
        publication_type = getattr(
            obj,
            "tipo",
            None,
        )

        if publication_type is None:
            return None

        return _optional_text(
            getattr(
                publication_type,
                "nombre",
                None,
            )
        )

    def get_tipo_codigo(
        self,
        obj,
    ):
        publication_type = getattr(
            obj,
            "tipo",
            None,
        )

        if publication_type is None:
            return None

        return _optional_text(
            getattr(
                publication_type,
                "codigo",
                None,
            )
        )

    def get_tipo_publicacion_final(
        self,
        obj,
    ):
        return _resolve_final_publication_type(obj)

    def get_tipo_publicacion_final_label(
        self,
        obj,
    ):
        final_type = self.get_tipo_publicacion_final(
            obj
        )

        return tipo_publicacion_label(
            final_type
        )

    def get_tipo_label(
        self,
        obj,
    ):
        return self.get_tipo_publicacion_final_label(
            obj
        )

    # ========================================================
    # PROYECTO, FUENTE Y MEDIO
    # ========================================================

    def get_proyecto(
        self,
        obj,
    ):
        project = getattr(
            obj,
            "proyecto",
            None,
        )

        if project is None:
            return None

        return _optional_text(
            getattr(
                project,
                "nombre",
                None,
            )
        )

    def get_source(
        self,
        obj,
    ):
        return _resolve_source(obj)

    def get_venue(
        self,
        obj,
    ):
        return _resolve_venue(obj)

    def get_revista(
        self,
        obj,
    ):
        return _resolve_specific_alias(
            obj,
            "articulo",
            "nombre_revista",
        )

    def get_evento(
        self,
        obj,
    ):
        return _resolve_specific_alias(
            obj,
            "ponencia",
            "nombre_evento",
        )

    def get_snippet(
        self,
        obj,
    ):
        return _resolve_snippet(obj)

    # ========================================================
    # SEDE, CARRERA Y FACULTAD
    # ========================================================

    def get_sede(
        self,
        obj,
    ):
        site = getattr(
            obj,
            "sede",
            None,
        )

        if site is None:
            return None

        return _optional_text(
            getattr(
                site,
                "nombre",
                None,
            )
        )

    def get_carrera(
        self,
        obj,
    ):
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        return _optional_text(
            getattr(
                career,
                "nombre",
                None,
            )
        )

    def get_facultad_id(
        self,
        obj,
    ):
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        return getattr(
            career,
            "facultad_id",
            None,
        )

    def get_facultad(
        self,
        obj,
    ):
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        faculty = getattr(
            career,
            "facultad",
            None,
        )

        if faculty is None:
            return None

        return _optional_text(
            getattr(
                faculty,
                "nombre",
                None,
            )
        )

    # ========================================================
    # ÁREA Y SUBÁREA
    # ========================================================

    def get_area(
        self,
        obj,
    ):
        area = getattr(
            obj,
            "area",
            None,
        )

        if area is None:
            return None

        return _optional_text(
            getattr(
                area,
                "nombre",
                None,
            )
        )

    def get_area_label(
        self,
        obj,
    ):
        return self.get_area(obj)

    def get_subarea(
        self,
        obj,
    ):
        subarea = getattr(
            obj,
            "subarea",
            None,
        )

        if subarea is None:
            return None

        return _optional_text(
            getattr(
                subarea,
                "nombre",
                None,
            )
        )

    # ========================================================
    # AUTORÍAS CIENTÍFICAS
    # ========================================================

    def get_autor_id(
        self,
        obj,
    ):
        participation = _resolve_first_participation(
            obj
        )

        author = getattr(
            participation,
            "autor",
            None,
        )

        return getattr(
            author,
            "pk",
            None,
        )

    def get_autor(
        self,
        obj,
    ):
        """
        Mantiene un alias textual para consumidores antiguos.

        El valor representa al primer autor según el orden
        bibliográfico, no una jerarquía de autoría ni al Usuario
        que registró la publicación.
        """
        participation = _resolve_first_participation(
            obj
        )

        author = getattr(
            participation,
            "autor",
            None,
        )

        return _build_author_name(author)

    def get_authors(
        self,
        obj,
    ):
        """
        Devuelve las autorías reales, ordenadas según
        PublicacionAutor.orden.
        """
        output = []

        for participation in _get_participations(obj):
            author = getattr(
                participation,
                "autor",
                None,
            )

            if author is None:
                continue

            author_name = _build_author_name(
                author
            )

            if not author_name:
                continue

            order = getattr(
                participation,
                "orden",
                None,
            )

            output.append(
                {
                    "id": author.pk,
                    "autor_id": author.pk,
                    "name": author_name,
                    "nombre_completo": author_name,
                    "order": order,
                    "orden": order,
                    "es_externo": bool(
                        getattr(
                            author,
                            "es_externo",
                            False,
                        )
                    ),
                }
            )

        return output

    # ========================================================
    # PERIODO DE PUBLICACIÓN
    # ========================================================

    def get_year(
        self,
        obj,
    ):
        return getattr(
            obj,
            "anio_publicacion",
            None,
        )

    def get_month(
        self,
        obj,
    ):
        return getattr(
            obj,
            "mes_publicacion",
            None,
        )

    def get_mes_publicacion_label(
        self,
        obj,
    ):
        month = self.get_month(obj)

        if month is None:
            return None

        display = getattr(
            obj,
            "get_mes_publicacion_display",
            None,
        )

        if callable(display):
            value = _optional_text(display())
            if value:
                return value

        month_labels = {
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

        try:
            return month_labels.get(int(month))
        except (TypeError, ValueError):
            return None

    # ========================================================
    # PDF
    # ========================================================

    def get_tiene_pdf(
        self,
        obj,
    ):
        pdf_file = getattr(
            obj,
            "archivo_pdf",
            None,
        )

        return bool(
            pdf_file
            and getattr(
                pdf_file,
                "name",
                None,
            )
        )

    def get_has_pdf(
        self,
        obj,
    ):
        return self.get_tiene_pdf(obj)

    def get_hasPdf(
        self,
        obj,
    ):
        return self.get_tiene_pdf(obj)

    def get_archivo_pdf_url(
        self,
        obj,
    ):
        return _safe_file_url(
            getattr(
                obj,
                "archivo_pdf",
                None,
            ),
            request=self.context.get(
                "request"
            ),
        )

    def get_pdf_url(
        self,
        obj,
    ):
        return self.get_archivo_pdf_url(obj)

    # ========================================================
    # METADATOS ESPECÍFICOS
    # ========================================================

    def get_doi(
        self,
        obj,
    ):
        return _resolve_doi(obj)

    def get_external_url(
        self,
        obj,
    ):
        return _resolve_external_link(obj)