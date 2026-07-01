"""
Serializer para búsqueda rápida de proyectos.
Expone datos básicos del proyecto junto con su carrera y facultad relacionadas.
"""

from rest_framework import serializers

from core.models import Proyecto


class ProyectoBusquedaSerializer(serializers.ModelSerializer):
    carrera = serializers.CharField(source="carrera.nombre", read_only=True)
    facultad = serializers.CharField(source="carrera.facultad.nombre", read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "carrera",
            "facultad",
        ]
        read_only_fields = fields