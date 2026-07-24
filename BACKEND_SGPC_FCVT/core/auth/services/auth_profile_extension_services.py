"""
Servicio para enviar solicitudes de extensión del periodo de
edición del perfil.

Este servicio:

- Comprueba que el periodo de edición esté vencido o bloqueado.
- Valida nuevamente las horas y el motivo recibido.
- Obtiene destinatarios administrativos desde settings.py.
- Evita solicitudes repetidas mediante un bloqueo atómico en caché.
- Envía correo de texto plano y HTML.
- No modifica automáticamente el plazo del usuario.
- No desbloquea el perfil.
- No concede la extensión solicitada.

La aprobación y ampliación definitiva corresponden al
administrador del sistema.
"""

import hashlib
import logging
from datetime import datetime
from email.utils import formataddr
from smtplib import SMTPException

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.html import escape

from rest_framework import status

from core.auth.services.auth_profile_services import (
    get_profile_edit_status,
)


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURACIÓN
# ============================================================

DEFAULT_EXTENSION_HOURS = 48

ALLOWED_EXTENSION_HOURS = {
    24,
    48,
    72,
}

DEFAULT_COOLDOWN_SECONDS = 600

MIN_COOLDOWN_SECONDS = 60
MAX_COOLDOWN_SECONDS = 86_400

MAX_REASON_LENGTH = 1000
MIN_REASON_LENGTH = 20


# ============================================================
# EXCEPCIÓN DEL SERVICIO
# ============================================================

class ProfileExtensionRequestError(Exception):
    """
    Error controlado producido durante una solicitud de
    extensión del perfil.
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
# NORMALIZACIÓN
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual sin eliminar los saltos de línea
    internos.
    """
    return str(
        value or ""
    ).strip()


def _normalize_single_line(value):
    """
    Normaliza un texto en una sola línea.
    """
    return " ".join(
        str(value or "").split()
    )


def _normalize_email(value):
    """
    Normaliza un correo electrónico.
    """
    normalized = _normalize_single_line(
        value
    ).lower()

    return normalized or None


def _safe_positive_int(
    value,
    *,
    default,
):
    """
    Convierte un valor en entero positivo.
    """
    if isinstance(value, bool):
        return int(default)

    try:
        parsed = int(value)

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return int(default)

    if parsed < 1:
        return int(default)

    return parsed


def _normalize_reason(value):
    """
    Normaliza el motivo conservando párrafos, pero eliminando
    espacios repetidos en cada línea.
    """
    raw_reason = _normalize_text(
        value
    )

    normalized_lines = []

    for line in raw_reason.splitlines():
        normalized_line = " ".join(
            line.split()
        )

        if normalized_line:
            normalized_lines.append(
                normalized_line
            )

    return "\n".join(
        normalized_lines
    )


# ============================================================
# VALIDACIÓN DEL USUARIO Y SOLICITUD
# ============================================================

def _validate_user(user):
    """
    Valida que exista un usuario autenticado y activo.
    """
    if user is None:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "No fue posible determinar "
                    "el usuario autenticado."
                )
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not getattr(
        user,
        "pk",
        None,
    ):
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El usuario todavía no está registrado "
                    "en la base de datos."
                )
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not bool(
        getattr(
            user,
            "is_active",
            False,
        )
    ):
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "La cuenta se encuentra inactiva."
                )
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )


def _validate_reason(reason):
    """
    Valida nuevamente el motivo recibido.

    Aunque el serializer ya realiza esta validación, el servicio
    debe poder utilizarse de forma segura desde otras views,
    comandos o tareas.
    """
    normalized_reason = _normalize_reason(
        reason
    )

    if not normalized_reason:
        raise ProfileExtensionRequestError(
            {
                "motivo": (
                    "Debe indicar el motivo de la solicitud."
                )
            }
        )

    if len(normalized_reason) < MIN_REASON_LENGTH:
        raise ProfileExtensionRequestError(
            {
                "motivo": (
                    "El motivo debe contener al menos "
                    f"{MIN_REASON_LENGTH} caracteres."
                )
            }
        )

    if len(normalized_reason) > MAX_REASON_LENGTH:
        raise ProfileExtensionRequestError(
            {
                "motivo": (
                    "El motivo no puede superar "
                    f"los {MAX_REASON_LENGTH} caracteres."
                )
            }
        )

    return normalized_reason


