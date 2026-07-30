"""
Serializer para el registro público de usuarios externos.

Responsabilidades:

- Normalizar el correo, los nombres y los apellidos.
- Exigir una cédula de exactamente 10 dígitos numéricos.
- Validar la contraseña mediante las reglas configuradas
  en Django.
- Evitar correos y cédulas duplicados.
- Impedir que los correos institucionales se registren como
  cuentas externas locales.
- Crear exclusivamente usuarios externos locales.
- Impedir que el cliente asigne Carrera o privilegios
  administrativos.
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

from core.auth.services.auth_microsoft_services import (
    is_allowed_institutional_email,
)


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_EXTERNAL = "autor_externo"
AUTH_SOURCE_LOCAL = "local"

CEDULA_PATTERN = re.compile(
    r"^\d{10}$"
)

MAX_EMAIL_LENGTH = 150
MAX_NAME_LENGTH = 100

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza los espacios de nombres y apellidos.

    Convierte espacios repetidos, tabulaciones y saltos de línea
    en un solo espacio.
    """
    return " ".join(
        str(
            value or ""
        ).split()
    )


def _normalize_email(value):
    """
    Normaliza un correo mediante el manager del modelo.
    """
    normalized = (
        User.objects.normalize_email(
            str(
                value or ""
            )
        )
        .strip()
        .lower()
    )

    return normalized


def _normalize_cedula(value):
    """
    Normaliza la cédula sin alterar sus dígitos.
    """
    return str(
        value or ""
    ).strip()


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
        "detail": str(
            exc
        )
    }


def _role_external_value():
    """
    Obtiene el valor del rol externo conservando compatibilidad
    con el modelo que utiliza TextChoices.
    """
    role_choices = getattr(
        User,
        "Rol",
        None,
    )

    if role_choices is not None:
        return getattr(
            role_choices,
            "AUTOR_EXTERNO",
            ROLE_EXTERNAL,
        )

    return ROLE_EXTERNAL


def _local_auth_source_value():
    """
    Obtiene el valor del origen local conservando compatibilidad
    con el modelo que utiliza TextChoices.
    """
    auth_choices = getattr(
        User,
        "AuthSource",
        None,
    )

    if auth_choices is not None:
        return getattr(
            auth_choices,
            "LOCAL",
            AUTH_SOURCE_LOCAL,
        )

    return AUTH_SOURCE_LOCAL


# ============================================================
# SERIALIZER
# ============================================================

