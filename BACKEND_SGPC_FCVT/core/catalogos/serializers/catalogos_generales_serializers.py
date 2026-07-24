"""
Serializers de los catálogos generales del sistema.

Este módulo gestiona:

- Facultades.
- Carreras.
- Países.
- Ciudades.
- Áreas de conocimiento.
- Subáreas de conocimiento.

Los serializers normalizan textos antes de guardar y exponen
de forma segura los nombres de las relaciones utilizadas por
formularios, filtros y listados.
"""

import unicodedata

from rest_framework import serializers

from core.models import (
    AreaConocimiento,
    Carrera,
    Ciudad,
    Facultad,
    Pais,
    Subarea,
)


# ============================================================
# UTILIDADES DE NORMALIZACIÓN
# ============================================================

def _normalize_single_line(
    value,
    *,
    allow_blank=False,
):
    """
    Normaliza textos destinados a una sola línea.

    - Aplica normalización Unicode.
    - Elimina espacios repetidos.
    - Elimina saltos de línea y tabulaciones.
    """
    if value is None:
        if allow_blank:
            return ""

        raise serializers.ValidationError(
            "Este campo no puede ser nulo."
        )

    normalized = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    normalized = " ".join(
        normalized.split()
    )

    if not normalized and not allow_blank:
        raise serializers.ValidationError(
            "Este campo no puede estar vacío."
        )

    return normalized


def _normalize_multiline(
    value,
    *,
    allow_blank=True,
):
    """
    Normaliza textos que pueden contener varios párrafos.
    """
    if value is None:
        return "" if allow_blank else None

    normalized = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    normalized = (
        normalized
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    normalized_lines = []

    for raw_line in normalized.split("\n"):
        clean_line = " ".join(
            raw_line
            .replace("\t", " ")
            .split()
        )

        normalized_lines.append(
            clean_line
        )

    while (
        normalized_lines
        and not normalized_lines[-1]
    ):
        normalized_lines.pop()

    result = "\n".join(
        normalized_lines
    ).strip()

    if not result and not allow_blank:
        raise serializers.ValidationError(
            "Este campo no puede estar vacío."
        )

    return result


def _related_name(
    instance,
    relation_name,
):
    """
    Obtiene de forma segura el nombre de una relación.
    """
    related_object = getattr(
        instance,
        relation_name,
        None,
    )

    if related_object is None:
        return None

    name = getattr(
        related_object,
        "nombre",
        None,
    )

    if name is None:
        return None

    normalized_name = _normalize_single_line(
        name,
        allow_blank=True,
    )

    return normalized_name or None


# ============================================================
# MIXIN COMÚN
# ============================================================

class NombreCatalogoSerializerMixin:
    """
    Normalización compartida para catálogos con campo nombre.
    """

    def validate_nombre(
        self,
        value,
    ):
        return _normalize_single_line(
            value,
            allow_blank=False,
        )


# ============================================================
# FACULTADES
# ============================================================

class FacultadSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de facultades.
    """

    class Meta:
        model = Facultad

        fields = [
            "id",
            "nombre",
            "siglas",
            "descripcion",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_siglas(
        self,
        value,
    ):
        """
        Normaliza las siglas sin obligar a cambiar su capitalización.
        """
        return _normalize_single_line(
            value,
            allow_blank=True,
        )

    def validate_descripcion(
        self,
        value,
    ):
        """
        Conserva párrafos de la descripción.
        """
        return _normalize_multiline(
            value,
            allow_blank=True,
        )


# ============================================================
# CARRERAS
# ============================================================

class CarreraSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de carreras.

    La facultad se recibe como identificador y se expone también
    mediante facultad_nombre.
    """

    facultad_nombre = serializers.SerializerMethodField(
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

    def get_facultad_nombre(
        self,
        obj,
    ):
        return _related_name(
            obj,
            "facultad",
        )


# ============================================================
# PAÍSES
# ============================================================

class PaisSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de países.
    """

    class Meta:
        model = Pais

        fields = [
            "id",
            "nombre",
        ]

        read_only_fields = [
            "id",
        ]


# ============================================================
# CIUDADES
# ============================================================

class CiudadSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de ciudades.

    El país se recibe como identificador y se expone también
    mediante pais_nombre.
    """

    pais_nombre = serializers.SerializerMethodField(
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

    def get_pais_nombre(
        self,
        obj,
    ):
        return _related_name(
            obj,
            "pais",
        )


# ============================================================
# ÁREAS DE CONOCIMIENTO
# ============================================================

class AreaConocimientoSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de áreas de conocimiento.
    """

    class Meta:
        model = AreaConocimiento

        fields = [
            "id",
            "nombre",
        ]

        read_only_fields = [
            "id",
        ]


# ============================================================
# SUBÁREAS
# ============================================================

class SubareaConocimientoSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de subáreas de conocimiento.

    El área se recibe como identificador y se expone también
    mediante area_nombre.
    """

    area_nombre = serializers.SerializerMethodField(
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

    def get_area_nombre(
        self,
        obj,
    ):
        return _related_name(
            obj,
            "area",
        )