"""
Serializers administrativos para gestión de facultades y carreras.
Expone datos básicos y nombres relacionados para uso en panel de administración.
Complementa el módulo administrativo al entregar estructuras simples para listar,
consultar y relacionar carreras con sus respectivas facultades.
"""

from rest_framework import serializers
from core.models import Facultad, Carrera


class AdminFacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = ["id", "nombre", "siglas"]


class AdminCarreraSerializer(serializers.ModelSerializer):
    facultad_nombre = serializers.CharField(
        source="facultad.nombre",
        read_only=True,
    )

    class Meta:
        model = Carrera
        fields = ["id", "nombre", "facultad", "facultad_nombre"]