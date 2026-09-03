"""Serializers de comunicaciones globales."""

from rest_framework import serializers

from core.models import ComunicacionGlobal


class ComunicacionGlobalSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.SerializerMethodField(read_only=True)
    esta_vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = ComunicacionGlobal
        fields = [
            "id",
            "titulo",
            "mensaje",
            "tipo",
            "campania",
            "etiqueta_accion",
            "ruta_accion",
            "fecha_inicio",
            "fecha_fin",
            "activa",
            "esta_vigente",
            "creado_por",
            "creado_por_nombre",
            "created_at",
            "updated_at",
            "desactivada_at",
        ]
        read_only_fields = [
            "creado_por",
            "created_at",
            "updated_at",
            "desactivada_at",
        ]

    def get_creado_por_nombre(self, obj):
        user = getattr(obj, "creado_por", None)
        if user is None:
            return ""
        full_name = str(getattr(user, "get_full_name", lambda: "")() or "").strip()
        return full_name or str(getattr(user, "email", "") or "").strip()
