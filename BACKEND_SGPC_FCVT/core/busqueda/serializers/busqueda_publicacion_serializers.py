from rest_framework import serializers

from core.models import Publicacion
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import tipo_publicacion_label


class PublicacionBusquedaSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="tipo.nombre", read_only=True)
    tipo_codigo = serializers.CharField(source="tipo.codigo", read_only=True)

    tipo_publicacion_final = serializers.CharField(read_only=True)
    tipo_publicacion_final_label = serializers.SerializerMethodField(read_only=True)

    proyecto = serializers.CharField(source="proyecto.nombre", read_only=True)
    facultad = serializers.CharField(source="facultad.nombre", read_only=True)
    carrera = serializers.CharField(source="carrera.nombre", read_only=True)

    autor = serializers.SerializerMethodField(read_only=True)
    titulo = serializers.SerializerMethodField(read_only=True)

    # alias amigables para frontend
    title = serializers.SerializerMethodField(read_only=True)
    authors = serializers.SerializerMethodField(read_only=True)
    year = serializers.SerializerMethodField(read_only=True)
    tipo_label = serializers.SerializerMethodField(read_only=True)

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
        ]
        read_only_fields = fields

    def get_tipo_publicacion_final_label(self, obj):
        tipo_id = getattr(obj, "tipo_publicacion_final", "sin_clasificar")
        return tipo_publicacion_label(tipo_id)

    def get_tipo_label(self, obj):
        return self.get_tipo_publicacion_final_label(obj)

    def get_autor(self, obj):
        usuario = getattr(obj, "usuario_creador", None)
        if not usuario:
            return None
        return f"{usuario.nombres or ''} {usuario.apellidos or ''}".strip() or None

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