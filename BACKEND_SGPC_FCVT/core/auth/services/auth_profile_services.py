"""
Servicios para controlar la edición del perfil del usuario.

Este módulo centraliza:

- Cálculo del plazo disponible.
- Validación del permiso de edición.
- Descuento seguro de intentos.
- Bloqueo por intentos agotados.
- Finalización del perfil.
- Restablecimiento de intentos después de una edición válida.

La facultad no se almacena directamente en Usuario. Se deriva
exclusivamente mediante usuario.carrera.facultad.

Los autores externos no pueden registrar Facultad ni Carrera y el
campo identificacion contiene únicamente una cédula de 10 dígitos.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROFILE_EDIT_DEFAULT_HOURS = 48
PROFILE_EDIT_DEFAULT_ATTEMPTS = 3

PROFILE_EDIT_EXHAUSTED_REASON = (
    "Intentos agotados por datos inválidos."
)


# ============================================================
# EXCEPCIÓN DEL SERVICIO
# ============================================================

class ProfileEditServiceError(Exception):
    """
    Error controlado producido por las reglas de edición del
    perfil.
    """

    def __init__(
        self,
        detail,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        self.detail = detail
        self.status_code = status_code

        super().__init__(
            str(detail)
        )


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un texto opcional.
    """
    return str(
        value or ""
    ).strip()


def _safe_non_negative_int(
    value,
    *,
    default=0,
):
    """
    Convierte un valor en entero no negativo.
    """
    if isinstance(value, bool):
        return int(
            default
        )

    try:
        parsed = int(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return int(
            default
        )

    return max(
        0,
        parsed,
    )



def _normalized_role(user):
    return _normalize_text(getattr(user, "rol", "")).lower()


def _normalized_auth_source(user):
    return _normalize_text(getattr(user, "auth_source", "")).lower()


def _is_external_user(user):
    if user is None:
        return False
    return bool(
        _normalized_role(user) == "autor_externo"
        and _normalized_auth_source(user) == "local"
    )


def _is_institutional_user(user):
    if user is None:
        return False
    return bool(
        _normalized_role(user) == "autor"
        and _normalized_auth_source(user) == "microsoft"
    )


def _has_valid_cedula(user):
    cedula = _normalize_text(getattr(user, "identificacion", None))
    return bool(len(cedula) == 10 and cedula.isdigit())

def _sync_user_instance(
    destination,
    source,
    field_names,
):
    """
    Sincroniza en la instancia original los valores modificados
    sobre la fila bloqueada de la base de datos.

    Esto permite que las views actuales continúen utilizando la
    misma instancia sin necesitar otra consulta inmediata.
    """
    if destination is None:
        return

    for field_name in field_names:
        setattr(
            destination,
            field_name,
            getattr(
                source,
                field_name,
                None,
            ),
        )

    if "carrera_id" in field_names and hasattr(destination, "_state"):
        destination._state.fields_cache.pop("carrera", None)


def _get_locked_user(user):
    """
    Obtiene y bloquea la fila del usuario.

    Debe utilizarse dentro de transaction.atomic().
    """
    if user is None:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario del perfil."
                )
            },
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    user_id = getattr(
        user,
        "pk",
        None,
    )

    if not user_id:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "El usuario todavía no está "
                    "registrado en la base de datos."
                )
            },
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    user_model = type(
        user
    )

    try:
        return (
            user_model.objects
            .select_for_update()
            .get(
                pk=user_id
            )
        )

    except user_model.DoesNotExist as exc:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "El usuario ya no existe."
                )
            },
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
        ) from exc


# ============================================================
# PLAZO DE EDICIÓN
# ============================================================

def get_profile_edit_deadline(user):
    """
    Obtiene la fecha límite vigente para editar el perfil.

    Prioridad:

    1. profile_edit_until definido explícitamente.
    2. fecha_registro + 48 horas.
    3. None cuando no existe ninguna fecha de referencia.
    """
    if user is None:
        return None

    explicit_deadline = getattr(
        user,
        "profile_edit_until",
        None,
    )

    if explicit_deadline is not None:
        return explicit_deadline

    registration_date = getattr(
        user,
        "fecha_registro",
        None,
    )

    if registration_date is None:
        return None

    return (
        registration_date
        + timedelta(
            hours=PROFILE_EDIT_DEFAULT_HOURS
        )
    )


