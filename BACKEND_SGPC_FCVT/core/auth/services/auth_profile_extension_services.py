"""
Servicio de correo para solicitudes de extensión del plazo de edición.

Este servicio es independiente de ProfileView.patch, por lo que puede
utilizarse aunque el periodo de edición haya finalizado o el perfil esté
bloqueado.
"""

import logging
from datetime import timedelta
from email.utils import formataddr

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.html import escape
from rest_framework import status

logger = logging.getLogger(__name__)


class ProfileExtensionRequestError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def _normalizar_lista_correos(value):
    if not value:
        return []

    if isinstance(value, str):
        candidates = value.replace(";", ",").split(",")
    else:
        candidates = list(value)

    emails = []

    for candidate in candidates:
        email = str(candidate or "").strip()

        if not email:
            continue

        try:
            validate_email(email)
        except ValidationError:
            logger.warning(
                "Se ignoró un correo de administrador no válido: %s",
                email,
            )
            continue

        if email not in emails:
            emails.append(email)

    return emails


def get_profile_extension_admin_emails():
    configured = getattr(
        settings,
        "PROFILE_EXTENSION_ADMIN_EMAILS",
        None,
    )

    emails = _normalizar_lista_correos(configured)

    if not emails:
        emails = _normalizar_lista_correos(
            getattr(settings, "PROFILE_EXTENSION_ADMIN_EMAIL", None)
        )

    if not emails:
        emails = _normalizar_lista_correos(
            getattr(settings, "DEFAULT_FROM_EMAIL", None)
        )

    if not emails:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "No existe un correo administrativo configurado para "
                    "recibir solicitudes de extensión."
                )
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return emails


def _get_user_display_name(user):
    microsoft_name = str(
        getattr(user, "ms_display_name", "") or ""
    ).strip()

    if microsoft_name:
        return microsoft_name

    full_name = str(user.get_full_name() or "").strip()

    if full_name:
        return full_name

    nombres = str(getattr(user, "nombres", "") or "").strip()
    apellidos = str(getattr(user, "apellidos", "") or "").strip()
    combined = f"{nombres} {apellidos}".strip()

    return combined or str(getattr(user, "email", "Usuario"))


def _get_facultad_label(user):
    carrera = getattr(user, "carrera", None)
    facultad = getattr(carrera, "facultad", None) if carrera else None

    return (
        str(getattr(facultad, "nombre", "") or "").strip()
        or str(getattr(user, "facultad_nombre", "") or "").strip()
        or "No registrada"
    )


def _get_carrera_label(user):
    carrera = getattr(user, "carrera", None)

    return (
        str(getattr(carrera, "nombre", "") or "").strip()
        or str(getattr(user, "carrera_nombre", "") or "").strip()
        or "No registrada"
    )


def _get_current_edit_limit(user):
    explicit_limit = getattr(user, "profile_edit_until", None)

    if explicit_limit:
        return explicit_limit

    fecha_registro = getattr(user, "fecha_registro", None)

    if fecha_registro:
        return fecha_registro + timedelta(hours=48)

    return None


def _profile_edit_is_available(user):
    if getattr(user, "profile_edit_locked", False):
        return False

    limit = _get_current_edit_limit(user)

    if limit is None:
        return True

    return timezone.now() <= limit


def _format_datetime(value):
    if not value:
        return "No disponible"

    try:
        local_value = timezone.localtime(value)
    except (ValueError, TypeError):
        local_value = value

    return local_value.strftime("%d/%m/%Y %H:%M")


