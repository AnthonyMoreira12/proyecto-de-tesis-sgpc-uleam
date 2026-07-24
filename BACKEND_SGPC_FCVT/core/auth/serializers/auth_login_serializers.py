"""
Serializer para el inicio de sesión local.

Responsabilidades:

- Validar el correo electrónico.
- Normalizar el correo antes de autenticar.
- Validar que la contraseña no esté vacía.
- Limitar el tamaño de los datos recibidos.
- Mantener la contraseña como campo de solo escritura.

La comprobación real de las credenciales se realiza en LoginView
mediante django.contrib.auth.authenticate().
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_email(value):
    """
    Normaliza el correo utilizando el manager del modelo.

    El dominio se normaliza y el valor completo se convierte
    a minúsculas para conservar el comportamiento actual del
    sistema.
    """
    normalized = User.objects.normalize_email(
        str(value or "")
    )

    return normalized.strip().lower()


# ============================================================
# SERIALIZER
# ============================================================

class LoginSerializer(serializers.Serializer):
    """
    Valida los datos necesarios para iniciar sesión mediante
    autenticación local.

    Este serializer no autentica al usuario ni genera tokens.
    """

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=150,
        trim_whitespace=True,
        error_messages={
            "required": (
                "El correo electrónico es obligatorio."
            ),
            "blank": (
                "El correo electrónico es obligatorio."
            ),
            "invalid": (
                "Ingrese un correo electrónico válido."
            ),
            "max_length": (
                "El correo electrónico no puede superar "
                "los 150 caracteres."
            ),
        },
    )

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
        trim_whitespace=False,
        min_length=1,
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
            "max_length": (
                "La contraseña no puede superar "
                "los 128 caracteres."
            ),
        },
    )

    def validate_email(self, value):
        """
        Normaliza el correo antes de entregarlo a LoginView.
        """
        normalized_email = _normalize_email(
            value
        )

        if not normalized_email:
            raise serializers.ValidationError(
                "El correo electrónico es obligatorio."
            )

        return normalized_email

    def validate_password(self, value):
        """
        Rechaza contraseñas vacías sin modificar espacios
        intencionales que formen parte de la contraseña.
        """
        if value is None or value == "":
            raise serializers.ValidationError(
                "La contraseña es obligatoria."
            )

        return value