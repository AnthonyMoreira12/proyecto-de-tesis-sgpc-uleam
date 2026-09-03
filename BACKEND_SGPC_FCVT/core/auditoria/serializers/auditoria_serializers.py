"""Serializer de lectura del registro de auditoría."""

from rest_framework import serializers

from core.models import AuditoriaSistema


class AuditoriaSistemaSerializer(serializers.ModelSerializer):
    actor_nombre = serializers.SerializerMethodField(read_only=True)
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = AuditoriaSistema
        fields = [
            "id",
            "actor",
            "actor_nombre",
            "actor_email",
            "accion",
            "modulo",
            "entidad_tipo",
            "entidad_id",
            "descripcion",
            "datos_anteriores",
            "datos_nuevos",
            "contexto",
            "ip",
            "user_agent",
            "ruta",
            "metodo_http",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor_nombre(self, obj):
        if obj.actor is None:
            return None
        return f"{getattr(obj.actor, 'nombres', '')} {getattr(obj.actor, 'apellidos', '')}".strip()
