"""Servicios administrativos para usuarios."""

import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.core.validators import validate_email
from django.db.models import Q
from django.utils import timezone


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_INSTITUTIONAL = "autor"
ROLE_EXTERNAL = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"

CEDULA_PATTERN = re.compile(r"^\d{10}$")

PROFILE_EDIT_DEFAULT_HOURS = 48
PROFILE_EDIT_DEFAULT_ATTEMPTS = 3


# ============================================================
# EXCEPCIÓN DEL SERVICIO
# ============================================================

class AdminUsuariosServiceError(Exception):
    """
    Error controlado producido por las reglas administrativas
    de usuarios.
    """

    def __init__(
        self,
        detail,
        *,
        status_code=400,
    ):
        self.detail = detail
        self.status_code = status_code

        super().__init__(
            str(detail)
        )


# ============================================================
# UTILIDADES
# ============================================================

def _text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _normalize_email(value):
    """
    Normaliza un correo mediante el manager del modelo Usuario.
    """
    return (
        User.objects.normalize_email(
            str(
                value or ""
            )
        )
        .strip()
        .lower()
    )


def _normalized_role(user):
    """
    Obtiene el rol normalizado del usuario.
    """
    return _text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()


def _normalized_auth_source(user):
    """
    Obtiene el origen de autenticación normalizado.
    """
    return _text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()


def _is_external_user(user):
    """
    Determina si el usuario es un autor externo local.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_EXTERNAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_LOCAL
    )


def _is_institutional_user(user):
    """
    Determina si el usuario es institucional Microsoft.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_INSTITUTIONAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_MICROSOFT
    )


def _has_valid_cedula(user):
    """
    Comprueba que el usuario tenga una cédula de exactamente
    10 dígitos numéricos.
    """
    cedula = _text(
        getattr(
            user,
            "identificacion",
            "",
        )
    )

    return bool(
        CEDULA_PATTERN.fullmatch(
            cedula
        )
    )


def _is_admin(user):
    """
    Comprueba si el usuario posee privilegios administrativos.
    """
    if user is None:
        return False

    return bool(
        getattr(
            user,
            "is_staff",
            False,
        )
        or getattr(
            user,
            "is_superuser",
            False,
        )
    )


def _append_field(
    fields,
    field_name,
):
    """
    Agrega un campo a update_fields evitando duplicados.
    """
    if field_name not in fields:
        fields.append(
            field_name
        )


# ============================================================
# CONVERSIÓN DE BOOLEANOS
# ============================================================

def parse_bool(
    value,
    *,
    default=None,
):
    """
    Convierte valores comunes en un booleano seguro.
    """
    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return value

    normalized = _text(
        value
    ).lower()

    if normalized in {
        "1",
        "true",
        "yes",
        "y",
        "on",
        "si",
        "sí",
    }:
        return True

    if normalized in {
        "0",
        "false",
        "no",
        "n",
        "off",
    }:
        return False

    raise AdminUsuariosServiceError(
        {
            "detail": (
                "El valor debe ser verdadero "
                "o falso."
            )
        }
    )


# ============================================================
# PROTECCIÓN ADMINISTRATIVA
# ============================================================

def validate_admin_guard(
    target,
    actor,
    *,
    new_is_active=None,
    new_is_staff=None,
):
    """
    Protege cuentas administrativas críticas.

    Impide:

    - Desactivar un superusuario.
    - Revocar permisos a un superusuario.
    - Retirar el propio acceso administrativo.
    - Retirar al último administrador activo.
    """
    if target is None:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario seleccionado."
                )
            },
            status_code=404,
        )

    if actor is None:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el administrador autenticado."
                )
            },
            status_code=401,
        )

    target_is_superuser = bool(
        getattr(
            target,
            "is_superuser",
            False,
        )
    )

    target_is_staff = bool(
        getattr(
            target,
            "is_staff",
            False,
        )
    )

    target_is_active = bool(
        getattr(
            target,
            "is_active",
            False,
        )
    )

    if target_is_superuser:
        if (
            new_is_active is False
            or new_is_staff is False
        ):
            raise AdminUsuariosServiceError(
                {
                    "detail": (
                        "No se puede desactivar ni revocar "
                        "los permisos de un superusuario."
                    )
                },
                status_code=403,
            )

    same_user = bool(
        getattr(
            target,
            "pk",
            None,
        )
        == getattr(
            actor,
            "pk",
            None,
        )
    )

    if same_user:
        if (
            new_is_active is False
            or new_is_staff is False
        ):
            raise AdminUsuariosServiceError(
                {
                    "detail": (
                        "No puede retirar su propio acceso "
                        "administrativo."
                    )
                },
                status_code=403,
            )

    target_is_admin = bool(
        target_is_staff
        or target_is_superuser
    )

    deactivating_admin = bool(
        target_is_admin
        and target_is_active
        and new_is_active is False
    )

    revoking_admin = bool(
        target_is_staff
        and not target_is_superuser
        and new_is_staff is False
    )

    if (
        deactivating_admin
        or revoking_admin
    ):
        remaining_admin_exists = (
            User.objects
            .filter(
                is_active=True
            )
            .filter(
                Q(
                    is_staff=True
                )
                | Q(
                    is_superuser=True
                )
            )
            .exclude(
                pk=target.pk
            )
            .exists()
        )

        if not remaining_admin_exists:
            raise AdminUsuariosServiceError(
                {
                    "detail": (
                        "No se puede retirar al último "
                        "administrador activo del sistema."
                    )
                },
                status_code=409,
            )


