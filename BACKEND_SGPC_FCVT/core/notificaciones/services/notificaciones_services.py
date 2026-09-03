"""
Servicios de notificaciones internas y correo.

Reglas acordadas:

Autor / usuario creador:
- publicación enviada;
- publicación observada;
- publicación aprobada;
- publicación rechazada.

Administradores:
- nueva publicación para revisar;
- publicación corregida y reenviada.

El correo se ejecuta mediante ``transaction.on_commit``. Un fallo SMTP
se registra en la propia notificación y nunca revierte la operación
que originó el aviso.
"""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from core.models import Notificacion


logger = logging.getLogger(
    __name__
)

User = get_user_model()


def _text(
    value,
):
    return str(
        value
        or ""
    ).strip()


def _publication_reference(
    publicacion,
):
    if publicacion is None:
        return "la publicación"

    number = getattr(
        publicacion,
        "numero",
        None,
    )

    publication_id = getattr(
        publicacion,
        "pk",
        None,
    )

    type_name = ""

    publication_type = getattr(
        publicacion,
        "tipo",
        None,
    )

    if publication_type is not None:
        type_name = _text(
            getattr(
                publication_type,
                "nombre",
                None,
            )
        )

    if (
        type_name
        and number
    ):
        return (
            f"{type_name} #{number}"
        )

    if publication_id:
        return (
            f"publicación #{publication_id}"
        )

    return "la publicación"


def _frontend_url():
    return _text(
        getattr(
            settings,
            "FRONTEND_URL",
            "",
        )
    ).rstrip("/")


def _build_email_body(
    *,
    titulo,
    mensaje,
):
    lines = [
        titulo,
        "",
        mensaje,
        "",
        (
            "Ingrese al SGPC para consultar la "
            "información completa."
        ),
    ]

    frontend_url = (
        _frontend_url()
    )

    if frontend_url:
        lines.extend(
            [
                "",
                frontend_url,
            ]
        )

    lines.extend(
        [
            "",
            (
                "Este es un mensaje automático "
                "del SGPC ULEAM."
            ),
        ]
    )

    return "\n".join(
        lines
    )


def _update_email_status(
    notification_id,
    *,
    sent,
    error=None,
):
    values = {
        "email_intentado_at": (
            timezone.now()
        ),
        "email_enviado": bool(
            sent
        ),
        "email_error": (
            None
            if sent
            else (
                _text(
                    error
                )
                or (
                    "No fue posible enviar "
                    "el correo."
                )
            )
        ),
    }

    try:
        (
            Notificacion.objects
            .filter(
                pk=notification_id
            )
            .update(
                **values
            )
        )
    except Exception:
        logger.exception(
            (
                "No se pudo actualizar el estado "
                "de correo de la notificación %s."
            ),
            notification_id,
        )


def _send_notification_email(
    notification_id,
):
    try:
        notification = (
            Notificacion.objects
            .select_related(
                "destinatario",
                "publicacion",
            )
            .get(
                pk=notification_id
            )
        )
    except Notificacion.DoesNotExist:
        return

    email = _text(
        getattr(
            notification.destinatario,
            "email",
            None,
        )
    )

    if not email:
        _update_email_status(
            notification_id,
            sent=False,
            error=(
                "El destinatario no posee "
                "correo registrado."
            ),
        )
        return

    try:
        message = EmailMultiAlternatives(
            subject=(
                f"{notification.titulo} — SGPC ULEAM"
            ),
            body=_build_email_body(
                titulo=notification.titulo,
                mensaje=notification.mensaje,
            ),
            from_email=getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                None,
            ),
            to=[
                email,
            ],
        )

        sent_count = message.send(
            fail_silently=False
        )

        if int(
            sent_count
            or 0
        ) < 1:
            raise RuntimeError(
                "El backend de correo no confirmó el envío."
            )

    except Exception as exc:
        logger.exception(
            (
                "Falló el envío de correo para "
                "la notificación %s."
            ),
            notification_id,
        )

        _update_email_status(
            notification_id,
            sent=False,
            error=str(
                exc
            ),
        )
        return

    _update_email_status(
        notification_id,
        sent=True,
    )


def _schedule_email(
    notification,
):
    if not notification.email_programado:
        return

    notification_id = (
        notification.pk
    )

    transaction.on_commit(
        lambda: (
            _send_notification_email(
                notification_id
            )
        )
    )


