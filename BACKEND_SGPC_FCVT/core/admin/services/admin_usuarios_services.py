"""Servicios administrativos para usuarios."""

from datetime import timedelta

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.utils import timezone


class AdminUsuariosServiceError(Exception):
    def __init__(self, detail, *, status_code=400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def parse_bool(value, *, default=None):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in {"1", "true", "yes", "y", "on", "si", "sí"}:
        return True

    if normalized in {"0", "false", "no", "n", "off"}:
        return False

    raise AdminUsuariosServiceError(
        {"detail": "El valor debe ser verdadero o falso."}
    )


def validate_admin_guard(
    target,
    actor,
    *,
    new_is_active=None,
    new_is_staff=None,
):
    if getattr(target, "is_superuser", False):
        if new_is_active is False or new_is_staff is False:
            raise AdminUsuariosServiceError(
                {
                    "detail": (
                        "No se puede desactivar ni revocar "
                        "a un superusuario."
                    )
                }
            )

    if getattr(target, "pk", None) == getattr(actor, "pk", None):
        if new_is_active is False or new_is_staff is False:
            raise AdminUsuariosServiceError(
                {
                    "detail": (
                        "No puede retirar su propio acceso "
                        "administrativo."
                    )
                }
            )

    removing_admin = (
        (new_is_active is False and target.is_active)
        or (
            new_is_staff is False
            and target.is_staff
            and not target.is_superuser
        )
    )

    if removing_admin:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        remaining = (
            User.objects
            .filter(is_active=True)
            .filter(Q(is_staff=True) | Q(is_superuser=True))
            .exclude(pk=target.pk)
            .exists()
        )

        if not remaining:
            raise AdminUsuariosServiceError(
                {
                    "detail": (
                        "No se puede retirar al último "
                        "administrador activo."
                    )
                }
            )


def activate_external_user(user, *, email=None, password=None):
    if email is not None:
        email = str(email).strip().lower()

        try:
            validate_email(email)
        except DjangoValidationError as exc:
            raise AdminUsuariosServiceError(
                {"email": "Ingrese un correo válido."}
            ) from exc

        user.email = email

    if password is not None:
        password = str(password)

        if not password:
            raise AdminUsuariosServiceError(
                {"password": "La contraseña es obligatoria."}
            )

        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise AdminUsuariosServiceError(
                {"password": list(exc.messages)}
            ) from exc

        user.set_password(password)

    user.is_active = True

    fields = ["is_active"]

    if email is not None:
        fields.append("email")

    if password is not None:
        fields.append("password")

    return fields


def enable_profile_edit(user, *, hours=48, attempts=3):
    try:
        hours = int(hours)
        attempts = int(attempts)
    except (TypeError, ValueError, OverflowError) as exc:
        raise AdminUsuariosServiceError(
            {"detail": "Horas e intentos deben ser numéricos."}
        ) from exc

    if hours <= 0 or attempts <= 0:
        raise AdminUsuariosServiceError(
            {
                "detail": (
                    "Horas e intentos deben ser mayores "
                    "que cero."
                )
            }
        )

    user.profile_edit_until = timezone.now() + timedelta(hours=hours)
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
    except (TypeError, ValueError, OverflowError) as exc:
        raise AdminUsuariosServiceError(
            {"detail": "El valor de horas debe ser numérico."}
        ) from exc

    if hours <= 0:
        raise AdminUsuariosServiceError(
            {"detail": "Las horas deben ser mayores que cero."}
        )

    now = timezone.now()
    base = (
        user.profile_edit_until
        if (
            getattr(user, "profile_edit_until", None)
            and user.profile_edit_until > now
        )
        else now
    )

    user.profile_edit_until = base + timedelta(hours=hours)
    user.profile_edit_attempts_left = max(
        int(getattr(user, "profile_edit_attempts_left", 0) or 0),
        3,
    )
    user.profile_edit_locked = False
    user.profile_edit_lock_reason = None

    return [
        "profile_edit_until",
        "profile_edit_attempts_left",
        "profile_edit_locked",
        "profile_edit_lock_reason",
    ]


def block_profile_edit(user, *, reason=None):
    reason = str(reason or "").strip() or (
        "Bloqueado por el administrador."
    )

    if len(reason) > 255:
        raise AdminUsuariosServiceError(
            {"reason": "El motivo no puede superar 255 caracteres."}
        )

    user.profile_edit_locked = True
    user.profile_edit_lock_reason = reason
    user.profile_edit_attempts_left = 0
    user.profile_edit_until = None

    return [
        "profile_edit_locked",
        "profile_edit_lock_reason",
        "profile_edit_attempts_left",
        "profile_edit_until",
    ]