def _validate_requested_hours(value):
    """
    Valida la cantidad de horas solicitadas.
    """
    requested_hours = _safe_positive_int(
        value,
        default=DEFAULT_EXTENSION_HOURS,
    )

    if requested_hours not in ALLOWED_EXTENSION_HOURS:
        raise ProfileExtensionRequestError(
            {
                "horas_solicitadas": (
                    "Seleccione una extensión de "
                    "24, 48 o 72 horas."
                )
            }
        )

    return requested_hours


def _ensure_extension_is_required(user):
    """
    Verifica que la edición no esté disponible actualmente.

    La solicitud solamente se admite cuando:

    - El plazo expiró.
    - El perfil está bloqueado.
    - No quedan intentos disponibles.
    """
    edit_status = get_profile_edit_status(
        user
    )

    if edit_status.get(
        "available",
        False,
    ):
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El periodo de edición todavía está "
                    "disponible. No es necesario solicitar "
                    "una extensión."
                ),
                "profile_edit_until": (
                    edit_status.get(
                        "profile_edit_until"
                    )
                ),
                "attempts_left": (
                    edit_status.get(
                        "attempts_left",
                        0,
                    )
                ),
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return edit_status


# ============================================================
# DESTINATARIOS
# ============================================================

def _normalize_email_collection(value):
    """
    Convierte una cadena o iterable en una lista de correos
    válidos y sin duplicados.

    Formatos admitidos:

    - "admin@dominio.com"
    - "admin1@dominio.com,admin2@dominio.com"
    - ["admin1@dominio.com", "admin2@dominio.com"]
    - (("Nombre", "correo@dominio.com"), ...)
    """
    if value in (
        None,
        "",
    ):
        return []

    if isinstance(
        value,
        str,
    ):
        candidates = (
            value
            .replace(";", ",")
            .split(",")
        )

    else:
        try:
            candidates = list(
                value
            )

        except TypeError:
            candidates = [
                value,
            ]

    normalized_emails = []

    for candidate in candidates:
        email_candidate = candidate

        # Compatible con settings.ADMINS:
        #
        # ADMINS = [
        #     ("Administrador", "admin@correo.com"),
        # ]
        if isinstance(
            candidate,
            (tuple, list),
        ):
            if len(candidate) >= 2:
                email_candidate = candidate[1]
            elif len(candidate) == 1:
                email_candidate = candidate[0]
            else:
                continue

        normalized_email = _normalize_email(
            email_candidate
        )

        if not normalized_email:
            continue

        try:
            validate_email(
                normalized_email
            )

        except ValidationError:
            logger.warning(
                (
                    "Se ignoró un correo administrativo "
                    "inválido configurado para solicitudes "
                    "de extensión."
                )
            )

            continue

        if normalized_email not in normalized_emails:
            normalized_emails.append(
                normalized_email
            )

    return normalized_emails


def get_profile_extension_admin_emails():
    """
    Obtiene los destinatarios administrativos.

    Orden de prioridad:

    1. PROFILE_EXTENSION_ADMIN_EMAILS
    2. PROFILE_EXTENSION_ADMIN_EMAIL
    3. ADMINS

    DEFAULT_FROM_EMAIL no se utiliza como destinatario porque
    normalmente representa al remitente del sistema.
    """
    recipients = _normalize_email_collection(
        getattr(
            settings,
            "PROFILE_EXTENSION_ADMIN_EMAILS",
            None,
        )
    )

    if not recipients:
        recipients = _normalize_email_collection(
            getattr(
                settings,
                "PROFILE_EXTENSION_ADMIN_EMAIL",
                None,
            )
        )

    if not recipients:
        recipients = _normalize_email_collection(
            getattr(
                settings,
                "ADMINS",
                None,
            )
        )

    if not recipients:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "No existe un correo administrativo "
                    "configurado para recibir solicitudes "
                    "de extensión."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    return recipients


def _get_from_email():
    """
    Obtiene y valida el correo remitente.
    """
    from_email = (
        _normalize_email(
            getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                None,
            )
        )
        or _normalize_email(
            getattr(
                settings,
                "EMAIL_HOST_USER",
                None,
            )
        )
    )

    if not from_email:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El servidor no tiene configurado "
                    "el correo remitente."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    try:
        validate_email(
            from_email
        )

    except ValidationError as exc:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El correo remitente configurado "
                    "en el servidor no es válido."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        ) from exc

    sender_name = _normalize_single_line(
        getattr(
            settings,
            "PROFILE_EXTENSION_FROM_NAME",
            "SGPC ULEAM",
        )
    )

    return formataddr(
        (
            sender_name or "SGPC ULEAM",
            from_email,
        )
    )


