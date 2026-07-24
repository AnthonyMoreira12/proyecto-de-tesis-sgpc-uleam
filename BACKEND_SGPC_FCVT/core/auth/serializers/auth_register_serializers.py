"""
Serializer para el registro público de usuarios externos.

Responsabilidades:

- Normalizar correo, nombres, apellidos e identificación.
- Validar la contraseña mediante las reglas de Django.
- Evitar correos e identificaciones duplicadas.
- Crear únicamente usuarios externos con autenticación local.
- Impedir que el cliente asigne privilegios administrativos.
- Ejecutar la creación dentro de una transacción.
"""

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from rest_framework import serializers


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

IDENTIFICATION_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._/-]{2,19}$"
)


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza espacios externos e internos.

    También evita que saltos de línea o tabulaciones queden
    almacenados dentro de nombres y apellidos.
    """
    return " ".join(
        str(value or "").split()
    )


def _normalize_optional_text(value):
    """
    Normaliza un texto opcional.
    """
    normalized = str(
        value or ""
    ).strip()

    return normalized or None


def _normalize_email(value):
    """
    Normaliza el correo utilizando el manager del modelo.
    """
    normalized = User.objects.normalize_email(
        str(value or "")
    )

    return normalized.strip().lower()


def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": str(exc),
    }


# ============================================================
# SERIALIZER
# ============================================================

class RegisterSerializer(
    serializers.ModelSerializer
):
    """
    Registra exclusivamente autores externos locales.

    El cliente no puede definir:

    - rol
    - auth_source
    - carrera
    - is_staff
    - is_superuser
    - perfil_completo

    Estos valores se determinan de forma segura en create().
    """

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        min_length=8,
        max_length=128,
        style={
            "input_type": "password",
        },
        error_messages={
            "required": (
                "La contraseña es obligatoria."
            ),
            "blank": (
                "La contraseña es obligatoria."
            ),
            "min_length": (
                "La contraseña debe contener "
                "al menos 8 caracteres."
            ),
            "max_length": (
                "La contraseña no puede superar "
                "los 128 caracteres."
            ),
        },
    )

    class Meta:
        model = User

        fields = [
            "email",
            "nombres",
            "apellidos",
            "identificacion",
            "password",
        ]

        extra_kwargs = {
            "email": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },

            "nombres": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },

            "apellidos": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },

            "identificacion": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
                "trim_whitespace": True,
            },
        }

    # ========================================================
    # CORREO
    # ========================================================

    def validate_email(
        self,
        value,
    ):
        """
        Normaliza el correo y comprueba duplicados ignorando
        mayúsculas y minúsculas.
        """
        normalized_email = _normalize_email(
            value
        )

        if not normalized_email:
            raise serializers.ValidationError(
                (
                    "El correo electrónico "
                    "es obligatorio."
                )
            )

        if User.objects.filter(
            email__iexact=normalized_email
        ).exists():
            raise serializers.ValidationError(
                (
                    "Ya existe un usuario registrado "
                    "con este correo electrónico."
                )
            )

        return normalized_email

    # ========================================================
    # NOMBRES
    # ========================================================

    def validate_nombres(
        self,
        value,
    ):
        normalized_names = _normalize_text(
            value
        )

        if not normalized_names:
            raise serializers.ValidationError(
                "Los nombres son obligatorios."
            )

        if len(normalized_names) > 100:
            raise serializers.ValidationError(
                (
                    "Los nombres no pueden superar "
                    "los 100 caracteres."
                )
            )

        return normalized_names

    def validate_apellidos(
        self,
        value,
    ):
        normalized_surnames = _normalize_text(
            value
        )

        if not normalized_surnames:
            raise serializers.ValidationError(
                "Los apellidos son obligatorios."
            )

        if len(normalized_surnames) > 100:
            raise serializers.ValidationError(
                (
                    "Los apellidos no pueden superar "
                    "los 100 caracteres."
                )
            )

        return normalized_surnames

    # ========================================================
    # IDENTIFICACIÓN
    # ========================================================

    def validate_identificacion(
        self,
        value,
    ):
        """
        Admite cédulas, pasaportes y otros documentos.

        Formato permitido:

        - Entre 3 y 20 caracteres.
        - Letras y números.
        - Punto.
        - Guion.
        - Barra.
        - Guion bajo.
        """
        normalized_identification = (
            _normalize_optional_text(
                value
            )
        )

        if normalized_identification is None:
            return None

        if len(
            normalized_identification
        ) > 20:
            raise serializers.ValidationError(
                (
                    "La identificación no puede superar "
                    "los 20 caracteres."
                )
            )

        if not IDENTIFICATION_PATTERN.fullmatch(
            normalized_identification
        ):
            raise serializers.ValidationError(
                (
                    "La identificación debe contener entre "
                    "3 y 20 caracteres alfanuméricos. "
                    "También puede incluir punto, guion, "
                    "barra o guion bajo."
                )
            )

        if User.objects.filter(
            identificacion__iexact=(
                normalized_identification
            )
        ).exists():
            raise serializers.ValidationError(
                (
                    "Esta identificación ya está "
                    "registrada."
                )
            )

        return normalized_identification

    # ========================================================
    # VALIDACIÓN GENERAL
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        """
        Valida la contraseña considerando los datos del usuario
        que se registrará.
        """
        provisional_user = User(
            email=attrs.get(
                "email"
            ),

            nombres=attrs.get(
                "nombres",
                "",
            ),

            apellidos=attrs.get(
                "apellidos",
                "",
            ),

            identificacion=attrs.get(
                "identificacion"
            ),

            rol=User.Rol.AUTOR_EXTERNO,

            auth_source=(
                User.AuthSource.LOCAL
            ),

            carrera=None,

            is_active=True,

            is_staff=False,

            is_superuser=False,
        )

        try:
            validate_password(
                attrs["password"],
                user=provisional_user,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {
                    "password": list(
                        exc.messages
                    )
                }
            ) from exc

        return attrs

    # ========================================================
    # CREACIÓN
    # ========================================================

    def create(
        self,
        validated_data,
    ):
        """
        Crea el usuario externo dentro de una transacción.

        Los valores sensibles se fuerzan desde el backend y no
        pueden ser definidos por el cliente.
        """
        password = validated_data.pop(
            "password"
        )

        identification = (
            validated_data.get(
                "identificacion"
            )
        )

        user_data = {
            **validated_data,

            "rol": (
                User.Rol.AUTOR_EXTERNO
            ),

            "auth_source": (
                User.AuthSource.LOCAL
            ),

            "carrera": None,

            "is_active": True,

            "is_staff": False,

            "is_superuser": False,

            "creado_desde_selector": False,

            # Para un autor externo, el perfil se considera
            # completo cuando posee identificación.
            "perfil_completo": bool(
                identification
            ),
        }

        try:
            with transaction.atomic():
                user = (
                    User.objects.create_user(
                        password=password,
                        **user_data,
                    )
                )

                return user

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except ValueError as exc:
            raise serializers.ValidationError(
                {
                    "detail": str(
                        exc
                    )
                }
            ) from exc

        except IntegrityError as exc:
            email = user_data.get(
                "email"
            )

            identification = user_data.get(
                "identificacion"
            )

            if (
                email
                and User.objects.filter(
                    email__iexact=email
                ).exists()
            ):
                raise serializers.ValidationError(
                    {
                        "email": (
                            "Ya existe un usuario registrado "
                            "con este correo electrónico."
                        )
                    }
                ) from exc

            if (
                identification
                and User.objects.filter(
                    identificacion__iexact=(
                        identification
                    )
                ).exists()
            ):
                raise serializers.ValidationError(
                    {
                        "identificacion": (
                            "Esta identificación ya está "
                            "registrada."
                        )
                    }
                ) from exc

            raise serializers.ValidationError(
                {
                    "detail": (
                        "No se pudo completar el registro "
                        "debido a un conflicto de integridad."
                    )
                }
            ) from exc