class RegisterSerializer(
    serializers.ModelSerializer
):
    """
    Registra exclusivamente autores externos locales.

    El cliente únicamente puede enviar:

    - email
    - nombres
    - apellidos
    - identificacion
    - password

    Los siguientes valores son controlados por el backend:

    - rol
    - auth_source
    - carrera
    - is_active
    - is_staff
    - is_superuser
    - perfil_completo
    - creado_desde_selector
    """

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=MAX_EMAIL_LENGTH,

        # Se desactiva el UniqueValidator automático para
        # controlar el mensaje y comprobar sin distinguir
        # mayúsculas y minúsculas.
        validators=[],

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
                f"los {MAX_EMAIL_LENGTH} caracteres."
            ),
        },
    )

    nombres = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=MAX_NAME_LENGTH,
        error_messages={
            "required": (
                "Los nombres son obligatorios."
            ),
            "blank": (
                "Los nombres son obligatorios."
            ),
            "max_length": (
                "Los nombres no pueden superar "
                f"los {MAX_NAME_LENGTH} caracteres."
            ),
        },
    )

    apellidos = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=MAX_NAME_LENGTH,
        error_messages={
            "required": (
                "Los apellidos son obligatorios."
            ),
            "blank": (
                "Los apellidos son obligatorios."
            ),
            "max_length": (
                "Los apellidos no pueden superar "
                f"los {MAX_NAME_LENGTH} caracteres."
            ),
        },
    )

    identificacion = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        trim_whitespace=True,
        min_length=10,
        max_length=10,

        # La unicidad se comprueba manualmente para controlar
        # el mensaje y proteger el flujo ante datos antiguos.
        validators=[],

        error_messages={
            "required": (
                "El número de cédula es obligatorio."
            ),
            "null": (
                "El número de cédula es obligatorio."
            ),
            "blank": (
                "El número de cédula es obligatorio."
            ),
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

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
        trim_whitespace=False,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
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
                "La contraseña debe contener al menos "
                f"{MIN_PASSWORD_LENGTH} caracteres."
            ),
            "max_length": (
                "La contraseña no puede superar "
                f"los {MAX_PASSWORD_LENGTH} caracteres."
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

    # ========================================================
    # CORREO
    # ========================================================

    def validate_email(
        self,
        value,
    ):
        """
        Normaliza el correo y comprueba:

        - Formato válido.
        - Que no corresponda al acceso Microsoft.
        - Que no exista otro usuario con el mismo correo.
        """
        normalized_email = _normalize_email(
            value
        )

        if not normalized_email:
            raise serializers.ValidationError(
                "El correo electrónico es obligatorio."
            )

        if len(
            normalized_email
        ) > MAX_EMAIL_LENGTH:
            raise serializers.ValidationError(
                (
                    "El correo electrónico no puede superar "
                    f"los {MAX_EMAIL_LENGTH} caracteres."
                )
            )

        if is_allowed_institutional_email(
            normalized_email
        ):
            raise serializers.ValidationError(
                (
                    "Las cuentas institucionales deben iniciar "
                    "sesión mediante Microsoft 365 y no pueden "
                    "registrarse como cuentas externas."
                )
            )

        if User.objects.filter(
            email__iexact=normalized_email
        ).exists():
            raise serializers.ValidationError(
                (
                    "Ya existe un usuario registrado con "
                    "este correo electrónico."
                )
            )

        return normalized_email

    # ========================================================
    # NOMBRES Y APELLIDOS
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

        if len(
            normalized_names
        ) > MAX_NAME_LENGTH:
            raise serializers.ValidationError(
                (
                    "Los nombres no pueden superar "
                    f"los {MAX_NAME_LENGTH} caracteres."
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

        if len(
            normalized_surnames
        ) > MAX_NAME_LENGTH:
            raise serializers.ValidationError(
                (
                    "Los apellidos no pueden superar "
                    f"los {MAX_NAME_LENGTH} caracteres."
                )
            )

        return normalized_surnames

    # ========================================================
    # CÉDULA
    # ========================================================

    def validate_identificacion(
        self,
        value,
    ):
        """
        Valida únicamente el formato acordado:

        - Obligatoria.
        - Exactamente 10 caracteres.
        - Únicamente números.

        No aplica validación matemática del dígito verificador.
        """
        normalized_cedula = _normalize_cedula(
            value
        )

        if not normalized_cedula:
            raise serializers.ValidationError(
                "El número de cédula es obligatorio."
            )

        if not CEDULA_PATTERN.fullmatch(
            normalized_cedula
        ):
            raise serializers.ValidationError(
                (
                    "La cédula debe contener exactamente "
                    "10 dígitos numéricos."
                )
            )

        if User.objects.filter(
            identificacion=normalized_cedula
        ).exists():
            raise serializers.ValidationError(
                "Esta cédula ya está registrada."
            )

        return normalized_cedula

    # ========================================================
    # VALIDACIÓN GENERAL
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        """
        Valida la contraseña considerando los datos reales del
        usuario externo que se creará.
        """
        password = attrs.get(
            "password"
        )

        if password is None:
            raise serializers.ValidationError(
                {
                    "password": (
                        "La contraseña es obligatoria."
                    )
                }
            )

        password = str(
            password
        )

        if not password:
            raise serializers.ValidationError(
                {
                    "password": (
                        "La contraseña es obligatoria."
                    )
                }
            )

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

            rol=_role_external_value(),

            auth_source=(
                _local_auth_source_value()
            ),

            carrera=None,

            is_active=True,

            is_staff=False,

            is_superuser=False,
        )

        try:
            validate_password(
                password,
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
        Crea el usuario externo activo.

        Este serializer pertenece al registro público, donde el
        propio usuario establece su contraseña y el RegisterView
        genera inmediatamente su sesión JWT.

        La creación administrativa utiliza otro flujo y conserva
        la cuenta inactiva hasta su activación.
        """
        password = validated_data.pop(
            "password"
        )

        user_data = {
            "email": validated_data[
                "email"
            ],

            "nombres": validated_data[
                "nombres"
            ],

            "apellidos": validated_data[
                "apellidos"
            ],

            "identificacion": (
                validated_data[
                    "identificacion"
                ]
            ),

            "rol": (
                _role_external_value()
            ),

            "auth_source": (
                _local_auth_source_value()
            ),

            # Los usuarios externos nunca reciben una Carrera.
            "carrera": None,

            # El registro público incluye contraseña y devuelve
            # una sesión, por lo que la cuenta queda activa.
            "is_active": True,

            # Nunca se aceptan privilegios enviados por el
            # cliente.
            "is_staff": False,

            "is_superuser": False,

            "creado_desde_selector": False,

            # La cédula es obligatoria y válida en este punto.
            "perfil_completo": True,
        }

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    password=password,
                    **user_data,
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

            cedula = user_data.get(
                "identificacion"
            )

            # La comprobación se realiza después de salir del
            # bloque atomic(), cuando la transacción ya puede
            # consultarse nuevamente.
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
                cedula
                and User.objects.filter(
                    identificacion=cedula
                ).exists()
            ):
                raise serializers.ValidationError(
                    {
                        "identificacion": (
                            "Esta cédula ya está registrada."
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