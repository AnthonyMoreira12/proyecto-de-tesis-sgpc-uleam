"""
Serializer para resultados rápidos de búsqueda de publicaciones.

Expone:

- Título resuelto desde el modelo base o el subtipo.
- Tipo general y tipo final.
- Proyecto, carrera y facultad.
- Área y subárea.
- Usuario creador.
- Fecha y año de publicación.
- Disponibilidad y URL absoluta del PDF.

Se mantienen alias en inglés utilizados por el frontend:

- title
- authors
- year
- has_pdf
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


# ============================================================
# UTILIDADES
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
    normalized = _normalize_text(
        value
    )

    return normalized or None


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


def _get_user_full_name(user):
    """
    Construye el nombre completo de un usuario.
    """
    if user is None:
        return None

    get_full_name = getattr(
        user,
        "get_full_name",
        None,
    )

    if callable(get_full_name):
        resolved_name = _optional_text(
            get_full_name()
        )

        if resolved_name:
            return resolved_name

    names = _optional_text(
        getattr(
            user,
            "nombres",
            None,
        )
    )

    surnames = _optional_text(
        getattr(
            user,
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


def _resolve_final_publication_type(
    publication,
):
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
            return (
                FINAL_TYPE_ARTICLE_HIGH_IMPACT
            )

        if article_type == "regional":
            return (
                FINAL_TYPE_ARTICLE_REGIONAL
            )

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
    # Proyecto
    # --------------------------------------------------------

    proyecto_id = serializers.IntegerField(
        read_only=True,
    )

    proyecto = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Carrera y facultad
    # --------------------------------------------------------

    carrera_id = serializers.IntegerField(
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

    subarea_id = serializers.IntegerField(
        read_only=True,
    )

    subarea = serializers.SerializerMethodField(
        read_only=True,
    )

    # --------------------------------------------------------
    # Autor creador
    # --------------------------------------------------------

    usuario_creador_id = serializers.IntegerField(
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

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    tiene_pdf = serializers.SerializerMethodField(
        read_only=True,
    )

    has_pdf = serializers.SerializerMethodField(
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

            # Proyecto
            "proyecto_id",
            "proyecto",

            # Carrera y facultad
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",

            # Área y subárea
            "area_id",
            "area",
            "subarea_id",
            "subarea",

            # Autor creador
            "usuario_creador_id",
            "autor",
            "authors",

            # Fecha
            "fecha_publicacion",
            "anio_publicacion",
            "year",

            # PDF
            "tiene_pdf",
            "has_pdf",
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
        return _resolve_publication_title(
            obj
        )

    def get_title(
        self,
        obj,
    ):
        return self.get_titulo(
            obj
        )

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
        return _resolve_final_publication_type(
            obj
        )

    def get_tipo_publicacion_final_label(
        self,
        obj,
    ):
        final_type = (
            self.get_tipo_publicacion_final(
                obj
            )
        )

        return tipo_publicacion_label(
            final_type
        )

    def get_tipo_label(
        self,
        obj,
    ):
        return (
            self
            .get_tipo_publicacion_final_label(
                obj
            )
        )

    # ========================================================
    # PROYECTO
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

    # ========================================================
    # CARRERA Y FACULTAD
    # ========================================================

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
    # AUTOR
    # ========================================================

    def get_autor(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario_creador",
            None,
        )

        return _get_user_full_name(
            user
        )

    def get_authors(
        self,
        obj,
    ):
        """
        Mantiene el alias utilizado por el frontend.

        La búsqueda rápida expone al usuario creador como autor
        principal. El detalle completo de autorías corresponde
        al endpoint de detalle de la publicación.
        """
        return self.get_autor(
            obj
        ) or "—"

    # ========================================================
    # AÑO
    # ========================================================

    def get_year(
        self,
        obj,
    ):
        publication_year = getattr(
            obj,
            "anio_publicacion",
            None,
        )

        if publication_year is not None:
            return publication_year

        publication_date = getattr(
            obj,
            "fecha_publicacion",
            None,
        )

        if publication_date is None:
            return None

        return getattr(
            publication_date,
            "year",
            None,
        )

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
        return self.get_tiene_pdf(
            obj
        )

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
        return self.get_archivo_pdf_url(
            obj
        )

    # ========================================================
    # METADATOS ESPECÍFICOS
    # ========================================================

    def get_doi(
        self,
        obj,
    ):
        return _resolve_doi(
            obj
        )

    def get_external_url(
        self,
        obj,
    ):
        return _resolve_external_link(
            obj
        )