# ============================================================
# ACTIVACIÓN DE USUARIO EXTERNO
# ============================================================

def activate_external_user(
    user,
    *,
    email=None,
    password=None,
):
    """
    Activa exclusivamente una cuenta externa local pendiente.

    Reglas aplicadas:

    - Debe ser rol=autor_externo.
    - Debe utilizar auth_source=local.
    - Debe encontrarse inactiva.
    - Debe poseer una cédula válida de 10 dígitos.
    - El correo es obligatorio y debe ser único.
    - La contraseña es obligatoria.
    - La Carrera se elimina.
    - No se conceden privilegios administrativos.
    """
    if user is None:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario que se activará."
                )
            },
            status_code=404,
        )

    if not _is_external_user(
        user
    ):
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "Solo se pueden activar mediante esta "
                    "operación las cuentas externas locales."
                )
            },
            status_code=400,
        )

    if bool(
        getattr(
            user,
            "is_superuser",
            False,
        )
    ):
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No se puede procesar un superusuario "
                    "mediante la activación de cuentas externas."
                )
            },
            status_code=403,
        )

    if bool(
        getattr(
            user,
            "is_active",
            False,
        )
    ):
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "La cuenta seleccionada ya se "
                    "encuentra activa."
                )
            },
            status_code=409,
        )

    if not _has_valid_cedula(
        user
    ):
        raise AdminUsuariosServiceError(
            {
                "identificacion": (
                    "La cuenta debe tener una cédula válida "
                    "de exactamente 10 dígitos antes de "
                    "ser activada."
                )
            },
            status_code=400,
        )

    normalized_email = _normalize_email(
        email
    )

    if not normalized_email:
        raise AdminUsuariosServiceError(
            {
                "email": (
                    "El correo electrónico "
                    "es obligatorio."
                )
            }
        )

    try:
        validate_email(
            normalized_email
        )

    except DjangoValidationError as exc:
        raise AdminUsuariosServiceError(
            {
                "email": (
                    "Ingrese un correo electrónico válido."
                )
            }
        ) from exc

    duplicate_email = (
        User.objects
        .filter(
            email__iexact=normalized_email
        )
        .exclude(
            pk=user.pk
        )
        .exists()
    )

    if duplicate_email:
        raise AdminUsuariosServiceError(
            {
                "email": (
                    "Ya existe un usuario registrado "
                    "con este correo electrónico."
                )
            },
            status_code=409,
        )

    normalized_password = str(
        password or ""
    )

    if not normalized_password:
        raise AdminUsuariosServiceError(
            {
                "password": (
                    "La contraseña es obligatoria."
                )
            }
        )

    try:
        validate_password(
            normalized_password,
            user=user,
        )

    except DjangoValidationError as exc:
        raise AdminUsuariosServiceError(
            {
                "password": list(
                    exc.messages
                )
            }
        ) from exc

    update_fields = []

    if user.email != normalized_email:
        user.email = normalized_email
        _append_field(
            update_fields,
            "email",
        )

    user.set_password(
        normalized_password
    )

    _append_field(
        update_fields,
        "password",
    )

    if user.carrera_id is not None:
        user.carrera_id = None

        _append_field(
            update_fields,
            "carrera",
        )

    if user.is_staff:
        user.is_staff = False

        _append_field(
            update_fields,
            "is_staff",
        )

    if not user.is_active:
        user.is_active = True

        _append_field(
            update_fields,
            "is_active",
        )

    profile_complete = _has_valid_cedula(
        user
    )

    if (
        user.perfil_completo
        != profile_complete
    ):
        user.perfil_completo = (
            profile_complete
        )

        _append_field(
            update_fields,
            "perfil_completo",
        )

    return update_fields