def get_profile_edit_status(user):
    """
    Construye el estado actual de edición del perfil.
    """
    current_time = timezone.now()

    deadline = get_profile_edit_deadline(
        user
    )

    attempts_left = (
        _safe_non_negative_int(
            getattr(
                user,
                "profile_edit_attempts_left",
                PROFILE_EDIT_DEFAULT_ATTEMPTS,
            ),
            default=(
                PROFILE_EDIT_DEFAULT_ATTEMPTS
            ),
        )
    )

    locked = bool(
        getattr(
            user,
            "profile_edit_locked",
            False,
        )
    )

    lock_reason = (
        _normalize_text(
            getattr(
                user,
                "profile_edit_lock_reason",
                None,
            )
        )
        or None
    )

    expired = bool(
        deadline is not None
        and current_time > deadline
    )

    return {
        "profile_edit_until": deadline,
        "profile_edit_locked": locked,
        "profile_edit_lock_reason": (
            lock_reason
        ),
        "attempts_left": attempts_left,
        "expired": expired,
        "available": bool(
            not locked
            and attempts_left > 0
            and not expired
        ),
    }


# ============================================================
# VALIDACIÓN DEL PERMISO
# ============================================================

def ensure_profile_edit_allowed(user):
    """
    Verifica que el usuario pueda modificar su perfil.

    Retorna el estado cuando la edición está disponible.
    Lanza ProfileEditServiceError cuando está bloqueada,
    vencida o sin intentos.
    """
    if user is None:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario autenticado."
                )
            },
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
        )

    if not bool(
        getattr(
            user,
            "is_active",
            False,
        )
    ):
        raise ProfileEditServiceError(
            {
                "detail": (
                    "La cuenta del usuario está inactiva."
                )
            },
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
        )

    edit_status = get_profile_edit_status(
        user
    )

    if edit_status[
        "profile_edit_locked"
    ]:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "La edición del perfil está bloqueada. "
                    "Solicite al administrador que habilite "
                    "nuevamente el periodo de edición."
                ),
                "profile_edit_locked": True,
                "profile_edit_lock_reason": (
                    edit_status[
                        "profile_edit_lock_reason"
                    ]
                ),
                "attempts_left": (
                    edit_status[
                        "attempts_left"
                    ]
                ),
                "profile_edit_until": (
                    edit_status[
                        "profile_edit_until"
                    ]
                ),
            },
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
        )

    if edit_status[
        "attempts_left"
    ] <= 0:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "No quedan intentos disponibles "
                    "para modificar el perfil."
                ),
                "profile_edit_locked": True,
                "profile_edit_lock_reason": (
                    PROFILE_EDIT_EXHAUSTED_REASON
                ),
                "attempts_left": 0,
                "profile_edit_until": (
                    edit_status[
                        "profile_edit_until"
                    ]
                ),
            },
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
        )

    if edit_status["expired"]:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "El periodo de edición del perfil "
                    "ha finalizado."
                ),
                "profile_edit_locked": False,
                "attempts_left": (
                    edit_status[
                        "attempts_left"
                    ]
                ),
                "profile_edit_until": (
                    edit_status[
                        "profile_edit_until"
                    ]
                ),
            },
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
        )

    return edit_status


# ============================================================
# INTENTOS FALLIDOS
# ============================================================

