"""
Serializer para búsqueda rápida de usuarios.
Expone datos básicos del perfil, relación académica y URL absoluta del avatar.
"""

from rest_framework import serializers

from core.models import Usuario


class UsuarioBusquedaSerializer(serializers.ModelSerializer):
    facultad = serializers.CharField(source="facultad.nombre", read_only=True)
    carrera = serializers.CharField(source="carrera.nombre", read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "nombres",
            "apellidos",
            "email",
            "rol",
            "facultad",
            "carrera",
            "avatar_url",
        ]
        read_only_fields = fields

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        avatar = getattr(obj, "avatar", None)

        if not avatar:
            return None

        avatar_url = getattr(avatar, "url", None)
        if not avatar_url:
            return None

        if request:
            try:
                return request.build_absolute_uri(avatar_url)
            except Exception:
                return avatar_url

        return avatar_url   