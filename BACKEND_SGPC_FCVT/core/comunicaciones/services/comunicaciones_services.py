"""Servicios de comunicación global y avisos vinculados a campañas."""

from django.db import transaction
from django.utils import timezone

from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.models import (
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    ComunicacionGlobal,
    Notificacion,
)
from core.notificaciones.services.notificaciones_services import crear_notificacion


def _text(value):
    return str(value or "").strip()


def _campaign_message(campania, *, reminder=False):
    if reminder:
        base = (
            "Aún tiene información pendiente dentro de la campaña "
            f'“{campania.titulo}”. Revise y complete los datos habilitados.'
        )
    else:
        base = (
            f'Se habilitó la campaña “{campania.titulo}” para que revise '
            "y complete información del SGPC."
        )

    if campania.fecha_fin:
        try:
            deadline = timezone.localtime(campania.fecha_fin).strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            deadline = str(campania.fecha_fin)
        base += f" El periodo finaliza el {deadline}."

    return base


def publicar_comunicacion_campania(campania, *, actor, request=None):
    """Crea o actualiza el comunicado textual asociado a una campaña."""
    if not campania.crear_aviso:
        return None

    comunicacion, _created = ComunicacionGlobal.objects.update_or_create(
        campania=campania,
        defaults={
            "titulo": campania.titulo,
            "mensaje": campania.descripcion or _campaign_message(campania),
            "tipo": ComunicacionGlobal.TIPO_ACTUALIZACION,
            "etiqueta_accion": "Revisar información",
            "ruta_accion": "/informacion-pendiente",
            "fecha_inicio": campania.fecha_inicio,
            "fecha_fin": campania.fecha_fin,
            "activa": True,
            "desactivada_at": None,
            "creado_por": actor,
        },
    )

    registrar_evento_auditoria(
        actor=actor,
        accion="publicar",
        modulo="comunicaciones",
        entidad=comunicacion,
        descripcion="Se publicó una comunicación global vinculada a una campaña.",
        contexto={"campania_id": campania.pk},
        request=request,
    )
    return comunicacion


def desactivar_comunicacion_campania(campania, *, actor, request=None):
    try:
        comunicacion = campania.comunicacion_global
    except ComunicacionGlobal.DoesNotExist:
        return None

    if comunicacion.activa:
        comunicacion.activa = False
        comunicacion.desactivada_at = timezone.now()
        comunicacion.save(update_fields=["activa", "desactivada_at", "updated_at"])
        registrar_evento_auditoria(
            actor=actor,
            accion="desactivar",
            modulo="comunicaciones",
            entidad=comunicacion,
            descripcion="Se desactivó la comunicación vinculada a la campaña cerrada.",
            contexto={"campania_id": campania.pk},
            request=request,
        )
    return comunicacion


def _participants_for_delivery(campania, *, only_pending):
    qs = campania.participantes.select_related("usuario").all()

    # El administrador que creó la campaña es el emisor,
    # no un destinatario de su propia comunicación.
    creator_id = getattr(campania, "creado_por_id", None)
    if creator_id:
        qs = qs.exclude(usuario_id=creator_id)

    if only_pending:
        qs = qs.exclude(
            estado__in=[
                CampaniaActualizacionUsuario.ESTADO_COMPLETADA,
                CampaniaActualizacionUsuario.ESTADO_OMITIDA,
            ]
        )
    return qs.order_by("usuario_id")


@transaction.atomic
def notificar_campania(
    campania,
    *,
    actor,
    request=None,
    recordatorio=False,
    solo_pendientes=False,
):
    """Distribuye notificación/correo a participantes de una campaña.

    Cuando una campaña solicita correo pero no notificación interna se crea un
    registro de Notificacion oculto de la bandeja. De esa forma se conserva el
    estado SMTP sin contradecir la preferencia de comunicación del admin.
    """
    visible = bool(campania.notificar_internamente)
    send_email = bool(campania.enviar_correo)

    if not visible and not send_email:
        return {
            "destinatarios": 0,
            "notificaciones_visibles": 0,
            "correos_programados": 0,
        }

    participants = list(
        _participants_for_delivery(campania, only_pending=solo_pendientes)
    )

    notification_type = (
        Notificacion.TIPO_RECORDATORIO_ACTUALIZACION
        if recordatorio
        else Notificacion.TIPO_CAMPANIA_ACTUALIZACION
    )
    title = (
        "Recordatorio: información pendiente"
        if recordatorio
        else "Actualización de información requerida"
    )
    message = _campaign_message(campania, reminder=recordatorio)

    visible_count = 0
    mail_count = 0
    created_count = 0

    for participant in participants:
        user = participant.usuario
        notification = crear_notificacion(
            destinatario=user,
            tipo=notification_type,
            titulo=title,
            mensaje=message,
            metadata={
                "campania_id": campania.pk,
                "campania_tipo": campania.tipo,
                "participante_id": participant.pk,
                "campos_pendientes": participant.campos_pendientes,
                "recordatorio": bool(recordatorio),
                "action": "ver_informacion_pendiente",
                "ruta": "/informacion-pendiente",
            },
            enviar_email=send_email,
            visible_en_bandeja=visible,
        )
        if notification is None:
            continue
        created_count += 1
        if notification.visible_en_bandeja:
            visible_count += 1
        if notification.email_programado:
            mail_count += 1

    registrar_evento_auditoria(
        actor=actor,
        accion="recordatorio" if recordatorio else "notificar",
        modulo="comunicaciones",
        entidad=campania,
        descripcion=(
            "Se enviaron recordatorios a participantes pendientes de la campaña."
            if recordatorio
            else "Se notificó la activación de la campaña a sus participantes."
        ),
        contexto={
            "campania_id": campania.pk,
            "solo_pendientes": bool(solo_pendientes),
            "registros_notificacion": created_count,
            "notificaciones_visibles": visible_count,
            "correos_programados": mail_count,
        },
        request=request,
    )

    return {
        "destinatarios": created_count,
        "notificaciones_visibles": visible_count,
        "correos_programados": mail_count,
    }