def crear_notificacion(
    *,
    destinatario,
    tipo,
    titulo,
    mensaje,
    publicacion=None,
    metadata=None,
    enviar_email=True,
    visible_en_bandeja=True,
):
    """
    Crea la notificación interna.

    El registro interno forma parte de la transacción actual.
    El correo se agenda para después del COMMIT.
    """

    if destinatario is None:
        return None

    destination_email = _text(
        getattr(
            destinatario,
            "email",
            None,
        )
    )

    notification = Notificacion(
        destinatario=destinatario,
        tipo=tipo,
        titulo=_text(
            titulo
        ),
        mensaje=_text(
            mensaje
        ),
        publicacion=publicacion,
        metadata=(
            metadata
            if isinstance(
                metadata,
                dict,
            )
            else {}
        ),
        visible_en_bandeja=bool(
            visible_en_bandeja
        ),
        email_programado=bool(
            enviar_email
            and destination_email
        ),
    )

    notification.save()

    _schedule_email(
        notification
    )

    return notification


def _active_admins():
    return (
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
        .distinct()
        .order_by(
            "id"
        )
    )


def _notify_admins(
    *,
    publicacion,
    tipo,
    titulo,
    mensaje,
    metadata=None,
):
    notifications = []

    for admin in _active_admins():
        item = crear_notificacion(
            destinatario=admin,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            publicacion=publicacion,
            metadata=metadata,
            enviar_email=True,
        )

        if item is not None:
            notifications.append(
                item
            )

    return notifications


def notificar_envio_revision(
    *,
    publicacion,
):
    reference = (
        _publication_reference(
            publicacion
        )
    )

    notifications = []

    creator = getattr(
        publicacion,
        "usuario_creador",
        None,
    )

    if creator is not None:
        item = crear_notificacion(
            destinatario=creator,
            tipo=(
                Notificacion
                .TIPO_PUBLICACION_ENVIADA
            ),
            titulo=(
                "Publicación enviada a revisión"
            ),
            mensaje=(
                f"{reference} fue enviada a revisión "
                "correctamente."
            ),
            publicacion=publicacion,
            metadata={
                "estado": (
                    publicacion.estado
                ),
            },
            enviar_email=True,
        )

        if item is not None:
            notifications.append(
                item
            )

    notifications.extend(
        _notify_admins(
            publicacion=publicacion,
            tipo=(
                Notificacion
                .TIPO_NUEVA_PUBLICACION_REVISION
            ),
            titulo=(
                "Nueva publicación para revisar"
            ),
            mensaje=(
                f"{reference} ingresó a la bandeja "
                "de revisión."
            ),
            metadata={
                "estado": (
                    publicacion.estado
                ),
            },
        )
    )

    return notifications


def notificar_reenvio_revision(
    *,
    publicacion,
    revision_observacion_id=None,
):
    reference = (
        _publication_reference(
            publicacion
        )
    )

    return _notify_admins(
        publicacion=publicacion,
        tipo=(
            Notificacion
            .TIPO_PUBLICACION_REENVIADA
        ),
        titulo=(
            "Publicación corregida y reenviada"
        ),
        mensaje=(
            f"{reference} fue corregida y "
            "reenviada a revisión."
        ),
        metadata={
            "estado": (
                publicacion.estado
            ),
            "revision_observacion_id": (
                revision_observacion_id
            ),
        },
    )


def notificar_decision_revision(
    *,
    publicacion,
    decision,
    revision_id=None,
):
    creator = getattr(
        publicacion,
        "usuario_creador",
        None,
    )

    if creator is None:
        return None

    reference = (
        _publication_reference(
            publicacion
        )
    )

    config = {
        "observada": {
            "tipo": (
                Notificacion
                .TIPO_PUBLICACION_OBSERVADA
            ),
            "titulo": (
                "Publicación observada"
            ),
            "mensaje": (
                f"{reference} recibió observaciones. "
                "Ingrese al SGPC para consultar el "
                "detalle y realizar las correcciones."
            ),
        },
        "aprobada": {
            "tipo": (
                Notificacion
                .TIPO_PUBLICACION_APROBADA
            ),
            "titulo": (
                "Publicación aprobada"
            ),
            "mensaje": (
                f"{reference} fue aprobada "
                "correctamente."
            ),
        },
        "rechazada": {
            "tipo": (
                Notificacion
                .TIPO_PUBLICACION_RECHAZADA
            ),
            "titulo": (
                "Publicación rechazada"
            ),
            "mensaje": (
                f"{reference} fue rechazada. "
                "Ingrese al SGPC para consultar "
                "la decisión registrada."
            ),
        },
    }

    item = config.get(
        _text(
            decision
        ).lower()
    )

    if item is None:
        return None

    return crear_notificacion(
        destinatario=creator,
        tipo=item[
            "tipo"
        ],
        titulo=item[
            "titulo"
        ],
        mensaje=item[
            "mensaje"
        ],
        publicacion=publicacion,
        metadata={
            "estado": (
                publicacion.estado
            ),
            "revision_id": (
                revision_id
            ),
        },
        enviar_email=True,
    )


