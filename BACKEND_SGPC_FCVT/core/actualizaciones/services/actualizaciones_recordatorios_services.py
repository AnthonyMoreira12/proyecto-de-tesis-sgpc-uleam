"""Avisos y recordatorios automáticos de información pendiente.

Este módulo reutiliza las campañas de actualización existentes. No crea una
segunda fuente de verdad: antes de decidir si debe avisar, recalcula cada
participación contra los datos actuales del usuario.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from core.actualizaciones.services.actualizaciones_services import (
    cerrar_notificaciones_actualizacion_participante,
    recalcular_participante,
)
from core.models import (
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    Notificacion,
)
from core.notificaciones.services.notificaciones_services import crear_notificacion


User = get_user_model()

RECORDATORIO_INTERVALO_DIAS = 3

TIPOS_NOTIFICACION_ACTUALIZACION = (
    Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
    Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
)


def _participaciones_usuario(usuario):
    return (
        CampaniaActualizacionUsuario.objects.filter(usuario=usuario)
        .select_related("campania", "usuario")
        .order_by("campania_id", "id")
    )


def _notificaciones_participante(participante):
    return Notificacion.objects.filter(
        destinatario_id=participante.usuario_id,
        tipo__in=TIPOS_NOTIFICACION_ACTUALIZACION,
        metadata__campania_id=participante.campania_id,
        metadata__participante_id=participante.pk,
    )


def _mensaje_participante(participante, *, recordatorio=False):
    campania = participante.campania

    if recordatorio:
        mensaje = (
            f'Aún tiene información pendiente en “{campania.titulo}”. '
            "Revise y complete los datos solicitados desde Información pendiente."
        )
    else:
        mensaje = (
            f'La actualización “{campania.titulo}” requiere que revise y complete '
            "información asociada a su cuenta en el SGPC."
        )

    if campania.fecha_fin:
        try:
            limite = timezone.localtime(campania.fecha_fin).strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            limite = str(campania.fecha_fin)
        mensaje += f" El periodo de actualización finaliza el {limite}."

    return mensaje


def _crear_aviso_visible(participante, *, recordatorio=False):
    """Crea una notificación interna visible para un pendiente concreto.

    Los recordatorios automáticos son internos. El envío de correo continúa
    siendo una decisión explícita de Administración y no se repite cada tres
    días de manera automática.
    """
    return crear_notificacion(
        destinatario=participante.usuario,
        tipo=(
            Notificacion.TIPO_RECORDATORIO_ACTUALIZACION
            if recordatorio
            else Notificacion.TIPO_CAMPANIA_ACTUALIZACION
        ),
        titulo=(
            "Recordatorio: información pendiente"
            if recordatorio
            else "Actualización de información requerida"
        ),
        mensaje=_mensaje_participante(
            participante,
            recordatorio=recordatorio,
        ),
        metadata={
            "campania_id": participante.campania_id,
            "campania_tipo": participante.campania.tipo,
            "participante_id": participante.pk,
            "campos_pendientes": participante.campos_pendientes,
            "recordatorio": bool(recordatorio),
            "automatico": True,
            "action": "ver_informacion_pendiente",
            "ruta": "/informacion-pendiente",
        },
        enviar_email=False,
        visible_en_bandeja=True,
    )


def _conteos_participante(participante):
    campos = list(participante.campos_pendientes or [])
    resumen = participante.resumen_pendientes or {}

    if participante.campania.tipo == CampaniaActualizacion.TIPO_PERFIL:
        return {
            "registros": 1 if campos else 0,
            "campos": len(campos),
        }

    registros = resumen.get("registros", [])
    if not isinstance(registros, list):
        registros = []

    total_campos = 0
    for registro in registros:
        if not isinstance(registro, dict):
            continue
        registro_campos = registro.get("campos", [])
        if isinstance(registro_campos, list):
            total_campos += len(registro_campos)

    if not registros and campos:
        total_campos = len(campos)

    return {
        "registros": len(registros),
        "campos": total_campos,
    }


def _campania_vigente(campania, *, now):
    if campania.estado != CampaniaActualizacion.ESTADO_ACTIVA:
        return False
    if campania.fecha_inicio and campania.fecha_inicio > now:
        return False
    if campania.fecha_fin and campania.fecha_fin <= now:
        return False
    return True


def _debe_generar_recordatorio(participante, *, now, intervalo):
    ultima = (
        _notificaciones_participante(participante)
        .filter(visible_en_bandeja=True)
        .order_by("-created_at", "-id")
        .first()
    )

    if ultima is None:
        return False

    return ultima.created_at <= now - intervalo


def sincronizar_avisos_actualizacion_usuario(
    usuario,
    *,
    now=None,
    intervalo_dias=RECORDATORIO_INTERVALO_DIAS,
    generar_recordatorios=True,
):
    """Recalcula pendientes y sincroniza su presencia en Notificaciones.

    Se invoca al entrar al área autenticada y puede ejecutarse periódicamente.
    La respuesta está pensada para alimentar el modal global del frontend.
    """
    current_time = now or timezone.now()
    intervalo = timedelta(days=max(1, int(intervalo_dias or 1)))

    resumen = {
        "requiere_actualizacion": False,
        "total_campanias": 0,
        "total_registros_pendientes": 0,
        "total_campos_pendientes": 0,
        "recordatorio_intervalo_dias": intervalo.days,
        "notificaciones_creadas": 0,
        "recordatorios_creados": 0,
        "por_tipo": {
            CampaniaActualizacion.TIPO_PERFIL: {
                "campanias": 0,
                "registros": 0,
                "campos": 0,
            },
            CampaniaActualizacion.TIPO_PUBLICACION: {
                "campanias": 0,
                "registros": 0,
                "campos": 0,
            },
            CampaniaActualizacion.TIPO_PROYECTO: {
                "campanias": 0,
                "registros": 0,
                "campos": 0,
            },
        },
        "participaciones": [],
    }

    for participante in _participaciones_usuario(usuario):
        campania = participante.campania

        if (
            participante.estado == CampaniaActualizacionUsuario.ESTADO_OMITIDA
            or not _campania_vigente(campania, now=current_time)
        ):
            cerrar_notificaciones_actualizacion_participante(
                participante,
                now=current_time,
            )
            continue

        participante = recalcular_participante(participante)

        if participante.estado == CampaniaActualizacionUsuario.ESTADO_COMPLETADA:
            continue

        notificaciones = _notificaciones_participante(participante)
        inicial_visible = notificaciones.filter(
            tipo=Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
            visible_en_bandeja=True,
        ).exists()

        if not inicial_visible:
            if _crear_aviso_visible(participante, recordatorio=False) is not None:
                resumen["notificaciones_creadas"] += 1
        elif generar_recordatorios and _debe_generar_recordatorio(
            participante,
            now=current_time,
            intervalo=intervalo,
        ):
            if _crear_aviso_visible(participante, recordatorio=True) is not None:
                resumen["notificaciones_creadas"] += 1
                resumen["recordatorios_creados"] += 1

        conteos = _conteos_participante(participante)
        tipo = campania.tipo
        bucket = resumen["por_tipo"].setdefault(
            tipo,
            {"campanias": 0, "registros": 0, "campos": 0},
        )
        bucket["campanias"] += 1
        bucket["registros"] += conteos["registros"]
        bucket["campos"] += conteos["campos"]

        resumen["total_campanias"] += 1
        resumen["total_registros_pendientes"] += conteos["registros"]
        resumen["total_campos_pendientes"] += conteos["campos"]
        resumen["participaciones"].append(
            {
                "id": participante.pk,
                "campania_id": campania.pk,
                "titulo": campania.titulo,
                "tipo": tipo,
                "estado": participante.estado,
                "fecha_fin": campania.fecha_fin,
                "campos_pendientes": participante.campos_pendientes,
                "registros_pendientes": conteos["registros"],
                "total_campos_pendientes": conteos["campos"],
            }
        )

    resumen["requiere_actualizacion"] = resumen["total_campanias"] > 0
    return resumen


def procesar_recordatorios_periodicos_actualizacion(
    *,
    now=None,
    intervalo_dias=RECORDATORIO_INTERVALO_DIAS,
):
    """Procesa todos los usuarios con campañas potencialmente pendientes.

    Está diseñado para un cron/systemd timer diario. La propia sincronización
    impide repetir avisos antes del intervalo configurado.
    """
    current_time = now or timezone.now()

    user_ids = list(
        CampaniaActualizacionUsuario.objects.filter(
            campania__estado=CampaniaActualizacion.ESTADO_ACTIVA,
        )
        .filter(
            Q(campania__fecha_inicio__isnull=True)
            | Q(campania__fecha_inicio__lte=current_time)
        )
        .filter(
            Q(campania__fecha_fin__isnull=True)
            | Q(campania__fecha_fin__gt=current_time)
        )
        .exclude(estado=CampaniaActualizacionUsuario.ESTADO_OMITIDA)
        .values_list("usuario_id", flat=True)
        .distinct()
    )

    totals = {
        "usuarios_procesados": 0,
        "usuarios_con_pendientes": 0,
        "notificaciones_creadas": 0,
        "recordatorios_creados": 0,
    }

    for usuario in User.objects.filter(pk__in=user_ids, is_active=True).order_by("pk"):
        result = sincronizar_avisos_actualizacion_usuario(
            usuario,
            now=current_time,
            intervalo_dias=intervalo_dias,
            generar_recordatorios=True,
        )
        totals["usuarios_procesados"] += 1
        totals["notificaciones_creadas"] += result["notificaciones_creadas"]
        totals["recordatorios_creados"] += result["recordatorios_creados"]
        if result["requiere_actualizacion"]:
            totals["usuarios_con_pendientes"] += 1

    return totals
