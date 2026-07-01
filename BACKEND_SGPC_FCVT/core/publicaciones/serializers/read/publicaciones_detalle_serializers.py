from rest_framework import serializers

from core.models import Publicacion, PublicacionAutor
from core.publicaciones.serializers.base.publicaciones_autores_serializers import (
    PublicacionAutorSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import can_edit_publicacion
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    tipo_publicacion_label,
)


def _to_str(value):
    return "" if value is None else str(value).strip()


def _to_lower(value):
    value = _to_str(value)
    return value.lower() if value else ""


def _first_filled(*values):
    for value in values:
        text = _to_str(value)
        if text:
            return text
    return ""


def _resolve_tipo_final_codigo(obj):
    annotated = _to_str(getattr(obj, "tipo_publicacion_final", None)).lower()
    if annotated and annotated != "sin_clasificar":
        return annotated

    tipo = getattr(obj, "tipo", None)
    tipo_codigo = _to_str(getattr(tipo, "codigo", None)).lower()
    tipo_categoria = _to_str(getattr(tipo, "categoria", None)).lower()

    articulo = getattr(obj, "articulo", None)
    tipo_articulo = _to_str(getattr(articulo, "tipo_articulo", None)).lower()

    if tipo_categoria == "articulo" or tipo_codigo in {
        "articulo",
        "articulo_regional",
        "articulo_alto_impacto",
    }:
        if tipo_articulo == "alto_impacto":
            return "articulo_alto_impacto"
        if tipo_articulo == "regional":
            return "articulo_regional"

    if tipo_categoria == "ponencia" or tipo_codigo == "ponencia":
        return "ponencia"

    if tipo_categoria == "libro" or tipo_codigo == "libro":
        return "libro"

    if tipo_categoria == "capitulo" or tipo_codigo in {"capitulo", "capitulo_libro"}:
        return "capitulo_libro"

    return "sin_clasificar"


def _resolve_tipo_final_label(obj):
    codigo = _resolve_tipo_final_codigo(obj)
    label = tipo_publicacion_label(codigo)

    if label != "Sin clasificar":
        return label

    base_nombre = _to_str(getattr(getattr(obj, "tipo", None), "nombre", None))
    return base_nombre or "Publicación"