# ============================================================
# SOLICITUDES DE EXTENSIÓN DEL PERFIL
# ============================================================

def _notification_datetime(value):
    if not value:
        return ""

    try:
        value = timezone.localtime(value)
    except (ValueError, TypeError):
        pass

    try:
        return value.strftime("%d/%m/%Y %H:%M")
    except AttributeError:
        return _text(value)


def _user_display_name(user):
    if user is None:
        return "Usuario"

    full_name = _text(
        getattr(user, "get_full_name", lambda: "")()
    )
    if full_name:
        return full_name

    return (
        _text(getattr(user, "email", None))
        or f"Usuario #{getattr(user, 'pk', '—')}"
    )


def notificar_solicitud_extension_perfil(*, solicitud):
    """Notifica a todos los administradores una solicitud pendiente.

    La metadata conserva un snapshot suficiente para que la bandeja pueda
    mostrar usuario, correo, horas y motivo incluso antes de consultar el
    endpoint administrativo de detalle.
    """
    user = getattr(solicitud, "usuario", None)
    display_name = _user_display_name(user)
    user_email = _text(getattr(user, "email", None))

    metadata = {
        "solicitud_extension_id": solicitud.pk,
        "usuario_id": getattr(user, "pk", None),
        "usuario_nombre": display_name,
        "usuario_email": user_email,
        "horas_solicitadas": solicitud.horas_solicitadas,
        "horas_aprobadas": solicitud.horas_aprobadas,
        "estado_solicitud": solicitud.estado,
        "motivo": solicitud.motivo,
        "plazo_anterior": (
            solicitud.plazo_anterior.isoformat()
            if solicitud.plazo_anterior
            else None
        ),
        "nuevo_plazo": (
            solicitud.nuevo_plazo.isoformat()
            if solicitud.nuevo_plazo
            else None
        ),
        "solicitada_at": (
            solicitud.solicitada_at.isoformat()
            if solicitud.solicitada_at
            else None
        ),
        "action": "resolver_extension_perfil",
    }

    return _notify_admins(
        publicacion=None,
        tipo=Notificacion.TIPO_SOLICITUD_EXTENSION_PERFIL,
        titulo="Solicitud de extensión de perfil",
        mensaje=(
            f"{display_name} solicita {solicitud.horas_solicitadas} "
            "horas adicionales para editar su perfil."
        ),
        metadata=metadata,
    )


def notificar_resultado_extension_perfil(*, solicitud):
    """Notifica al usuario la decisión administrativa."""
    user = getattr(solicitud, "usuario", None)
    if user is None:
        return None

    approved = (
        solicitud.estado
        == solicitud.ESTADO_APROBADA
    )

    metadata = {
        "solicitud_extension_id": solicitud.pk,
        "usuario_id": getattr(user, "pk", None),
        "horas_solicitadas": solicitud.horas_solicitadas,
        "horas_aprobadas": solicitud.horas_aprobadas,
        "estado_solicitud": solicitud.estado,
        "nuevo_plazo": (
            solicitud.nuevo_plazo.isoformat()
            if solicitud.nuevo_plazo
            else None
        ),
        "motivo_resolucion": solicitud.motivo_resolucion,
        "action": "ver_perfil",
    }

    if approved:
        titulo = "Extensión de perfil aprobada"
        deadline = _notification_datetime(solicitud.nuevo_plazo)
        approved_hours = (
            solicitud.horas_aprobadas
            or solicitud.horas_solicitadas
        )
        mensaje = (
            "Su solicitud para ampliar el periodo de edición del perfil "
            f"fue aprobada por {approved_hours} horas. "
            "Ya puede realizar los cambios autorizados."
        )
        if deadline:
            mensaje += f" El nuevo plazo finaliza el {deadline}."
        notification_type = (
            Notificacion.TIPO_EXTENSION_PERFIL_APROBADA
        )
    else:
        titulo = "Solicitud de extensión rechazada"
        resolution = _text(solicitud.motivo_resolucion)
        mensaje = "Su solicitud de extensión del perfil fue rechazada."
        if resolution:
            mensaje += f" Motivo: {resolution}"
        notification_type = (
            Notificacion.TIPO_EXTENSION_PERFIL_RECHAZADA
        )

    return crear_notificacion(
        destinatario=user,
        tipo=notification_type,
        titulo=titulo,
        mensaje=mensaje,
        publicacion=None,
        metadata=metadata,
        enviar_email=True,
    )