# ============================================================
# DATOS DEL USUARIO
# ============================================================

def _get_user_display_name(user):
    """
    Obtiene el nombre visible del usuario.
    """
    microsoft_name = _normalize_single_line(
        getattr(
            user,
            "ms_display_name",
            None,
        )
    )

    if microsoft_name:
        return microsoft_name

    get_full_name = getattr(
        user,
        "get_full_name",
        None,
    )

    if callable(get_full_name):
        full_name = _normalize_single_line(
            get_full_name()
        )

        if full_name:
            return full_name

    names = _normalize_single_line(
        getattr(
            user,
            "nombres",
            None,
        )
    )

    surnames = _normalize_single_line(
        getattr(
            user,
            "apellidos",
            None,
        )
    )

    combined_name = " ".join(
        part
        for part in [
            names,
            surnames,
        ]
        if part
    )

    return (
        combined_name
        or _normalize_email(
            getattr(
                user,
                "email",
                None,
            )
        )
        or f"Usuario #{user.pk}"
    )


def _get_career(user):
    """
    Obtiene la carrera institucional del usuario.
    """
    if not getattr(
        user,
        "carrera_id",
        None,
    ):
        return None

    return getattr(
        user,
        "carrera",
        None,
    )


def _get_faculty(user):
    """
    Obtiene la facultad derivada desde carrera.facultad.
    """
    career = _get_career(
        user
    )

    if career is None:
        return None

    return getattr(
        career,
        "facultad",
        None,
    )


def _get_faculty_label(user):
    faculty = _get_faculty(
        user
    )

    if faculty is None:
        return "No registrada"

    return (
        _normalize_single_line(
            getattr(
                faculty,
                "nombre",
                None,
            )
        )
        or "No registrada"
    )


def _get_career_label(user):
    career = _get_career(
        user
    )

    if career is None:
        return "No registrada"

    return (
        _normalize_single_line(
            getattr(
                career,
                "nombre",
                None,
            )
        )
        or "No registrada"
    )


def _get_identification_label(user):
    return (
        _normalize_single_line(
            getattr(
                user,
                "identificacion",
                None,
            )
        )
        or "No registrada"
    )


def _get_role_label(user):
    get_role_display = getattr(
        user,
        "get_rol_display",
        None,
    )

    if callable(get_role_display):
        role_label = _normalize_single_line(
            get_role_display()
        )

        if role_label:
            return role_label

    return (
        _normalize_single_line(
            getattr(
                user,
                "rol",
                None,
            )
        )
        or "No disponible"
    )


def _get_auth_source_label(user):
    get_source_display = getattr(
        user,
        "get_auth_source_display",
        None,
    )

    if callable(get_source_display):
        source_label = _normalize_single_line(
            get_source_display()
        )

        if source_label:
            return source_label

    return (
        _normalize_single_line(
            getattr(
                user,
                "auth_source",
                None,
            )
        )
        or "No disponible"
    )


# ============================================================
# FECHAS
# ============================================================

def _format_datetime(value):
    """
    Convierte una fecha en texto usando la zona horaria activa.
    """
    if not value:
        return "No disponible"

    if not isinstance(
        value,
        datetime,
    ):
        return _normalize_single_line(
            value
        ) or "No disponible"

    local_value = value

    if timezone.is_aware(value):
        try:
            local_value = timezone.localtime(
                value
            )

        except (
            ValueError,
            OverflowError,
        ):
            local_value = value

    return local_value.strftime(
        "%d/%m/%Y %H:%M"
    )


# ============================================================
# DIRECCIÓN IP
# ============================================================

