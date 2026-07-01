"""
Serializer para listar autores visibles en el perfil público o institucional.
Expone nombre, afiliación, avatar y total de publicaciones asociadas.
"""

from rest_framework import serializers

from core.models import Autor


class PerfilAutorListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    org = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    publications = serializers.IntegerField(read_only=True)

    class Meta:
        model = Autor
        fields = ["id", "name", "org", "avatar", "publications"]
        read_only_fields = fields

    def get_name(self, obj):
        return f"{obj.nombres or ''} {obj.apellidos or ''}".strip()

    def get_org(self, obj):
        user = getattr(obj, "usuario", None)
        if not user:
            return "Autor externo"

        facultad = getattr(user, "facultad", None)
        carrera = getattr(user, "carrera", None)

        parts = []
        if carrera and getattr(carrera, "nombre", None):
            parts.append(carrera.nombre)
        if facultad and getattr(facultad, "nombre", None):
            parts.append(facultad.nombre)

        return " • ".join(parts) if parts else "ULEAM"

    def get_avatar(self, obj):
        request = self.context.get("request")
        user = getattr(obj, "usuario", None)

        if request and user and getattr(user, "avatar", None) and hasattr(user.avatar, "url"):
            try:
                return request.build_absolute_uri(user.avatar.url)
            except Exception:
                return user.avatar.url

        return None 