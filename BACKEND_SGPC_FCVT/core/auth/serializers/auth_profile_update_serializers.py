"""
Serializer para actualización controlada del perfil.

Permite modificar:

- Nombres y apellidos, únicamente para autores externos locales.
- Cédula de 10 dígitos.
- Carrera institucional.
- Facultad utilizada para validar la carrera.
- Tiempo de aplazamiento del aviso de perfil.

Los nombres de usuarios institucionales no se editan aquí porque
provienen de Microsoft 365.

La facultad no se almacena directamente en Usuario. Se deriva
exclusivamente desde usuario.carrera.facultad.
"""

import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from core.models import Carrera


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_INSTITUTIONAL = "autor"
ROLE_EXTERNAL = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"

CEDULA_PATTERN = re.compile(r"^\d{10}$")
MAX_NAME_LENGTH = 100


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """Normaliza un valor textual y elimina espacios repetidos."""
    return " ".join(
        str(value or "").split()
    )


def _normalize_optional_text(value):
    """Normaliza un texto opcional."""
    normalized = _normalize_text(value)
    return normalized or None


def _normalized_role(user):
    return _normalize_text(
        getattr(user, "rol", "")
    ).lower()


def _normalized_auth_source(user):
    return _normalize_text(
        getattr(user, "auth_source", "")
    ).lower()


def _is_external_user(user):
    """
    Una cuenta es externa únicamente cuando:

    - rol = autor_externo
    - auth_source = local
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user) == ROLE_EXTERNAL
        and _normalized_auth_source(user) == AUTH_SOURCE_LOCAL
    )


def _is_institutional_user(user):
    """
    Una cuenta es institucional únicamente cuando:

    - rol = autor
    - auth_source = microsoft
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user) == ROLE_INSTITUTIONAL
        and _normalized_auth_source(user) == AUTH_SOURCE_MICROSOFT
    )


