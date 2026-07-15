from rest_framework import serializers

from core.models import Publicacion
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    tipo_publicacion_label,
)


class PublicacionBusquedaSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="tipo.nombre", read_only=True)
    tipo_codigo = serializers.CharField(source="tipo.codigo", read_only=True)

    tipo_publicacion_final = serializers.CharField(read_only=True)
    tipo_publicacion_final_label = serializers.SerializerMethodField(read_only=True)

    proyecto = serializers.CharField(source="proyecto.nombre", read_only=True)
    facultad = serializers.SerializerMethodField(read_only=True)
    carrera = serializers.SerializerMethodField(read_only=True)

    autor = serializers.SerializerMethodField(read_only=True)
    titulo = serializers.SerializerMethodField(read_only=True)

    title = serializers.SerializerMethodField(read_only=True)
    authors = serializers.SerializerMethodField(read_only=True)
    year = serializers.SerializerMethodField(read_only=True)
    tipo_label = serializers.SerializerMethodField(read_only=True)

    tiene_pdf = serializers.SerializerMethodField(read_only=True)
    has_pdf = serializers.SerializerMethodField(read_only=True)
    archivo_pdf_url = serializers.SerializerMethodField(read_only=True)
    pdf_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Publicacion
        fields = [
            "id",
            "titulo",
            "title",
            "tipo",
            "tipo_codigo",
            "tipo_label",
            "tipo_publicacion_final",
            "tipo_publicacion_final_label",
            "proyecto",
            "autor",
            "authors",
            "facultad",
            "carrera",
            "fecha_publicacion",
            "year",
            "tiene_pdf",
            "has_pdf",
            "archivo_pdf_url",
            "pdf_url",
        ]
        read_only_fields = fields

    def get_tipo_publicacion_final_label(self, obj):
        tipo_id = getattr(obj, "tipo_publicacion_final", "sin_clasificar")
        return tipo_publicacion_label(tipo_id)

    def get_tipo_label(self, obj):
        return self.get_tipo_publicacion_final_label(obj)

    def get_facultad(self, obj):
        carrera = getattr(obj, "carrera", None)
        facultad = getattr(carrera, "facultad", None) if carrera else None
        return getattr(facultad, "nombre", None) if facultad else None

    def get_carrera(self, obj):
        carrera = getattr(obj, "carrera", None)
        return getattr(carrera, "nombre", None) if carrera else None

    def get_autor(self, obj):
        usuario = getattr(obj, "usuario_creador", None)
        if not usuario:
            return None

        nombre = f"{usuario.nombres or ''} {usuario.apellidos or ''}".strip()
        return nombre or None

    def get_authors(self, obj):
        autor = self.get_autor(obj)
        return autor or "—"

    def get_titulo(self, obj):
        def pick(value):
            text = str(value).strip() if value is not None else ""
            return text if text else ""

        direct = pick(getattr(obj, "titulo", None))
        if direct:
            return direct

        for attr in (
            "nombre_articulo",
            "title",
            "nombre_ponencia",
            "nombre_capitulo",
            "nombre_libro",
            "nombre",
        ):
            value = pick(getattr(obj, attr, None))
            if value:
                return value

        return "—"

    def get_title(self, obj):
        return self.get_titulo(obj)

    def get_year(self, obj):
        fecha = getattr(obj, "fecha_publicacion", None)
        return getattr(fecha, "year", None) if fecha else None

    def get_tiene_pdf(self, obj):
        archivo_pdf = getattr(obj, "archivo_pdf", None)
        return bool(archivo_pdf)

    def get_has_pdf(self, obj):
        return self.get_tiene_pdf(obj)

    def get_archivo_pdf_url(self, obj):
        archivo_pdf = getattr(obj, "archivo_pdf", None)

        if not archivo_pdf:
            return None

        try:
            url = archivo_pdf.url
        except Exception:
            return None

        request = self.context.get("request")

        if request:
            try:
                return request.build_absolute_uri(url)
            except Exception:
                return url

        return url

    def get_pdf_url(self, obj):
        return self.get_archivo_pdf_url(obj)