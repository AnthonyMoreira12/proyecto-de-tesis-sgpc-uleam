"""
Serializer para actualización controlada del perfil.

Permite modificar:

- Identificación.
- Carrera institucional.
- Facultad utilizada para validar la carrera.
- Tiempo de aplazamiento del aviso de perfil.

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
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _normalize_optional_text(value):
    """
    Normaliza un texto opcional.
    """
    normalized = _normalize_text(
        value
    )

    return normalized or None


def _is_external_user(user):
    """
    Determina si el usuario es realmente un autor externo.
    """
    if user is None:
        return False

    role = _normalize_text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()

    auth_source = _normalize_text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()

    return bool(
        role == "autor_externo"
        and auth_source == "local"
    )


# ============================================================
# SERIALIZER
# ============================================================

class ProfileUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Actualiza los datos editables del perfil.

    Los nombres facultad_set y carrera_set se conservan para no
    romper el contrato actual del frontend.
    """

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
            "invalid": (
                "Las horas deben ser un número entero."
            ),
            "min_value": (
                "Las horas deben ser mayores a 0."
            ),
            "max_value": (
                "El máximo permitido es 24 horas."
            ),
        },
    )

    class Meta:
        model = User

        fields = [
            "identificacion",
            "facultad_set",
            "carrera_set",
            "snooze_hours",
        ]

        extra_kwargs = {
            "identificacion": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
                "trim_whitespace": True,
            },
        }

    # ========================================================
    # IDENTIFICACIÓN
    # ========================================================

    def validate_identificacion(
        self,
        value,
    ):
        """
        Admite cédula, pasaporte u otra identificación.

        Se permiten entre 3 y 20 caracteres alfanuméricos,
        además de punto, guion, barra y guion bajo.
        """
        normalized = _normalize_optional_text(
            value
        )

        if normalized is None:
            return None

        if len(normalized) > 20:
            raise serializers.ValidationError(
                (
                    "La identificación no puede superar "
                    "los 20 caracteres."
                )
            )

        if not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._/-]{2,19}",
            normalized,
        ):
            raise serializers.ValidationError(
                (
                    "La identificación debe contener entre "
                    "3 y 20 caracteres alfanuméricos. "
                    "Puede incluir punto, guion, barra "
                    "o guion bajo."
                )
            )

        duplicate_query = (
            User.objects.filter(
                identificacion__iexact=normalized
            )
        )

        if self.instance is not None:
            duplicate_query = (
                duplicate_query.exclude(
                    pk=self.instance.pk
                )
            )

        if duplicate_query.exists():
            raise serializers.ValidationError(
                (
                    "Esta identificación ya está "
                    "registrada."
                )
            )

        return normalized

    # ========================================================
    # VALIDACIÓN GENERAL
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        """
        Valida la relación carrera-facultad.

        facultad_set se utiliza únicamente para comprobar que la
        carrera seleccionada pertenece a la facultad elegida.
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

        faculty_was_sent = (
            "facultad_set"
            in attrs
        )

        career_was_sent = (
            "carrera_set"
            in attrs
        )

        selected_faculty_id = attrs.get(
            "facultad_set"
        )

        selected_career_id = attrs.get(
            "carrera_set"
        )

        # ====================================================
        # AUTOR EXTERNO
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
        # CARRERA
        # ====================================================

        career = None

        if career_was_sent:
            if selected_career_id is not None:
                career = (
                    Carrera.objects
                    .select_related(
                        "facultad"
                    )
                    .filter(
                        pk=selected_career_id
                    )
                    .first()
                )

                if career is None:
                    raise serializers.ValidationError(
                        {
                            "carrera_set": (
                                "La carrera seleccionada "
                                "no existe."
                            )
                        }
                    )

        elif getattr(
            user,
            "carrera_id",
            None,
        ):
            career = (
                Carrera.objects
                .select_related(
                    "facultad"
                )
                .filter(
                    pk=user.carrera_id
                )
                .first()
            )

        # ====================================================
        # VALIDACIÓN DE FACULTAD
        # ====================================================

        if (
            career is not None
            and selected_faculty_id is not None
            and career.facultad_id
            != selected_faculty_id
        ):
            raise serializers.ValidationError(
                {
                    "carrera_set": (
                        "La carrera seleccionada no pertenece "
                        "a la facultad indicada."
                    )
                }
            )

        # Si se cambia solamente la facultad y la carrera actual
        # pertenece a otra facultad, se elimina la carrera.
        if (
            faculty_was_sent
            and not career_was_sent
            and career is not None
            and (
                selected_faculty_id is None
                or career.facultad_id
                != selected_faculty_id
            )
        ):
            attrs["carrera_set"] = None

        # Cuando se selecciona una carrera, la facultad real se
        # obtiene desde carrera.facultad.
        if career_was_sent and career is not None:
            attrs["facultad_set"] = (
                career.facultad_id
            )

        return attrs

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza exclusivamente campos reales del modelo.

        facultad_set nunca se asigna al usuario porque Usuario no
        contiene un campo facultad.
        """
        update_fields = []

        faculty_was_sent = (
            "facultad_set"
            in validated_data
        )

        selected_faculty_id = (
            validated_data.pop(
                "facultad_set",
                None,
            )
        )

        career_was_sent = (
            "carrera_set"
            in validated_data
        )

        selected_career_id = (
            validated_data.pop(
                "carrera_set",
                None,
            )
            if career_was_sent
            else None
        )

        snooze_hours = (
            validated_data.pop(
                "snooze_hours",
                None,
            )
        )

        # ====================================================
        # AVISO DE PERFIL
        # ====================================================

        if snooze_hours is not None:
            instance.perfil_banner_snooze_until = (
                timezone.now()
                + timedelta(
                    hours=snooze_hours
                )
            )

            update_fields.append(
                "perfil_banner_snooze_until"
            )

        # ====================================================
        # IDENTIFICACIÓN
        # ====================================================

        if "identificacion" in validated_data:
            new_identification = (
                validated_data[
                    "identificacion"
                ]
            )

            if (
                instance.identificacion
                != new_identification
            ):
                instance.identificacion = (
                    new_identification
                )

                update_fields.append(
                    "identificacion"
                )

        # ====================================================
        # CARRERA
        # ====================================================

        if _is_external_user(instance):
            if instance.carrera_id is not None:
                instance.carrera_id = None

                update_fields.append(
                    "carrera"
                )

        elif career_was_sent:
            new_career_id = (
                selected_career_id
                or None
            )

            if (
                instance.carrera_id
                != new_career_id
            ):
                instance.carrera_id = (
                    new_career_id
                )

                update_fields.append(
                    "carrera"
                )

        elif faculty_was_sent:
            current_career = getattr(
                instance,
                "carrera",
                None,
            )

            current_faculty_id = getattr(
                current_career,
                "facultad_id",
                None,
            )

            if (
                instance.carrera_id
                and (
                    selected_faculty_id is None
                    or current_faculty_id
                    != selected_faculty_id
                )
            ):
                instance.carrera_id = None

                update_fields.append(
                    "carrera"
                )

        # ====================================================
        # GUARDADO
        # ====================================================

        if update_fields:
            instance.save(
                update_fields=list(
                    dict.fromkeys(
                        update_fields
                    )
                )
            )

        return instance