def send_profile_edit_extension_request(
    *,
    user,
    motivo,
    horas_solicitadas=48,
    request=None,
):
    """
    Envía al administrador una solicitud real mediante el backend SMTP.

    Devuelve la cantidad de destinatarios que aceptó el backend de correo.
    """

    if _profile_edit_is_available(user):
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El periodo de edición todavía está disponible. "
                    "No es necesario solicitar una extensión."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    cooldown_seconds = int(
        getattr(
            settings,
            "PROFILE_EXTENSION_REQUEST_COOLDOWN_SECONDS",
            600,
        )
        or 600
    )

    cache_key = f"profile-extension-request:{user.pk}"

    if cache.get(cache_key):
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "Ya se envió una solicitud recientemente. "
                    "Espere unos minutos antes de intentarlo nuevamente."
                )
            },
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    recipients = get_profile_extension_admin_emails()
    display_name = _get_user_display_name(user)
    user_email = str(getattr(user, "email", "") or "").strip()
    identificacion = str(
        getattr(user, "identificacion", "") or "No registrada"
    )
    rol = str(getattr(user, "rol", "") or "Usuario")
    auth_source = str(
        getattr(user, "auth_source", "") or "No disponible"
    )
    edit_limit = _get_current_edit_limit(user)
    lock_reason = str(
        getattr(user, "profile_edit_lock_reason", "")
        or "El periodo habilitado finalizó."
    )

    ip_address = "No disponible"

    if request is not None:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip_address = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else request.META.get("REMOTE_ADDR", "No disponible")
        )

    subject = (
        "[SGPC ULEAM] Solicitud de extensión de perfil - "
        f"{display_name}"
    )

    text_body = f"""Se ha recibido una solicitud de extensión del plazo de edición del perfil.

DATOS DEL USUARIO
Nombre: {display_name}
Correo: {user_email or 'No disponible'}
Identificación: {identificacion}
Tipo de usuario: {rol}
Origen de autenticación: {auth_source}
Facultad: {_get_facultad_label(user)}
Carrera: {_get_carrera_label(user)}
Fecha de registro: {_format_datetime(getattr(user, 'fecha_registro', None))}
Límite anterior: {_format_datetime(edit_limit)}
Estado de bloqueo: {'Sí' if getattr(user, 'profile_edit_locked', False) else 'No'}
Motivo del bloqueo o vencimiento: {lock_reason}

SOLICITUD
Horas solicitadas: {horas_solicitadas}
Motivo indicado por el usuario:
{motivo}

DATOS DE CONTROL
ID del usuario: {user.pk}
Fecha de solicitud: {_format_datetime(timezone.now())}
Dirección IP: {ip_address}

Esta notificación fue generada automáticamente por SGPC ULEAM.
"""

    html_body = f"""
    <div style="font-family:Arial,sans-serif;color:#172033;line-height:1.55;max-width:720px">
      <h2 style="margin-bottom:8px">Solicitud de extensión del perfil</h2>
      <p style="margin-top:0">
        Un usuario de <strong>SGPC ULEAM</strong> solicita ampliar su plazo de edición.
      </p>

      <h3>Datos del usuario</h3>
      <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:6px 0"><strong>Nombre</strong></td><td>{escape(display_name)}</td></tr>
        <tr><td style="padding:6px 0"><strong>Correo</strong></td><td>{escape(user_email or 'No disponible')}</td></tr>
        <tr><td style="padding:6px 0"><strong>Identificación</strong></td><td>{escape(identificacion)}</td></tr>
        <tr><td style="padding:6px 0"><strong>Rol</strong></td><td>{escape(rol)}</td></tr>
        <tr><td style="padding:6px 0"><strong>Facultad</strong></td><td>{escape(_get_facultad_label(user))}</td></tr>
        <tr><td style="padding:6px 0"><strong>Carrera</strong></td><td>{escape(_get_carrera_label(user))}</td></tr>
        <tr><td style="padding:6px 0"><strong>Límite anterior</strong></td><td>{escape(_format_datetime(edit_limit))}</td></tr>
        <tr><td style="padding:6px 0"><strong>Extensión solicitada</strong></td><td>{horas_solicitadas} horas</td></tr>
      </table>

      <h3>Motivo</h3>
      <div style="padding:14px;border:1px solid #d9e1ee;border-radius:10px;background:#f7f9fc">
        {escape(motivo)}
      </div>

      <p style="margin-top:20px;color:#667085;font-size:13px">
        ID de usuario: {user.pk} · Solicitud: {escape(_format_datetime(timezone.now()))}
      </p>
    </div>
    """

    from_email_address = str(
        getattr(settings, "DEFAULT_FROM_EMAIL", "")
        or getattr(settings, "EMAIL_HOST_USER", "")
    ).strip()

    if not from_email_address:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El servidor no tiene configurado el correo remitente."
                )
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    from_email = formataddr(("SGPC ULEAM", from_email_address))

    reply_to = []
    if user_email:
        try:
            validate_email(user_email)
            reply_to = [user_email]
        except ValidationError:
            reply_to = []

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=recipients,
        reply_to=reply_to,
    )
    email.attach_alternative(html_body, "text/html")

    try:
        sent_count = email.send(fail_silently=False)
    except Exception as exc:
        logger.exception(
            "No se pudo enviar la solicitud de extensión del usuario %s",
            user.pk,
        )
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "El servidor no pudo enviar el correo. "
                    "Revise la configuración SMTP e inténtelo nuevamente."
                )
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from exc

    if sent_count < 1:
        raise ProfileExtensionRequestError(
            {"detail": "El servidor de correo no confirmó el envío."},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    cache.set(cache_key, True, timeout=max(60, cooldown_seconds))

    return {
        "sent_count": sent_count,
        "recipient_count": len(recipients),
        "requested_hours": int(horas_solicitadas),
    }