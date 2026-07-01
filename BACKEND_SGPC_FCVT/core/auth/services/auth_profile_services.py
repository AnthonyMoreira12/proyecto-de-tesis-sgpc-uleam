"""
Servicios para reglas de edición del perfil del usuario autenticado.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import status


class ProfileEditServiceError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def ensure_profile_edit_allowed(user):
    now = timezone.now()
    profile_edit_until = getattr(user, "profile_edit_until", None)

    if profile_edit_until is not None:
        if profile_edit_until and now > profile_edit_until:
            raise ProfileEditServiceError(
                {
                    "detail": "El periodo de edición de perfil ha finalizado.",
                    "profile_edit_until": profile_edit_until,
                },
                status_code=status.HTTP_403_FORBIDDEN,
            )
    else:
        fecha_registro = getattr(user, "fecha_registro", None)
        if fecha_registro and now - fecha_registro > timedelta(hours=48):
            raise ProfileEditServiceError(
                {"detail": "El periodo de edición de perfil ha finalizado."},
                status_code=status.HTTP_403_FORBIDDEN,
            )

    if getattr(user, "profile_edit_locked", False):
        raise ProfileEditServiceError(
            {
                "detail": (
                    "Edición de perfil bloqueada. "
                    "Solicita al administrador que habilite nuevamente."
                ),
                "profile_edit_locked": True,
                "attempts_left": getattr(user, "profile_edit_attempts_left", 0),
                "profile_edit_until": getattr(user, "profile_edit_until", None),
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )


def register_failed_profile_attempt(user):
    if not hasattr(user, "profile_edit_attempts_left"):
        return

    user.profile_edit_attempts_left = max(
        0,
        int(getattr(user, "profile_edit_attempts_left", 0) or 0) - 1,
    )

    update_fields = ["profile_edit_attempts_left"]

    if user.profile_edit_attempts_left == 0:
        user.profile_edit_locked = True
        user.profile_edit_lock_reason = "Intentos agotados por datos inválidos"
        update_fields.extend(["profile_edit_locked", "profile_edit_lock_reason"])

    user.save(update_fields=update_fields)


def finalize_profile_update(user):
    rol = str(getattr(user, "rol", "")).lower()
    ident_ok = bool(getattr(user, "identificacion", None))

    if rol == "autor_externo":
        user.perfil_completo = ident_ok
    else:
        user.perfil_completo = (
            ident_ok
            and bool(getattr(user, "facultad_id", None))
            and bool(getattr(user, "carrera_id", None))
        )

    update_fields = ["perfil_completo"]

    if hasattr(user, "profile_edit_attempts_left"):
        user.profile_edit_attempts_left = 3
        user.profile_edit_locked = False
        user.profile_edit_lock_reason = None
        update_fields.extend(
            [
                "profile_edit_attempts_left",
                "profile_edit_locked",
                "profile_edit_lock_reason",
            ]
        )

    if hasattr(user, "perfil_banner_snooze_until") and user.perfil_completo:
        user.perfil_banner_snooze_until = None
        update_fields.append("perfil_banner_snooze_until")

    user.save(update_fields=list(dict.fromkeys(update_fields)))