def register_failed_profile_attempt(user):
    """
    Descuenta un intento de edición de forma transaccional.

    Cuando el contador llega a cero:

    - Se bloquea la edición.
    - Se registra el motivo.
    - Se conserva el plazo existente.

    Retorna el estado actualizado.
    """
    with transaction.atomic():
        locked_user = _get_locked_user(
            user
        )

        current_attempts = (
            _safe_non_negative_int(
                getattr(
                    locked_user,
                    "profile_edit_attempts_left",
                    PROFILE_EDIT_DEFAULT_ATTEMPTS,
                ),
                default=(
                    PROFILE_EDIT_DEFAULT_ATTEMPTS
                ),
            )
        )

        new_attempts = max(
            0,
            current_attempts - 1,
        )

        update_fields = []

        if (
            locked_user.profile_edit_attempts_left
            != new_attempts
        ):
            locked_user.profile_edit_attempts_left = (
                new_attempts
            )

            update_fields.append(
                "profile_edit_attempts_left"
            )

        if new_attempts == 0:
            if not locked_user.profile_edit_locked:
                locked_user.profile_edit_locked = (
                    True
                )

                update_fields.append(
                    "profile_edit_locked"
                )

            if (
                locked_user.profile_edit_lock_reason
                != PROFILE_EDIT_EXHAUSTED_REASON
            ):
                locked_user.profile_edit_lock_reason = (
                    PROFILE_EDIT_EXHAUSTED_REASON
                )

                update_fields.append(
                    "profile_edit_lock_reason"
                )

        if update_fields:
            locked_user.save(
                update_fields=list(
                    dict.fromkeys(
                        update_fields
                    )
                )
            )

        synchronized_fields = [
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",
            "profile_edit_until",
        ]

        _sync_user_instance(
            user,
            locked_user,
            synchronized_fields,
        )

        return get_profile_edit_status(
            locked_user
        )


# ============================================================
# FINALIZACIÓN DEL PERFIL
# ============================================================

def finalize_profile_update(user):
    """
    Recalcula la completitud del perfil.

    Autor externo local:
        Requiere una cédula válida de 10 dígitos y no puede tener carrera.

    Autor institucional Microsoft:
        Requiere una cédula válida de 10 dígitos y carrera.

    Una combinación de rol y autenticación inconsistente nunca se
    considera completa.
    """
    with transaction.atomic():
        locked_user = _get_locked_user(user)

        cedula_complete = _has_valid_cedula(locked_user)
        career_complete = bool(getattr(locked_user, "carrera_id", None))
        is_external = _is_external_user(locked_user)
        is_institutional = _is_institutional_user(locked_user)

        if is_external:
            profile_complete = cedula_complete
        elif is_institutional:
            profile_complete = bool(cedula_complete and career_complete)
        else:
            profile_complete = False

        update_fields = []

        # Ninguna cuenta no institucional puede conservar una carrera.
        if not is_institutional and locked_user.carrera_id is not None:
            locked_user.carrera_id = None
            update_fields.append("carrera")

        if locked_user.perfil_completo != profile_complete:
            locked_user.perfil_completo = profile_complete
            update_fields.append("perfil_completo")

        if (
            locked_user.profile_edit_attempts_left
            != PROFILE_EDIT_DEFAULT_ATTEMPTS
        ):
            locked_user.profile_edit_attempts_left = (
                PROFILE_EDIT_DEFAULT_ATTEMPTS
            )
            update_fields.append("profile_edit_attempts_left")

        if locked_user.profile_edit_locked:
            locked_user.profile_edit_locked = False
            update_fields.append("profile_edit_locked")

        if locked_user.profile_edit_lock_reason is not None:
            locked_user.profile_edit_lock_reason = None
            update_fields.append("profile_edit_lock_reason")

        if (
            profile_complete
            and getattr(locked_user, "perfil_banner_snooze_until", None)
            is not None
        ):
            locked_user.perfil_banner_snooze_until = None
            update_fields.append("perfil_banner_snooze_until")

        if update_fields:
            locked_user.save(
                update_fields=list(dict.fromkeys(update_fields))
            )

        synchronized_fields = [
            "perfil_completo",
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",
            "profile_edit_until",
            "perfil_banner_snooze_until",
            "carrera_id",
        ]
        _sync_user_instance(user, locked_user, synchronized_fields)
        return locked_user
