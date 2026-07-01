"""
Servicios administrativos para gestión de usuarios.
Contiene lógica de negocio reutilizable y separada del ViewSet.
Complementa el módulo administrativo al validar cambios de acceso,
activar usuarios externos, habilitar o extender edición de perfil y bloquear
la edición cuando sea necesario.
"""

from datetime import timedelta

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import status

from core.admin.selectors.admin_usuarios_selectors import active_admins_qs


class AdminUsuariosServiceError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def parse_bool(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if value in (0, 1):
            return bool(value)
        return None

    s = str(value).strip().lower()

    if s in ("1", "true", "yes", "y", "on"):
        return True

    if s in ("0", "false", "no", "n", "off"):
        return False

    return None


def validate_admin_guard(usuario, actor, *, new_is_active=None, new_is_staff=None):
    final_is_active = usuario.is_active if new_is_active is None else bool(new_is_active)
    final_is_staff = usuario.is_staff if new_is_staff is None else bool(new_is_staff)

    current_is_admin = bool(usuario.is_superuser or usuario.is_staff)
    final_is_admin = bool(usuario.is_superuser or final_is_staff)

    current_is_active_admin = current_is_admin and bool(usuario.is_active)
    final_is_active_admin = final_is_admin and final_is_active

    changing_access = (
        (new_is_active is not None and final_is_active != usuario.is_active)
        or (new_is_staff is not None and final_is_staff != usuario.is_staff)
    )

    if changing_access and usuario.pk == getattr(actor, "pk", None):
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "No puedes modificar tu propio acceso administrativo "
                    "o estado activo desde este endpoint."
                )
            }
        )

    if current_is_active_admin and not final_is_active_admin:
        if not active_admins_qs().exclude(pk=usuario.pk).exists():
            raise AdminUsuariosServiceError(
                {"detail": "No se puede dejar el sistema sin administradores activos."}
            )

    return True


def _ensure_external_local_user(user):
    if (
        str(getattr(user, "rol", "")).lower() != "autor_externo"
        or str(getattr(user, "auth_source", "")).lower() != "local"
    ):
        raise AdminUsuariosServiceError(
            {"detail": "Solo se pueden activar usuarios externos (local)."}
        )


def activate_external_user(user, *, email=None, password=""):
    _ensure_external_local_user(user)

    if email is not None:
        email = str(email).strip().lower()

        if not email:
            raise AdminUsuariosServiceError(
                {"email": "Ingrese un correo válido."}
            )

        try:
            validate_email(email)
        except DjangoValidationError:
            raise AdminUsuariosServiceError(
                {"email": "Ingrese un correo válido."}
            )

    password = str(password).strip() if password is not None else ""
    if not password:
        raise AdminUsuariosServiceError(
            {"password": "La contraseña es obligatoria."}
        )

    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise AdminUsuariosServiceError(
            {"password": list(exc.messages)}
        )

    update_fields = []

    if email is not None:
        user.email = email
        update_fields.append("email")

    user.set_password(password)
    user.is_active = True
    update_fields.extend(["password", "is_active"])

    return update_fields


def enable_profile_edit(user, *, hours=48, attempts=3):
    now = timezone.now()

    user.profile_edit_until = now + timedelta(hours=hours)
    user.profile_edit_attempts_left = attempts
    user.profile_edit_locked = False
    user.profile_edit_lock_reason = None

    return [
        "profile_edit_until",
        "profile_edit_attempts_left",
        "profile_edit_locked",
        "profile_edit_lock_reason",
    ]


def extend_profile_edit(user, *, hours):
    try:
        hours = int(hours)
    except Exception:
        raise AdminUsuariosServiceError(
            {"detail": "El valor de 'horas' debe ser numérico."}
        )

    if hours <= 0:
        raise AdminUsuariosServiceError(
            {"detail": "Las horas deben ser mayores a 0."}
        )

    now = timezone.now()
    base = now

    if getattr(user, "profile_edit_until", None) and user.profile_edit_until > now:
        base = user.profile_edit_until

    user.profile_edit_until = base + timedelta(hours=hours)
    user.profile_edit_attempts_left = 3
    user.profile_edit_locked = False
    user.profile_edit_lock_reason = None

    return [
        "profile_edit_until",
        "profile_edit_attempts_left",
        "profile_edit_locked",
        "profile_edit_lock_reason",
    ]


def block_profile_edit(user, *, reason=None):
    if reason is not None:
        reason = str(reason).strip()
        if reason == "":
            reason = None

    if reason and len(reason) > 255:
        raise AdminUsuariosServiceError(
            {"reason": "El motivo no puede exceder 255 caracteres."}
        )

    user.profile_edit_locked = True
    user.profile_edit_lock_reason = reason or "Bloqueado por el administrador."
    user.profile_edit_attempts_left = 0
    user.profile_edit_until = None

    return [
        "profile_edit_locked",
        "profile_edit_lock_reason",
        "profile_edit_attempts_left",
        "profile_edit_until",
    ]