class PublicacionDetalleSerializer(serializers.ModelSerializer):
    titulo = serializers.SerializerMethodField()

    tipo = serializers.SerializerMethodField()
    tipo_codigo = serializers.SerializerMethodField()
    tipo_publicacion_final = serializers.SerializerMethodField()
    tipo_publicacion_final_label = serializers.SerializerMethodField()

    facultad_id = serializers.SerializerMethodField()
    facultad = serializers.SerializerMethodField()

    carrera_id = serializers.SerializerMethodField()
    carrera = serializers.SerializerMethodField()

    proyecto_id = serializers.SerializerMethodField()
    proyecto = serializers.SerializerMethodField()

    area_id = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()

    subarea_id = serializers.SerializerMethodField()
    subarea = serializers.SerializerMethodField()

    pais_id = serializers.SerializerMethodField()
    pais = serializers.SerializerMethodField()

    ciudad_id = serializers.SerializerMethodField()
    ciudad = serializers.SerializerMethodField()

    archivo_pdf = serializers.SerializerMethodField()
    autores = serializers.SerializerMethodField()
    puede_editar = serializers.SerializerMethodField()

    resumen = serializers.SerializerMethodField()
    descripcion = serializers.SerializerMethodField()
    abstract = serializers.SerializerMethodField()
    detalle = serializers.SerializerMethodField()

    tipo_presentacion = serializers.SerializerMethodField()
    nombre_evento = serializers.SerializerMethodField()
    nombre_ponencia = serializers.SerializerMethodField()
    codigo_issn_isbn = serializers.SerializerMethodField()
    link_evento = serializers.SerializerMethodField()

    tipo_articulo = serializers.SerializerMethodField()
    nombre_articulo = serializers.SerializerMethodField()
    base_datos_indexada = serializers.SerializerMethodField()
    base_datos_otra = serializers.SerializerMethodField()
    codigo_doi = serializers.SerializerMethodField()
    codigo_issn = serializers.SerializerMethodField()
    nombre_revista = serializers.SerializerMethodField()
    numero_revista = serializers.SerializerMethodField()
    link_publicacion = serializers.SerializerMethodField()
    link_revista = serializers.SerializerMethodField()
    factor_impacto = serializers.SerializerMethodField()
    cuartil = serializers.SerializerMethodField()
    sjr = serializers.SerializerMethodField()

    revisor_par_arbitraje = serializers.SerializerMethodField()

    nombre_libro = serializers.SerializerMethodField()
    codigo_isbn = serializers.SerializerMethodField()
    editorial_compilador = serializers.SerializerMethodField()
    link_libro = serializers.SerializerMethodField()

    nombre_capitulo = serializers.SerializerMethodField()
    editor_compilador = serializers.SerializerMethodField()
    link_capitulo = serializers.SerializerMethodField()

    class Meta:
        model = Publicacion
        fields = [
            "id",
            "titulo",
            "tipo",
            "tipo_codigo",
            "tipo_publicacion_final",
            "tipo_publicacion_final_label",
            "facultad_id",
            "facultad",
            "carrera_id",
            "carrera",
            "proyecto_id",
            "proyecto",
            "area_id",
            "area",
            "subarea_id",
            "subarea",
            "pais_id",
            "pais",
            "ciudad_id",
            "ciudad",
            "origen_tipo",
            "origen_grado",
            "fecha_publicacion",
            "anio_publicacion",
            "archivo_pdf",
            "autores",
            "puede_editar",
            "resumen",
            "descripcion",
            "abstract",
            "detalle",
            "tipo_presentacion",
            "nombre_evento",
            "nombre_ponencia",
            "codigo_issn_isbn",
            "link_evento",
            "tipo_articulo",
            "nombre_articulo",
            "base_datos_indexada",
            "base_datos_otra",
            "codigo_doi",
            "codigo_issn",
            "nombre_revista",
            "numero_revista",
            "link_publicacion",
            "link_revista",
            "factor_impacto",
            "cuartil",
            "sjr",
            "revisor_par_arbitraje",
            "nombre_libro",
            "codigo_isbn",
            "editorial_compilador",
            "link_libro",
            "nombre_capitulo",
            "editor_compilador",
            "link_capitulo",
        ]
        read_only_fields = fields

    def _related_attr(self, obj, rel_name, attr_name, default=""):
        rel = getattr(obj, rel_name, None)
        if rel is None:
            return default
        return getattr(rel, attr_name, default)

    def _obj_id(self, rel):
        return getattr(rel, "id", None) if rel is not None else None

    def _build_file_url(self, file_field):
        try:
            if not file_field:
                return None
            url = file_field.url
        except Exception:
            return None

        request = self.context.get("request")
        if request:
            try:
                return request.build_absolute_uri(url)
            except Exception:
                return url
        return url

    def _get_autor_rels(self, obj):
        prefetched = getattr(obj, "_prefetched_objects_cache", {})

        if "publicacionautor_set" in prefetched:
            return prefetched["publicacionautor_set"]

        if "participaciones" in prefetched:
            return prefetched["participaciones"]

        if "participaciones_ordenadas" in prefetched:
            return prefetched["participaciones_ordenadas"]

        return (
            PublicacionAutor.objects.select_related("autor")
            .filter(publicacion=obj)
            .order_by("orden", "id")
        )

    def _get_articulo(self, obj):
        return getattr(obj, "articulo", None)

    def _get_tipo_articulo(self, obj):
        articulo = self._get_articulo(obj)
        return _to_lower(getattr(articulo, "tipo_articulo", None))

    def get_titulo(self, obj):
        return _first_filled(
            getattr(obj, "titulo", None),
            getattr(obj, "nombre_publicacion", None),
            self._related_attr(obj, "articulo", "nombre_articulo"),
            self._related_attr(obj, "ponencia", "nombre_ponencia"),
            self._related_attr(obj, "libro", "nombre_libro"),
            self._related_attr(obj, "capitulo_libro", "nombre_capitulo"),
            getattr(getattr(obj, "proyecto", None), "nombre", None),
            "Publicación",
        )

    def get_tipo(self, obj):
        return _resolve_tipo_final_label(obj)

    def get_tipo_codigo(self, obj):
        return _resolve_tipo_final_codigo(obj)

    def get_tipo_publicacion_final(self, obj):
        return _resolve_tipo_final_codigo(obj)

    def get_tipo_publicacion_final_label(self, obj):
        return _resolve_tipo_final_label(obj)

    def get_facultad_id(self, obj):
        return self._obj_id(getattr(obj, "facultad", None))

    def get_facultad(self, obj):
        return _to_str(getattr(getattr(obj, "facultad", None), "nombre", None))

    def get_carrera_id(self, obj):
        return self._obj_id(getattr(obj, "carrera", None))

    def get_carrera(self, obj):
        return _to_str(getattr(getattr(obj, "carrera", None), "nombre", None))

    def get_proyecto_id(self, obj):
        return self._obj_id(getattr(obj, "proyecto", None))

    def get_proyecto(self, obj):
        return _to_str(getattr(getattr(obj, "proyecto", None), "nombre", None))

    def get_area_id(self, obj):
        return self._obj_id(getattr(obj, "area", None))

    def get_area(self, obj):
        return _to_str(getattr(getattr(obj, "area", None), "nombre", None))

    def get_subarea_id(self, obj):
        return self._obj_id(getattr(obj, "subarea", None))

    def get_subarea(self, obj):
        return _to_str(getattr(getattr(obj, "subarea", None), "nombre", None))

    def get_pais_id(self, obj):
        return self._obj_id(getattr(obj, "pais", None))

    def get_pais(self, obj):
        return _to_str(getattr(getattr(obj, "pais", None), "nombre", None))

    def get_ciudad_id(self, obj):
        return self._obj_id(getattr(obj, "ciudad", None))

    def get_ciudad(self, obj):
        return _to_str(getattr(getattr(obj, "ciudad", None), "nombre", None))

    def get_archivo_pdf(self, obj):
        return self._build_file_url(getattr(obj, "archivo_pdf", None))

    def get_autores(self, obj):
        rels = self._get_autor_rels(obj)
        return PublicacionAutorSerializer(rels, many=True).data

    def get_puede_editar(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return can_edit_publicacion(user, obj)

    def get_resumen(self, obj):
        return _to_str(getattr(obj, "resumen", None))

    def get_descripcion(self, obj):
        return _to_str(getattr(obj, "descripcion", None))

    def get_abstract(self, obj):
        return _to_str(getattr(obj, "abstract", None))

    def get_detalle(self, obj):
        return _to_str(getattr(obj, "detalle", None))

    def get_tipo_presentacion(self, obj):
        return _to_str(self._related_attr(obj, "ponencia", "tipo_presentacion"))

    def get_nombre_evento(self, obj):
        return _to_str(self._related_attr(obj, "ponencia", "nombre_evento"))

    def get_nombre_ponencia(self, obj):
        return _to_str(self._related_attr(obj, "ponencia", "nombre_ponencia"))

    def get_codigo_issn_isbn(self, obj):
        return _to_str(self._related_attr(obj, "ponencia", "codigo_issn_isbn"))

    def get_link_evento(self, obj):
        return _to_str(self._related_attr(obj, "ponencia", "link_evento"))

    def get_tipo_articulo(self, obj):
        return self._get_tipo_articulo(obj)

    def get_nombre_articulo(self, obj):
        return _to_str(self._related_attr(obj, "articulo", "nombre_articulo"))

    def get_base_datos_indexada(self, obj):
        if self._get_tipo_articulo(obj) != "regional":
            return ""

        value = self._related_attr(obj, "articulo", "base_datos_indexada")
        return _to_str(value)

    def get_base_datos_otra(self, obj):
        if self._get_tipo_articulo(obj) != "regional":
            return ""

        base = self._related_attr(obj, "articulo", "base_datos_indexada")
        if _to_lower(base) != "otra":
            return ""

        return _to_str(self._related_attr(obj, "articulo", "base_datos_otra"))

    def get_codigo_doi(self, obj):
        return _to_str(self._related_attr(obj, "articulo", "codigo_doi"))

    def get_codigo_issn(self, obj):
        return _to_str(self._related_attr(obj, "articulo", "codigo_issn"))

    def get_nombre_revista(self, obj):
        return _to_str(self._related_attr(obj, "articulo", "nombre_revista"))

    def get_numero_revista(self, obj):
        return self._related_attr(obj, "articulo", "numero_revista", None)

    def get_link_publicacion(self, obj):
        return _to_str(self._related_attr(obj, "articulo", "link_publicacion"))

    def get_link_revista(self, obj):
        return _to_str(self._related_attr(obj, "articulo", "link_revista"))

    def get_factor_impacto(self, obj):
        if self._get_tipo_articulo(obj) != "alto_impacto":
            return ""
        return _to_str(self._related_attr(obj, "articulo", "factor_impacto"))

    def get_cuartil(self, obj):
        if self._get_tipo_articulo(obj) != "alto_impacto":
            return ""
        return _to_str(self._related_attr(obj, "articulo", "cuartil"))

    def get_sjr(self, obj):
        if self._get_tipo_articulo(obj) != "alto_impacto":
            return ""
        return _to_str(self._related_attr(obj, "articulo", "sjr"))

    def get_revisor_par_arbitraje(self, obj):
        return _first_filled(
            self._related_attr(obj, "libro", "revisor_par_arbitraje"),
            self._related_attr(obj, "capitulo_libro", "revisor_par_arbitraje"),
        )

    def get_nombre_libro(self, obj):
        return _first_filled(
            self._related_attr(obj, "libro", "nombre_libro"),
            self._related_attr(obj, "capitulo_libro", "nombre_libro"),
        )

    def get_codigo_isbn(self, obj):
        return _first_filled(
            self._related_attr(obj, "libro", "codigo_isbn"),
            self._related_attr(obj, "capitulo_libro", "codigo_isbn"),
        )

    def get_editorial_compilador(self, obj):
        return _to_str(self._related_attr(obj, "libro", "editorial_compilador"))

    def get_link_libro(self, obj):
        return _to_str(self._related_attr(obj, "libro", "link_libro"))

    def get_nombre_capitulo(self, obj):
        return _to_str(self._related_attr(obj, "capitulo_libro", "nombre_capitulo"))

    def get_editor_compilador(self, obj):
        return _to_str(self._related_attr(obj, "capitulo_libro", "editor_compilador"))

    def get_link_capitulo(self, obj):
        return _to_str(self._related_attr(obj, "capitulo_libro", "link_capitulo"))