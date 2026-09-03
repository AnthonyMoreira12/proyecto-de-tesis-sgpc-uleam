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

Los autores externos no pueden registrar Sede, Facultad ni Carrera. La
identificación es opcional para cuentas externas y, cuando se proporciona,
continúa siendo una cédula ecuatoriana de 10 dígitos.
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

    if hasattr(destination, "_state"):
        if "sede_id" in field_names:
            destination._state.fields_cache.pop("sede", None)

        if "carrera_id" in field_names:
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

def _requested_profile_campaign_fields(requested_fields):
    """Traduce el contrato del serializer a campos lógicos de campaña."""
    mapping = {
        "identificacion": "identificacion",
        "sede_set": "sede",
        "facultad_set": "carrera",
        "carrera_set": "carrera",
        "nombres": "nombres",
        "apellidos": "apellidos",
        "snooze_hours": "snooze_hours",
    }
    return {
        mapping.get(str(field), str(field))
        for field in (requested_fields or [])
    }


def _profile_campaign_override(user, requested_fields=None):
    """Busca una campaña vigente que autorice una edición bloqueada normalmente."""
    # Importación local para mantener el servicio de autenticación desacoplado
    # durante el arranque de Django y evitar ciclos entre módulos.
    from core.actualizaciones.services.actualizaciones_services import (
        campanias_activas_para_usuario,
    )
    from core.models import CampaniaActualizacion

    participants = list(
        campanias_activas_para_usuario(
            user,
            tipo=CampaniaActualizacion.TIPO_PERFIL,
        )
    )
    if not participants:
        return None

    allowed = set()
    participant_ids = []
    campaign_ids = []
    for participant in participants:
        participant_ids.append(participant.pk)
        campaign_ids.append(participant.campania_id)
        allowed.update(participant.campania.campos_habilitados or [])

    requested = _requested_profile_campaign_fields(requested_fields)
    if not requested:
        return None

    # facultad_set es un selector auxiliar de carrera y se traduce a carrera.
    unauthorized = sorted(requested - allowed)
    if unauthorized:
        return {
            "authorized": False,
            "allowed_fields": sorted(allowed),
            "unauthorized_fields": unauthorized,
            "participant_ids": participant_ids,
            "campaign_ids": campaign_ids,
        }

    return {
        "authorized": True,
        "allowed_fields": sorted(allowed),
        "unauthorized_fields": [],
        "participant_ids": participant_ids,
        "campaign_ids": campaign_ids,
    }


def ensure_profile_edit_allowed(user, requested_fields=None):
    """Verifica edición normal y, si está cerrada, una campaña global vigente.

    La campaña es una autorización adicional: nunca reduce permisos que el
    usuario todavía posea por su ventana individual. Cuando se usa la campaña,
    únicamente se permiten los campos declarados por Administración.
    """
    if user is None:
        raise ProfileEditServiceError(
            {"detail": "No fue posible determinar el usuario autenticado."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not bool(getattr(user, "is_active", False)):
        raise ProfileEditServiceError(
            {"detail": "La cuenta del usuario está inactiva."},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    edit_status = get_profile_edit_status(user)

    # Mientras la ventana individual siga disponible, se preserva el
    # comportamiento histórico sin imponer restricciones de campaña.
    if edit_status["available"]:
        return {
            **edit_status,
            "via_campaign": False,
            "campaign_ids": [],
            "campaign_participant_ids": [],
        }

    campaign_override = _profile_campaign_override(
        user,
        requested_fields=requested_fields,
    )
    if campaign_override and campaign_override.get("authorized"):
        return {
            **edit_status,
            "available": True,
            "via_campaign": True,
            "campaign_ids": campaign_override["campaign_ids"],
            "campaign_participant_ids": campaign_override["participant_ids"],
            "campaign_allowed_fields": campaign_override["allowed_fields"],
        }

    if campaign_override and campaign_override.get("unauthorized_fields"):
        raise ProfileEditServiceError(
            {
                "detail": (
                    "La campaña global no habilita uno o más de los campos "
                    "que intenta modificar."
                ),
                "campos_no_habilitados": campaign_override["unauthorized_fields"],
                "campos_habilitados": campaign_override["allowed_fields"],
                "campaign_ids": campaign_override["campaign_ids"],
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if edit_status["profile_edit_locked"]:
        raise ProfileEditServiceError(
            {
                "detail": (
                    "La edición del perfil está bloqueada. Solicite al "
                    "administrador que habilite nuevamente el periodo de edición."
                ),
                "profile_edit_locked": True,
                "profile_edit_lock_reason": edit_status["profile_edit_lock_reason"],
                "attempts_left": edit_status["attempts_left"],
                "profile_edit_until": edit_status["profile_edit_until"],
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if edit_status["attempts_left"] <= 0:
        raise ProfileEditServiceError(
            {
                "detail": "No quedan intentos disponibles para modificar el perfil.",
                "profile_edit_locked": True,
                "profile_edit_lock_reason": PROFILE_EDIT_EXHAUSTED_REASON,
                "attempts_left": 0,
                "profile_edit_until": edit_status["profile_edit_until"],
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if edit_status["expired"]:
        raise ProfileEditServiceError(
            {
                "detail": "El periodo de edición del perfil ha finalizado.",
                "profile_edit_locked": False,
                "attempts_left": edit_status["attempts_left"],
                "profile_edit_until": edit_status["profile_edit_until"],
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return {
        **edit_status,
        "via_campaign": False,
        "campaign_ids": [],
        "campaign_participant_ids": [],
    }


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
    Recalcula la completitud del perfil y normaliza la relación académica.

    Autor externo local:
        La identificación es opcional y nunca puede conservar Sede ni
        Carrera institucional.

    Autor institucional Microsoft:
        Requiere una cédula válida de 10 dígitos, Sede y Carrera. La
        compatibilidad Sede-Carrera queda protegida por Usuario.clean().

    Una combinación de rol y autenticación inconsistente nunca se considera
    completa.
    """
    with transaction.atomic():
        locked_user = _get_locked_user(user)

        is_external = _is_external_user(locked_user)
        is_institutional = _is_institutional_user(locked_user)
        update_fields = []

        # Ninguna cuenta no institucional puede conservar clasificación
        # académica institucional.
        if not is_institutional:
            if getattr(locked_user, "sede_id", None) is not None:
                locked_user.sede_id = None
                update_fields.append("sede")

            if getattr(locked_user, "carrera_id", None) is not None:
                locked_user.carrera_id = None
                update_fields.append("carrera")

        calcular_perfil = getattr(
            locked_user,
            "calcular_perfil_completo",
            None,
        )

        if callable(calcular_perfil):
            profile_complete = bool(calcular_perfil())
        elif is_external:
            profile_complete = True
        elif is_institutional:
            profile_complete = bool(
                _has_valid_cedula(locked_user)
                and getattr(locked_user, "sede_id", None)
                and getattr(locked_user, "carrera_id", None)
            )
        else:
            profile_complete = False

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
            "sede_id",
            "carrera_id",
        ]
        _sync_user_instance(user, locked_user, synchronized_fields)
        return locked_user