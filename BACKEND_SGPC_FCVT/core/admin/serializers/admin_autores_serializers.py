# Serializer administrativo de autores:
# expone los datos principales del autor, su usuario vinculado y el total de publicaciones para listados del módulo admin.

from rest_framework import serializers

from core.models import Autor


class AdminAutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    usuario_id = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()
    total_publicaciones = serializers.IntegerField(read_only=True)

    class Meta:
        model = Autor
        fields = [
            "id",
            "identificacion",
            "nombres",
            "apellidos",
            "nombre_completo",
            "correo",
            "institucion",
            "es_externo",
            "usuario_id",
            "usuario_email",
            "usuario_nombre",
            "total_publicaciones",
        ]
        read_only_fields = fields

    def get_nombre_completo(self, obj):
        return f"{obj.nombres or ''} {obj.apellidos or ''}".strip()

    def get_usuario_id(self, obj):
        usuario = getattr(obj, "usuario", None)
        return getattr(usuario, "id", None)

    def get_usuario_email(self, obj):
        usuario = getattr(obj, "usuario", None)
        return getattr(usuario, "email", None)

    def get_usuario_nombre(self, obj):
        usuario = getattr(obj, "usuario", None)
        if not usuario:
            return None
        return f"{usuario.nombres or ''} {usuario.apellidos or ''}".strip()