# ============================================================
# SERIALIZER
# ============================================================

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Actualiza los datos editables del perfil.

    Reglas:

    - El autor externo puede corregir nombres, apellidos y cédula.
    - El usuario institucional puede completar cédula y carrera.
    - Los nombres institucionales continúan administrados por
      Microsoft 365.
    - El autor externo nunca puede tener Facultad ni Carrera.

    Los nombres facultad_set y carrera_set se conservan para no
    romper el contrato actual del frontend.
    """

    nombres = serializers.CharField(
        required=False,
        allow_blank=False,
        trim_whitespace=True,
        max_length=MAX_NAME_LENGTH,
        error_messages={
            "blank": "Los nombres son obligatorios.",
            "max_length": (
                "Los nombres no pueden superar "
                f"los {MAX_NAME_LENGTH} caracteres."
            ),
        },
    )

    apellidos = serializers.CharField(
        required=False,
        allow_blank=False,
        trim_whitespace=True,
        max_length=MAX_NAME_LENGTH,
        error_messages={
            "blank": "Los apellidos son obligatorios.",
            "max_length": (
                "Los apellidos no pueden superar "
                f"los {MAX_NAME_LENGTH} caracteres."
            ),
        },
    )

    identificacion = serializers.CharField(
        required=False,
        allow_null=False,
        allow_blank=False,
        trim_whitespace=True,
        min_length=10,
        max_length=10,
        error_messages={
            "null": "El número de cédula es obligatorio.",
            "blank": "El número de cédula es obligatorio.",
            "min_length": (
                "La cédula debe contener exactamente "
                "10 dígitos numéricos."
            ),
            "max_length": (
                "La cédula debe contener exactamente "
                "10 dígitos numéricos."
            ),
        },
    )

    facultad_set = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        write_only=True,
    )

    carrera_set = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        write_only=True,
    )

    snooze_hours = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=24,
        write_only=True,
        error_messages={
            "invalid": "Las horas deben ser un número entero.",
            "min_value": "Las horas deben ser mayores a 0.",
            "max_value": "El máximo permitido es 24 horas.",
        },
    )

    class Meta:
        model = User

        fields = [
            "nombres",
            "apellidos",
            "identificacion",
            "facultad_set",
            "carrera_set",
            "snooze_hours",
        ]

    # ========================================================
    # NOMBRES Y APELLIDOS
    # ========================================================

    def validate_nombres(self, value):
        normalized = _normalize_text(value)

        if not normalized:
            raise serializers.ValidationError(
                "Los nombres son obligatorios."
            )

        if len(normalized) > MAX_NAME_LENGTH:
            raise serializers.ValidationError(
                "Los nombres no pueden superar los 100 caracteres."
            )

        return normalized

    def validate_apellidos(self, value):
        normalized = _normalize_text(value)

        if not normalized:
            raise serializers.ValidationError(
                "Los apellidos son obligatorios."
            )

        if len(normalized) > MAX_NAME_LENGTH:
            raise serializers.ValidationError(
                "Los apellidos no pueden superar los 100 caracteres."
            )

        return normalized

    # ========================================================
    # CÉDULA
    # ========================================================

    def validate_identificacion(self, value):
        """
        Exige exactamente 10 dígitos numéricos.

        No aplica validación matemática del dígito verificador.
        """
        normalized = _normalize_optional_text(value)

        if normalized is None:
            raise serializers.ValidationError(
                "El número de cédula es obligatorio."
            )

        if not CEDULA_PATTERN.fullmatch(normalized):
            raise serializers.ValidationError(
                "La cédula debe contener exactamente 10 dígitos numéricos."
            )

        duplicate_query = User.objects.filter(
            identificacion=normalized
        )

        if self.instance is not None:
            duplicate_query = duplicate_query.exclude(
                pk=self.instance.pk
            )

        if duplicate_query.exists():
            raise serializers.ValidationError(
                "Esta cédula ya está registrada."
            )

        return normalized

    # ========================================================
    # VALIDACIÓN GENERAL
    # ========================================================

    def validate(self, attrs):
        """
        Aplica las reglas de edición según el tipo de cuenta y
        valida la relación Carrera-Facultad.
        """
        user = self.instance

        if user is None:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible determinar "
                        "el usuario del perfil."
                    )
                }
            )

        names_were_sent = (
            "nombres" in attrs
            or "apellidos" in attrs
        )

        faculty_was_sent = "facultad_set" in attrs
        career_was_sent = "carrera_set" in attrs

        selected_faculty_id = attrs.get("facultad_set")
        selected_career_id = attrs.get("carrera_set")

        # ====================================================
        # AUTOR EXTERNO LOCAL
        # ====================================================

        if _is_external_user(user):
            if (
                selected_faculty_id is not None
                or selected_career_id is not None
            ):
                raise serializers.ValidationError(
                    {
                        "carrera_set": (
                            "Los autores externos no pueden "
                            "tener una carrera institucional."
                        )
                    }
                )

            attrs["facultad_set"] = None
            attrs["carrera_set"] = None

            return attrs

        # ====================================================
        # CUENTA NO EXTERNA
        # ====================================================

        if names_were_sent:
            raise serializers.ValidationError(
                {
                    "nombres": (
                        "Los nombres y apellidos solo pueden "
                        "editarse desde el perfil de una cuenta "
                        "externa local."
                    )
                }
            )

        # Solo una cuenta institucional Microsoft puede conservar
        # o modificar una relación académica.
        if not _is_institutional_user(user):
            if (
                selected_faculty_id is not None
                or selected_career_id is not None
            ):
                raise serializers.ValidationError(
                    {
                        "carrera_set": (
                            "Solo los usuarios institucionales "
                            "autenticados mediante Microsoft "
                            "pueden tener una carrera asignada."
                        )
                    }
                )

            attrs["facultad_set"] = None
            attrs["carrera_set"] = None

            return attrs

        # ====================================================
        # CARRERA INSTITUCIONAL
        # ====================================================

        career = None

        if career_was_sent:
            if selected_career_id is not None:
                career = (
                    Carrera.objects
                    .select_related("facultad")
                    .filter(pk=selected_career_id)
                    .first()
                )

                if career is None:
                    raise serializers.ValidationError(
                        {
                            "carrera_set": (
                                "La carrera seleccionada no existe."
                            )
                        }
                    )

        elif getattr(user, "carrera_id", None):
            career = (
                Carrera.objects
                .select_related("facultad")
                .filter(pk=user.carrera_id)
                .first()
            )

        if (
            career is not None
            and selected_faculty_id is not None
            and career.facultad_id != selected_faculty_id
        ):
            raise serializers.ValidationError(
                {
                    "carrera_set": (
                        "La carrera seleccionada no pertenece "
                        "a la facultad indicada."
                    )
                }
            )

        # Si cambia solamente la Facultad y la Carrera actual
        # pertenece a otra Facultad, se elimina la Carrera.
        if (
            faculty_was_sent
            and not career_was_sent
            and career is not None
            and (
                selected_faculty_id is None
                or career.facultad_id != selected_faculty_id
            )
        ):
            attrs["carrera_set"] = None

        # La Facultad real siempre se deriva de la Carrera.
        if career_was_sent and career is not None:
            attrs["facultad_set"] = career.facultad_id

        return attrs

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(self, instance, validated_data):
        """
        Actualiza exclusivamente campos reales del modelo.

        facultad_set nunca se asigna al Usuario porque Usuario no
        contiene un campo Facultad.
        """
        update_fields = []

        faculty_was_sent = "facultad_set" in validated_data
        selected_faculty_id = validated_data.pop(
            "facultad_set",
            None,
        )

        career_was_sent = "carrera_set" in validated_data
        selected_career_id = (
            validated_data.pop("carrera_set", None)
            if career_was_sent
            else None
        )

        snooze_hours = validated_data.pop(
            "snooze_hours",
            None,
        )

        # ====================================================
        # AVISO DE PERFIL
        # ====================================================

        if snooze_hours is not None:
            instance.perfil_banner_snooze_until = (
                timezone.now()
                + timedelta(hours=snooze_hours)
            )
            update_fields.append("perfil_banner_snooze_until")

        # ====================================================
        # NOMBRES DEL AUTOR EXTERNO
        # ====================================================

        if _is_external_user(instance):
            if "nombres" in validated_data:
                new_names = validated_data["nombres"]

                if instance.nombres != new_names:
                    instance.nombres = new_names
                    update_fields.append("nombres")

            if "apellidos" in validated_data:
                new_surnames = validated_data["apellidos"]

                if instance.apellidos != new_surnames:
                    instance.apellidos = new_surnames
                    update_fields.append("apellidos")

        # ====================================================
        # CÉDULA
        # ====================================================

        if "identificacion" in validated_data:
            new_identification = validated_data["identificacion"]

            if instance.identificacion != new_identification:
                instance.identificacion = new_identification
                update_fields.append("identificacion")

        # ====================================================
        # CARRERA
        # ====================================================

        if not _is_institutional_user(instance):
            if instance.carrera_id is not None:
                instance.carrera_id = None
                update_fields.append("carrera")

        elif career_was_sent:
            new_career_id = selected_career_id or None

            if instance.carrera_id != new_career_id:
                instance.carrera_id = new_career_id
                update_fields.append("carrera")

        elif faculty_was_sent:
            current_career = getattr(instance, "carrera", None)
            current_faculty_id = getattr(
                current_career,
                "facultad_id",
                None,
            )

            if (
                instance.carrera_id
                and (
                    selected_faculty_id is None
                    or current_faculty_id != selected_faculty_id
                )
            ):
                instance.carrera_id = None
                update_fields.append("carrera")

        # ====================================================
        # GUARDADO
        # ====================================================

        if update_fields:
            instance.save(
                update_fields=list(dict.fromkeys(update_fields))
            )

        return instance