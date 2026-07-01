"""
Serializers de catálogos generales del sistema.
Exponen información base y nombres relacionados para formularios, filtros y listados.
"""

from rest_framework import serializers

from core.models import (
    Facultad,
    Carrera,
    Pais,
    Ciudad,
    AreaConocimiento,
    Subarea,
)


class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = [
            "id",
            "nombre",
            "siglas",
            "descripcion",
        ]
        read_only_fields = ["id"]


class CarreraSerializer(serializers.ModelSerializer):
    facultad_nombre = serializers.CharField(
        source="facultad.nombre",
        read_only=True,
    )

    class Meta:
        model = Carrera
        fields = [
            "id",
            "nombre",
            "facultad",
            "facultad_nombre",
        ]
        read_only_fields = [
            "id",
            "facultad_nombre",
        ]


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = [
            "id",
            "nombre",
        ]
        read_only_fields = ["id"]


class CiudadSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(
        source="pais.nombre",
        read_only=True,
    )

    class Meta:
        model = Ciudad
        fields = [
            "id",
            "nombre",
            "pais",
            "pais_nombre",
        ]
        read_only_fields = [
            "id",
            "pais_nombre",
        ]


class AreaConocimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaConocimiento
        fields = [
            "id",
            "nombre",
        ]
        read_only_fields = ["id"]


class SubareaConocimientoSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True,
    )

    class Meta:
        model = Subarea
        fields = [
            "id",
            "nombre",
            "area",
            "area_nombre",
        ]
        read_only_fields = [
            "id",
            "area_nombre",
        ]