def _get_client_ip(request):
    """
    Obtiene la dirección IP del cliente.

    X-Forwarded-For solamente se utiliza cuando el proyecto
    habilita expresamente TRUST_X_FORWARDED_FOR.
    """
    if request is None:
        return "No disponible"

    trust_forwarded = bool(
        getattr(
            settings,
            "TRUST_X_FORWARDED_FOR",
            False,
        )
    )

    if trust_forwarded:
        forwarded_for = _normalize_single_line(
            request.META.get(
                "HTTP_X_FORWARDED_FOR",
                "",
            )
        )

        if forwarded_for:
            return (
                forwarded_for
                .split(",")[0]
                .strip()
                or "No disponible"
            )

    return (
        _normalize_single_line(
            request.META.get(
                "REMOTE_ADDR",
                "",
            )
        )
        or "No disponible"
    )


# ============================================================
# CONTROL DE REPETICIÓN
# ============================================================

def _get_cooldown_seconds():
    """
    Obtiene el tiempo mínimo entre solicitudes.
    """
    configured = getattr(
        settings,
        "PROFILE_EXTENSION_REQUEST_COOLDOWN_SECONDS",
        DEFAULT_COOLDOWN_SECONDS,
    )

    cooldown = _safe_positive_int(
        configured,
        default=DEFAULT_COOLDOWN_SECONDS,
    )

    return max(
        MIN_COOLDOWN_SECONDS,
        min(
            cooldown,
            MAX_COOLDOWN_SECONDS,
        ),
    )


def _build_cooldown_key(user):
    """
    Construye una clave de caché sin exponer directamente el ID
    del usuario.
    """
    raw_identifier = (
        f"profile-extension:{user.pk}"
    )

    digest = hashlib.sha256(
        raw_identifier.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        "auth:profile-extension:"
        f"{digest}"
    )


def _acquire_cooldown(user):
    """
    Reserva atómicamente el derecho de enviar una solicitud.

    Retorna:
        tuple:
            cache_key
            cooldown_seconds
    """
    cooldown_seconds = (
        _get_cooldown_seconds()
    )

    cache_key = _build_cooldown_key(
        user
    )

    acquired = cache.add(
        cache_key,
        timezone.now().isoformat(),
        timeout=cooldown_seconds,
    )

    if not acquired:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "Ya se envió una solicitud recientemente. "
                    "Espere unos minutos antes de intentarlo "
                    "nuevamente."
                ),
                "retry_after_seconds": (
                    cooldown_seconds
                ),
            },
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
        )

    return (
        cache_key,
        cooldown_seconds,
    )


# ============================================================
# CONTENIDO DEL CORREO
# ============================================================

def _build_email_context(
    *,
    user,
    reason,
    requested_hours,
    edit_status,
    request,
):
    """
    Construye los datos utilizados en el correo.
    """
    current_time = timezone.now()

    user_email = (
        _normalize_email(
            getattr(
                user,
                "email",
                None,
            )
        )
        or "No disponible"
    )

    lock_reason = (
        _normalize_single_line(
            edit_status.get(
                "profile_edit_lock_reason"
            )
        )
        or (
            "El periodo habilitado finalizó "
            "o no quedan intentos disponibles."
        )
    )

    return {
        "user_id": user.pk,
        "display_name": (
            _get_user_display_name(
                user
            )
        ),
        "email": user_email,
        "identification": (
            _get_identification_label(
                user
            )
        ),
        "role": _get_role_label(
            user
        ),
        "auth_source": (
            _get_auth_source_label(
                user
            )
        ),
        "faculty": (
            _get_faculty_label(
                user
            )
        ),
        "career": (
            _get_career_label(
                user
            )
        ),
        "registration_date": (
            _format_datetime(
                getattr(
                    user,
                    "fecha_registro",
                    None,
                )
            )
        ),
        "previous_deadline": (
            _format_datetime(
                edit_status.get(
                    "profile_edit_until"
                )
            )
        ),
        "locked": bool(
            edit_status.get(
                "profile_edit_locked",
                False,
            )
        ),
        "expired": bool(
            edit_status.get(
                "expired",
                False,
            )
        ),
        "attempts_left": int(
            edit_status.get(
                "attempts_left",
                0,
            )
            or 0
        ),
        "lock_reason": lock_reason,
        "requested_hours": (
            requested_hours
        ),
        "reason": reason,
        "requested_at": (
            _format_datetime(
                current_time
            )
        ),
        "ip_address": (
            _get_client_ip(
                request
            )
        ),
    }


def _build_subject(context):
    """
    Construye el asunto del correo.
    """
    return (
        "[SGPC ULEAM] Solicitud de extensión "
        f"de perfil — {context['display_name']}"
    )


