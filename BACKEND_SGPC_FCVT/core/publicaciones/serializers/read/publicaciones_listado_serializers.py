from rest_framework import serializers

from core.models import Publicacion, PublicacionAutor
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    tipo_publicacion_label,
)


def _to_str(value):
    return "" if value is None else str(value).strip()


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


class PublicacionListadoSerializer(serializers.ModelSerializer):
    titulo = serializers.SerializerMethodField()
    autor = serializers.SerializerMethodField()
    proyecto = serializers.SerializerMethodField()
    facultad = serializers.SerializerMethodField()
    carrera = serializers.SerializerMethodField()

    tipo = serializers.SerializerMethodField()
    tipo_codigo = serializers.SerializerMethodField()

    tipo_publicacion_final = serializers.SerializerMethodField()
    tipo_publicacion_final_label = serializers.SerializerMethodField()

    tiene_pdf = serializers.SerializerMethodField()
    has_pdf = serializers.SerializerMethodField()
    hasPdf = serializers.SerializerMethodField()
    archivo_pdf_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Publicacion
        fields = [
            "id",
            "titulo",
            "autor",
            "proyecto",
            "facultad",
            "carrera",
            "fecha_publicacion",
            "anio_publicacion",
            "tipo",
            "tipo_codigo",
            "tipo_publicacion_final",
            "tipo_publicacion_final_label",
            "tiene_pdf",
            "has_pdf",
            "hasPdf",
            "archivo_pdf_url",
            "pdf_url",
        ]
        read_only_fields = fields

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

    def _get_facultad_obj(self, obj):
        carrera = getattr(obj, "carrera", None)
        if not carrera:
            return None
        return getattr(carrera, "facultad", None)

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

    def _get_pdf_file(self, obj):
        archivo_pdf = getattr(obj, "archivo_pdf", None)

        if archivo_pdf and getattr(archivo_pdf, "name", None):
            return archivo_pdf

        prefetched = getattr(obj, "_prefetched_objects_cache", {})

        if "archivos" in prefetched:
            for adjunto in prefetched["archivos"]:
                archivo = getattr(adjunto, "archivo", None)
                if archivo and getattr(archivo, "name", None):
                    return archivo
            return None

        try:
            adjunto = (
                obj.archivos.filter(archivo__isnull=False)
                .exclude(archivo="")
                .order_by("orden", "id")
                .first()
            )
        except Exception:
            return None

        if adjunto and adjunto.archivo and getattr(adjunto.archivo, "name", None):
            return adjunto.archivo

        return None

    def get_titulo(self, obj):
        articulo = getattr(obj, "articulo", None)
        ponencia = getattr(obj, "ponencia", None)
        libro = getattr(obj, "libro", None)
        capitulo = getattr(obj, "capitulo_libro", None)

        return _first_filled(
            getattr(obj, "titulo", None),
            getattr(obj, "nombre_publicacion", None),
            getattr(articulo, "nombre_articulo", None),
            getattr(ponencia, "nombre_ponencia", None),
            getattr(libro, "nombre_libro", None),
            getattr(capitulo, "nombre_capitulo", None),
            getattr(getattr(obj, "proyecto", None), "nombre", None),
            "Sin título",
        )

    def get_autor(self, obj):
        nombres = []

        for rel in self._get_autor_rels(obj):
            autor = getattr(rel, "autor", None)
            if not autor:
                continue

            full = _first_filled(
                f"{_to_str(getattr(autor, 'nombres', None))} {_to_str(getattr(autor, 'apellidos', None))}".strip(),
                getattr(autor, "nombre_completo", None),
            )

            if full:
                nombres.append(full)

        return ", ".join(nombres) if nombres else "—"

    def get_proyecto(self, obj):
        return _to_str(getattr(getattr(obj, "proyecto", None), "nombre", None))

    def get_facultad(self, obj):
        facultad = self._get_facultad_obj(obj)
        return _to_str(getattr(facultad, "nombre", None))

    def get_carrera(self, obj):
        return _to_str(getattr(getattr(obj, "carrera", None), "nombre", None))

    def get_tipo(self, obj):
        return _resolve_tipo_final_label(obj)

    def get_tipo_codigo(self, obj):
        return _resolve_tipo_final_codigo(obj)

    def get_tipo_publicacion_final(self, obj):
        return _resolve_tipo_final_codigo(obj)

    def get_tipo_publicacion_final_label(self, obj):
        return _resolve_tipo_final_label(obj)

    def get_tiene_pdf(self, obj):
        return bool(self._get_pdf_file(obj))

    def get_has_pdf(self, obj):
        return self.get_tiene_pdf(obj)

    def get_hasPdf(self, obj):
        return self.get_tiene_pdf(obj)

    def get_archivo_pdf_url(self, obj):
        return self._build_file_url(self._get_pdf_file(obj))

    def get_pdf_url(self, obj):
        return self.get_archivo_pdf_url(obj)