# ============================================================
# HABILITAR EDICIÓN DEL PERFIL
# ============================================================

def enable_profile_edit(
    user,
    *,
    hours=PROFILE_EDIT_DEFAULT_HOURS,
    attempts=PROFILE_EDIT_DEFAULT_ATTEMPTS,
):
    """
    Habilita nuevamente la edición del perfil y restablece
    intentos.
    """
    if user is None:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario seleccionado."
                )
            },
            status_code=404,
        )

    try:
        normalized_hours = int(
            hours
        )

        normalized_attempts = int(
            attempts
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "Las horas y los intentos "
                    "deben ser numéricos."
                )
            }
        ) from exc

    if normalized_hours <= 0:
        raise AdminUsuariosServiceError(
            {
                "horas": (
                    "Las horas deben ser "
                    "mayores que cero."
                )
            }
        )

    if normalized_attempts <= 0:
        raise AdminUsuariosServiceError(
            {
                "intentos": (
                    "Los intentos deben ser "
                    "mayores que cero."
                )
            }
        )

    user.profile_edit_until = (
        timezone.now()
        + timedelta(
            hours=normalized_hours
        )
    )

    user.profile_edit_attempts_left = (
        normalized_attempts
    )

    user.profile_edit_locked = False
    user.profile_edit_lock_reason = None

    return [
        "profile_edit_until",
        "profile_edit_attempts_left",
        "profile_edit_locked",
        "profile_edit_lock_reason",
    ]


# ============================================================
# EXTENDER EDICIÓN DEL PERFIL
# ============================================================

def extend_profile_edit(
    user,
    *,
    hours,
):
    """
    Extiende el periodo de edición.

    Si el periodo anterior ya finalizó, la extensión comienza
    desde la fecha actual.
    """
    if user is None:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario seleccionado."
                )
            },
            status_code=404,
        )

    try:
        normalized_hours = int(
            hours
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise AdminUsuariosServiceError(
            {
                "horas": (
                    "El valor de horas "
                    "debe ser numérico."
                )
            }
        ) from exc

    if normalized_hours <= 0:
        raise AdminUsuariosServiceError(
            {
                "horas": (
                    "Las horas deben ser "
                    "mayores que cero."
                )
            }
        )

    current_time = timezone.now()

    current_deadline = getattr(
        user,
        "profile_edit_until",
        None,
    )

    base_time = (
        current_deadline
        if (
            current_deadline is not None
            and current_deadline
            > current_time
        )
        else current_time
    )

    user.profile_edit_until = (
        base_time
        + timedelta(
            hours=normalized_hours
        )
    )

    current_attempts = getattr(
        user,
        "profile_edit_attempts_left",
        0,
    )

    try:
        current_attempts = int(
            current_attempts or 0
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        current_attempts = 0

    user.profile_edit_attempts_left = max(
        current_attempts,
        PROFILE_EDIT_DEFAULT_ATTEMPTS,
    )

    user.profile_edit_locked = False
    user.profile_edit_lock_reason = None

    return [
        "profile_edit_until",
        "profile_edit_attempts_left",
        "profile_edit_locked",
        "profile_edit_lock_reason",
    ]


# ============================================================
# BLOQUEAR EDICIÓN DEL PERFIL
# ============================================================

def block_profile_edit(
    user,
    *,
    reason=None,
):
    """
    Bloquea la edición del perfil y registra el motivo.
    """
    if user is None:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario seleccionado."
                )
            },
            status_code=404,
        )

    normalized_reason = (
        _text(
            reason
        )
        or "Bloqueado por el administrador."
    )

    if len(
        normalized_reason
    ) > 255:
        raise AdminUsuariosServiceError(
            {
                "reason": (
                    "El motivo no puede superar "
                    "los 255 caracteres."
                )
            }
        )

    user.profile_edit_locked = True
    user.profile_edit_lock_reason = (
        normalized_reason
    )

    user.profile_edit_attempts_left = 0
    user.profile_edit_until = None

    return [
        "profile_edit_locked",
        "profile_edit_lock_reason",
        "profile_edit_attempts_left",
        "profile_edit_until",
    ]