def _build_text_body(context):
    """
    Construye la versión de texto plano.
    """
    locked_label = (
        "Sí"
        if context["locked"]
        else "No"
    )

    expired_label = (
        "Sí"
        if context["expired"]
        else "No"
    )

    return f"""Se ha recibido una solicitud de extensión del periodo de edición del perfil.

DATOS DEL USUARIO

Nombre: {context["display_name"]}
Correo: {context["email"]}
Identificación: {context["identification"]}
Tipo de usuario: {context["role"]}
Origen de autenticación: {context["auth_source"]}
Facultad: {context["faculty"]}
Carrera: {context["career"]}
Fecha de registro: {context["registration_date"]}

ESTADO ACTUAL DE EDICIÓN

Fecha límite anterior: {context["previous_deadline"]}
Periodo expirado: {expired_label}
Perfil bloqueado: {locked_label}
Intentos disponibles: {context["attempts_left"]}
Motivo del bloqueo o vencimiento: {context["lock_reason"]}

SOLICITUD

Horas solicitadas: {context["requested_hours"]}

Motivo indicado por el usuario:

{context["reason"]}

DATOS DE CONTROL

ID del usuario: {context["user_id"]}
Fecha de solicitud: {context["requested_at"]}
Dirección IP: {context["ip_address"]}

Esta notificación fue generada automáticamente por SGPC ULEAM.
La extensión no se concede automáticamente. Debe ser revisada
y aprobada por un administrador.
"""


def _html_multiline(value):
    """
    Escapa un texto y conserva sus saltos de línea en HTML.
    """
    return escape(
        str(value or "")
    ).replace(
        "\n",
        "<br>",
    )


def _build_html_body(context):
    """
    Construye la versión HTML del correo.
    """
    locked_label = (
        "Sí"
        if context["locked"]
        else "No"
    )

    expired_label = (
        "Sí"
        if context["expired"]
        else "No"
    )

    return f"""
    <div
      style="
        max-width:720px;
        margin:0 auto;
        font-family:Arial,Helvetica,sans-serif;
        color:#172033;
        line-height:1.55;
      "
    >
      <div
        style="
          padding:22px 24px;
          background:#0f2f57;
          color:#ffffff;
          border-radius:12px 12px 0 0;
        "
      >
        <div
          style="
            font-size:12px;
            font-weight:700;
            letter-spacing:.08em;
            text-transform:uppercase;
            opacity:.82;
          "
        >
          SGPC ULEAM
        </div>

        <h2
          style="
            margin:6px 0 0;
            font-size:22px;
          "
        >
          Solicitud de extensión del perfil
        </h2>
      </div>

      <div
        style="
          padding:24px;
          border:1px solid #d9e1ee;
          border-top:0;
          border-radius:0 0 12px 12px;
          background:#ffffff;
        "
      >
        <p style="margin-top:0">
          Un usuario solicita ampliar el periodo habilitado
          para modificar su perfil.
        </p>

        <h3
          style="
            margin:24px 0 10px;
            font-size:16px;
          "
        >
          Datos del usuario
        </h3>

        <table
          style="
            width:100%;
            border-collapse:collapse;
          "
        >
          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Nombre</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["display_name"])}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Correo</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["email"])}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Identificación</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["identification"])}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Tipo de usuario</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["role"])}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Facultad</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["faculty"])}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Carrera</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["career"])}
            </td>
          </tr>
        </table>

        <h3
          style="
            margin:24px 0 10px;
            font-size:16px;
          "
        >
          Estado actual
        </h3>

        <table
          style="
            width:100%;
            border-collapse:collapse;
          "
        >
          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Límite anterior</strong>
            </td>
            <td style="padding:7px 0">
              {escape(context["previous_deadline"])}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Periodo expirado</strong>
            </td>
            <td style="padding:7px 0">
              {expired_label}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Perfil bloqueado</strong>
            </td>
            <td style="padding:7px 0">
              {locked_label}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Intentos disponibles</strong>
            </td>
            <td style="padding:7px 0">
              {context["attempts_left"]}
            </td>
          </tr>

          <tr>
            <td style="padding:7px 8px 7px 0">
              <strong>Extensión solicitada</strong>
            </td>
            <td style="padding:7px 0">
              {context["requested_hours"]} horas
            </td>
          </tr>
        </table>

        <h3
          style="
            margin:24px 0 10px;
            font-size:16px;
          "
        >
          Motivo
        </h3>

        <div
          style="
            padding:14px;
            border:1px solid #d9e1ee;
            border-radius:10px;
            background:#f7f9fc;
          "
        >
          {_html_multiline(context["reason"])}
        </div>

        <p
          style="
            margin:22px 0 0;
            color:#667085;
            font-size:13px;
          "
        >
          ID de usuario:
          {context["user_id"]}
          · Solicitud:
          {escape(context["requested_at"])}
          · IP:
          {escape(context["ip_address"])}
        </p>

        <p
          style="
            margin:10px 0 0;
            color:#667085;
            font-size:13px;
          "
        >
          La extensión no fue concedida automáticamente.
          Debe ser revisada por un administrador.
        </p>
      </div>
    </div>
    """


