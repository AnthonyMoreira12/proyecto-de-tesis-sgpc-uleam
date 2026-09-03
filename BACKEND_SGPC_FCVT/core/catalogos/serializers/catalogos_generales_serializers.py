"""
Serializers de los catálogos generales del sistema.

Este módulo gestiona:

- Sedes.
- Facultades.
- Carreras.
- Países.
- Ciudades.
- Áreas de conocimiento.
- Subáreas de conocimiento.

Los serializers normalizan textos antes de guardar y exponen
de forma segura los nombres de las relaciones utilizadas por
formularios, filtros y listados.

Para las áreas y subáreas de conocimiento también se conserva
el código oficial UNESCO como información estructurada.
"""

import unicodedata

from rest_framework import serializers

from core.models import (
    AreaConocimiento,
    Carrera,
    Ciudad,
    Facultad,
    Pais,
    Sede,
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


def _normalize_codigo(
    value,
    *,
    length,
    label,
):
    """
    Normaliza y valida códigos numéricos de catálogos UNESCO.

    Los códigos se conservan como texto para mantener
    correctamente los ceros iniciales:

        "01"
        "05"
        "061"
    """
    if value is None:
        raise serializers.ValidationError(
            f"El código de {label} no puede ser nulo."
        )

    codigo = str(
        value
    ).strip()

    if not codigo:
        raise serializers.ValidationError(
            f"El código de {label} es obligatorio."
        )

    if (
        len(codigo) != length
        or not codigo.isdigit()
    ):
        raise serializers.ValidationError(
            f"El código de {label} debe contener "
            f"exactamente {length} dígitos."
        )

    return codigo


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
# SEDES
# ============================================================

class SedeSerializer(
    NombreCatalogoSerializerMixin,
    serializers.ModelSerializer,
):
    """
    Serializer de sedes institucionales.

    El código se normaliza en minúsculas para conservar el mismo
    contrato definido por el modelo Sede.
    """

    class Meta:
        model = Sede

        fields = [
            "id",
            "nombre",
            "codigo",
            "ciudad",
            "descripcion",
            "activa",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_codigo(
        self,
        value,
    ):
        return _normalize_single_line(
            value,
            allow_blank=False,
        ).lower()

    def validate_ciudad(
        self,
        value,
    ):
        return _normalize_single_line(
            value,
            allow_blank=True,
        )

    def validate_descripcion(
        self,
        value,
    ):
        return _normalize_multiline(
            value,
            allow_blank=True,
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

    El código UNESCO se conserva como texto para mantener
    correctamente los ceros iniciales.
    """

    class Meta:
        model = AreaConocimiento

        fields = [
            "id",
            "codigo",
            "nombre",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_codigo(
        self,
        value,
    ):
        """
        Valida códigos UNESCO de área amplia.

        Ejemplos válidos:

            00
            01
            05
            06
            10
        """
        return _normalize_codigo(
            value,
            length=2,
            label="área",
        )


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

    El código de la subárea debe conservar la jerarquía
    establecida por el área UNESCO.
    """

    area_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Subarea

        fields = [
            "id",
            "codigo",
            "nombre",
            "area",
            "area_nombre",
        ]

        read_only_fields = [
            "id",
            "area_nombre",
        ]

    def validate_codigo(
        self,
        value,
    ):
        """
        Valida códigos UNESCO de subárea.

        Ejemplos válidos:

            011
            051
            052
            061
            091
        """
        return _normalize_codigo(
            value,
            length=3,
            label="subárea",
        )

    def validate(
        self,
        attrs,
    ):
        attrs = super().validate(
            attrs
        )

        instance = getattr(
            self,
            "instance",
            None,
        )

        codigo = attrs.get(
            "codigo",
            getattr(
                instance,
                "codigo",
                None,
            )
            if instance is not None
            else None,
        )

        area = attrs.get(
            "area",
            getattr(
                instance,
                "area",
                None,
            )
            if instance is not None
            else None,
        )

        if (
            codigo
            and area is not None
        ):
            area_codigo = str(
                getattr(
                    area,
                    "codigo",
                    "",
                )
                or ""
            ).strip()

            if (
                area_codigo
                and not codigo.startswith(
                    area_codigo
                )
            ):
                raise serializers.ValidationError(
                    {
                        "codigo": [
                            "El código de la subárea no "
                            "corresponde al área seleccionada."
                        ]
                    }
                )

        return attrs

    def get_area_nombre(
        self,
        obj,
    ):
        return _related_name(
            obj,
            "area",
        )