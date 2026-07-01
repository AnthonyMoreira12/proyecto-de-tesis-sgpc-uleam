"""
Serializer para búsqueda rápida de autores.
Expone identificación básica y nombre completo para listados y autocompletado.
"""

from rest_framework import serializers

from core.models import Autor


class AutorBusquedaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Autor
        fields = [
            "id",
            "nombres",
            "apellidos",
            "correo",
            "nombre_completo",
        ]
        read_only_fields = fields

    def get_nombre_completo(self, obj):
        return f"{obj.nombres or ''} {obj.apellidos or ''}".strip()