# ============================================================
# ENVÍO
# ============================================================

def _send_extension_email(
    *,
    context,
    recipients,
):
    """
    Construye y envía el correo.

    Retorna la cantidad confirmada por el backend de correo.
    """
    user_email = context["email"]

    reply_to = []

    if user_email != "No disponible":
        try:
            validate_email(
                user_email
            )

            reply_to = [
                user_email,
            ]

        except ValidationError:
            reply_to = []

    email = EmailMultiAlternatives(
        subject=_build_subject(
            context
        ),
        body=_build_text_body(
            context
        ),
        from_email=_get_from_email(),
        to=recipients,
        reply_to=reply_to,
    )

    email.attach_alternative(
        _build_html_body(
            context
        ),
        "text/html",
    )

    return email.send(
        fail_silently=False
    )


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

def send_profile_edit_extension_request(
    *,
    user,
    motivo,
    horas_solicitadas=DEFAULT_EXTENSION_HOURS,
    request=None,
):
    """
    Envía una solicitud de extensión al administrador.

    La función no modifica ningún campo del usuario.

    Retorna:

    {
        "sent_count": 1,
        "recipient_count": 2,
        "requested_hours": 48
    }
    """
    _validate_user(
        user
    )

    normalized_reason = _validate_reason(
        motivo
    )

    requested_hours = (
        _validate_requested_hours(
            horas_solicitadas
        )
    )

    edit_status = _ensure_extension_is_required(
        user
    )

    recipients = (
        get_profile_extension_admin_emails()
    )

    cooldown_key, cooldown_seconds = (
        _acquire_cooldown(
            user
        )
    )

    context = _build_email_context(
        user=user,
        reason=normalized_reason,
        requested_hours=requested_hours,
        edit_status=edit_status,
        request=request,
    )

    try:
        sent_count = _send_extension_email(
            context=context,
            recipients=recipients,
        )

    except (
        SMTPException,
        OSError,
        ConnectionError,
        TimeoutError,
    ) as exc:
        # Se libera el bloqueo porque el correo no fue enviado.
        cache.delete(
            cooldown_key
        )

        logger.exception(
            (
                "No se pudo enviar la solicitud de extensión "
                "del Usuario %s."
            ),
            user.pk,
        )

        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El servidor no pudo enviar el correo. "
                    "Revise la configuración SMTP e inténtelo "
                    "nuevamente."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        ) from exc

    except Exception as exc:
        # Algunos backends personalizados de Django pueden
        # utilizar excepciones propias. Este límite externo
        # evita exponer errores internos al cliente.
        cache.delete(
            cooldown_key
        )

        logger.exception(
            (
                "El backend de correo produjo un error "
                "inesperado al procesar la solicitud del "
                "Usuario %s."
            ),
            user.pk,
        )

        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "No fue posible procesar la solicitud "
                    "de extensión en este momento."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        ) from exc

    if int(sent_count or 0) < 1:
        cache.delete(
            cooldown_key
        )

        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El servidor de correo no confirmó "
                    "el envío de la solicitud."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    logger.info(
        (
            "Solicitud de extensión enviada. "
            "Usuario=%s Horas=%s Destinatarios=%s"
        ),
        user.pk,
        requested_hours,
        len(recipients),
    )

    return {
        "sent_count": int(
            sent_count
        ),
        "recipient_count": len(
            recipients
        ),
        "requested_hours": (
            requested_hours
        ),
        "cooldown_seconds": (
            cooldown_seconds
        ),
    }