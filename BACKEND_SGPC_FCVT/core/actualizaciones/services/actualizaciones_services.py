"""Motor de campañas globales de actualización de información."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status

from core.actualizaciones.services.actualizaciones_diagnostico_services import (
    diagnosticar_proyecto,
    diagnosticar_publicacion,
    diagnosticar_usuario_para_campania,
    publicacion_es_elegible_para_actualizacion,
)
from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.comunicaciones.services.comunicaciones_services import (
    desactivar_comunicacion_campania,
    notificar_campania,
    publicar_comunicacion_campania,
)
from core.models import (
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    Notificacion,
)


User = get_user_model()


class ActualizacionServiceError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(str(detail))
        self.detail = detail if isinstance(detail, dict) else {"detail": str(detail)}
        self.status_code = status_code


def _parse_positive_id(value, field):
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ActualizacionServiceError({field: "Debe indicar un identificador válido."}) from exc
    if parsed <= 0:
        raise ActualizacionServiceError({field: "Debe indicar un identificador válido."})
    return parsed


def destinatarios_queryset(campania):
    """Resuelve usuarios elegibles según el alcance de la campaña."""
    # "Todos" significa todos los usuarios activos del SGPC. Los permisos
    # administrativos (is_staff/is_superuser) no eximen a una persona de
    # completar información. Con ``solo_incompletos=True`` las cuentas que no
    # tengan nada pendiente quedarán fuera automáticamente.
    qs = User.objects.filter(is_active=True)
    filters = campania.filtros_destinatarios or {}

    if campania.alcance == CampaniaActualizacion.ALCANCE_SEDE:
        sede_id = _parse_positive_id(filters.get("sede_id"), "sede_id")
        qs = qs.filter(sede_id=sede_id)

    elif campania.alcance == CampaniaActualizacion.ALCANCE_FACULTAD:
        facultad_id = _parse_positive_id(filters.get("facultad_id"), "facultad_id")
        qs = qs.filter(carrera__facultad_id=facultad_id)

    elif campania.alcance == CampaniaActualizacion.ALCANCE_CARRERA:
        carrera_id = _parse_positive_id(filters.get("carrera_id"), "carrera_id")
        qs = qs.filter(carrera_id=carrera_id)

    elif campania.alcance == CampaniaActualizacion.ALCANCE_USUARIOS:
        raw_ids = filters.get("usuarios", [])
        if not isinstance(raw_ids, list) or not raw_ids:
            raise ActualizacionServiceError(
                {"usuarios": "Debe seleccionar al menos un usuario."}
            )
        ids = [_parse_positive_id(item, "usuarios") for item in raw_ids]
        qs = qs.filter(pk__in=ids)

    return qs.select_related("sede", "carrera", "carrera__facultad").order_by("pk")


def diagnostico_campania(campania):
    """Calcula el alcance real de una campaña antes de activarla.

    ``afectados_estimados`` respeta ``solo_incompletos``: si la campaña está
    limitada a registros incompletos, solo cuenta a quienes realmente tienen
    pendientes. En caso contrario, todos los destinatarios elegibles quedan
    incluidos aunque sus datos actuales ya estén completos.
    """
    candidates = list(destinatarios_queryset(campania))
    results = []
    incomplete = 0
    field_counts = {}

    for user in candidates:
        diagnosis = diagnosticar_usuario_para_campania(user, campania)
        pending = list(diagnosis.get("campos_pendientes", []) or [])

        if pending:
            incomplete += 1
            for field in pending:
                field_counts[field] = field_counts.get(field, 0) + 1

        results.append(
            {
                "usuario_id": user.pk,
                "nombre": f"{getattr(user, 'nombres', '')} {getattr(user, 'apellidos', '')}".strip(),
                "email": user.email,
                "campos_pendientes": pending,
                "resumen": diagnosis.get("resumen", {}),
            }
        )

    affected = incomplete if campania.solo_incompletos else len(results)

    return {
        "candidatos": len(results),
        "con_pendientes": incomplete,
        "sin_pendientes": len(results) - incomplete,
        "afectados_estimados": affected,
        "usuarios_por_campo": dict(sorted(field_counts.items())),
        "results": results,
    }


def _participant_state(pending):
    return (
        CampaniaActualizacionUsuario.ESTADO_PENDIENTE
        if pending
        else CampaniaActualizacionUsuario.ESTADO_COMPLETADA
    )



def sincronizar_participantes_campania(campania, *, diagnostic=None, now=None):
    """Sincroniza participantes con el diagnóstico actual de la campaña.

    Además de recalcular a los participantes existentes, incorpora usuarios que
    ahora cumplen el alcance y tienen información pendiente. Esto permite
    recuperar campañas activas antiguas que quedaron con cero participantes por
    reglas de destinatarios demasiado restrictivas.
    """
    current_time = now or timezone.now()
    diagnostic = diagnostic or diagnostico_campania(campania)

    users_by_id = {
        user.pk: user
        for user in destinatarios_queryset(campania)
    }
    existing = {
        participant.usuario_id: participant
        for participant in campania.participantes.select_related(
            "usuario",
            "campania",
        )
    }

    created = 0
    updated = 0
    completed = 0
    pending_count = 0
    skipped = 0
    new_participant_ids = []

    for item in diagnostic.get("results", []):
        user = users_by_id.get(item.get("usuario_id"))
        if user is None:
            continue

        pending = list(item.get("campos_pendientes", []) or [])
        participant = existing.get(user.pk)

        if campania.solo_incompletos and not pending:
            skipped += 1
            if participant is not None:
                CampaniaActualizacionUsuario.objects.filter(
                    pk=participant.pk
                ).update(
                    estado=CampaniaActualizacionUsuario.ESTADO_COMPLETADA,
                    campos_pendientes=[],
                    resumen_pendientes=item.get("resumen", {}),
                    completada_at=participant.completada_at or current_time,
                    updated_at=current_time,
                )
                participant.refresh_from_db()
                cerrar_notificaciones_actualizacion_participante(
                    participant,
                    now=current_time,
                )
                completed += 1
                updated += 1
            continue

        state = _participant_state(pending)
        completed_at = current_time if not pending else None

        if participant is not None and pending and participant.iniciada_at:
            state = CampaniaActualizacionUsuario.ESTADO_EN_PROGRESO

        if participant is None:
            participant = CampaniaActualizacionUsuario.objects.create(
                campania=campania,
                usuario=user,
                estado=state,
                campos_pendientes=pending,
                resumen_pendientes=item.get("resumen", {}),
                completada_at=completed_at,
            )
            existing[user.pk] = participant
            created += 1
            new_participant_ids.append(participant.pk)
        else:
            CampaniaActualizacionUsuario.objects.filter(
                pk=participant.pk
            ).update(
                estado=state,
                campos_pendientes=pending,
                resumen_pendientes=item.get("resumen", {}),
                completada_at=(
                    participant.completada_at or current_time
                    if not pending
                    else None
                ),
                updated_at=current_time,
            )
            participant.refresh_from_db()
            updated += 1

        if pending:
            pending_count += 1
        else:
            completed += 1
            cerrar_notificaciones_actualizacion_participante(
                participant,
                now=current_time,
            )

    return {
        "creados": created,
        "actualizados": updated,
        "pendientes": pending_count,
        "completados": completed,
        "omitidos_sin_pendientes": skipped,
        "nuevos_participantes": new_participant_ids,
        "diagnostico": {
            "candidatos": diagnostic.get("candidatos", 0),
            "con_pendientes": diagnostic.get("con_pendientes", 0),
            "sin_pendientes": diagnostic.get("sin_pendientes", 0),
            "afectados_estimados": diagnostic.get("afectados_estimados", 0),
            "usuarios_por_campo": diagnostic.get("usuarios_por_campo", {}),
        },
    }

def cerrar_notificaciones_actualizacion_participante(participant, *, now=None):
    """Cierra avisos internos de una participación que ya no requiere acción.

    Las notificaciones se conservan como historial, pero dejan de contabilizarse
    como pendientes cuando la información fue completada, la campaña terminó o
    la participación fue omitida.
    """
    if participant is None or not getattr(participant, "pk", None):
        return 0

    current_time = now or timezone.now()
    return (
        Notificacion.objects.filter(
            destinatario_id=participant.usuario_id,
            tipo__in=[
                Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
                Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
            ],
            metadata__campania_id=participant.campania_id,
            metadata__participante_id=participant.pk,
            leida=False,
        ).update(
            leida=True,
            leida_at=current_time,
        )
    )


def cerrar_notificaciones_actualizacion_campania(campania, *, now=None):
    """Marca como leídos los avisos pendientes al cerrar una campaña."""
    if campania is None or not getattr(campania, "pk", None):
        return 0

    current_time = now or timezone.now()
    return (
        Notificacion.objects.filter(
            tipo__in=[
                Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
                Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
            ],
            metadata__campania_id=campania.pk,
            leida=False,
        ).update(
            leida=True,
            leida_at=current_time,
        )
    )


@transaction.atomic
def activar_campania(campania, *, admin_user, request=None):
    locked = CampaniaActualizacion.objects.select_for_update().get(pk=campania.pk)

    if locked.estado == CampaniaActualizacion.ESTADO_ACTIVA:
        raise ActualizacionServiceError("La campaña ya se encuentra activa.")
    if locked.estado in {
        CampaniaActualizacion.ESTADO_FINALIZADA,
        CampaniaActualizacion.ESTADO_CANCELADA,
    }:
        raise ActualizacionServiceError(
            "Una campaña finalizada o cancelada no puede activarse nuevamente."
        )

    now = timezone.now()
    if locked.fecha_fin and locked.fecha_fin <= now:
        raise ActualizacionServiceError({"fecha_fin": "La campaña ya se encuentra vencida."})

    diagnostic = diagnostico_campania(locked)

    if diagnostic["afectados_estimados"] <= 0:
        raise ActualizacionServiceError(
            {
                "detail": (
                    "No se puede activar la campaña porque ningún usuario "
                    "requiere completar los campos seleccionados para el "
                    "alcance actual. Revise el diagnóstico o cambie los "
                    "criterios de la campaña."
                ),
                "diagnostico": {
                    "candidatos": diagnostic["candidatos"],
                    "con_pendientes": diagnostic["con_pendientes"],
                    "sin_pendientes": diagnostic["sin_pendientes"],
                    "afectados_estimados": diagnostic["afectados_estimados"],
                    "usuarios_por_campo": diagnostic["usuarios_por_campo"],
                },
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    sync_result = sincronizar_participantes_campania(
        locked,
        diagnostic=diagnostic,
        now=now,
    )
    created = sync_result["creados"]
    completed = sync_result["completados"]
    skipped = sync_result["omitidos_sin_pendientes"]

    locked.estado = CampaniaActualizacion.ESTADO_ACTIVA
    locked.activada_at = now
    if locked.fecha_inicio is None:
        locked.fecha_inicio = now
    locked.save(update_fields=["estado", "activada_at", "fecha_inicio", "updated_at"])

    registrar_evento_auditoria(
        actor=admin_user,
        accion="activar",
        modulo="actualizaciones",
        entidad=locked,
        descripcion="Se activó una campaña global de actualización.",
        datos_nuevos={
            "estado": locked.estado,
            "participantes": created,
            "completos_al_activar": completed,
            "omitidos_sin_pendientes": skipped,
        },
        contexto={"tipo": locked.tipo, "alcance": locked.alcance},
        request=request,
    )

    publicar_comunicacion_campania(
        locked,
        actor=admin_user,
        request=request,
    )
    notificar_campania(
        locked,
        actor=admin_user,
        request=request,
        recordatorio=False,
        solo_pendientes=False,
    )

    return locked


@transaction.atomic
def finalizar_campania(campania, *, admin_user, request=None, cancelar=False):
    locked = CampaniaActualizacion.objects.select_for_update().get(pk=campania.pk)
    if locked.estado not in {
        CampaniaActualizacion.ESTADO_BORRADOR,
        CampaniaActualizacion.ESTADO_ACTIVA,
    }:
        raise ActualizacionServiceError("La campaña ya se encuentra cerrada.")

    previous = locked.estado
    locked.estado = (
        CampaniaActualizacion.ESTADO_CANCELADA
        if cancelar
        else CampaniaActualizacion.ESTADO_FINALIZADA
    )
    locked.finalizada_at = timezone.now()
    locked.save(update_fields=["estado", "finalizada_at", "updated_at"])

    registrar_evento_auditoria(
        actor=admin_user,
        accion="cancelar" if cancelar else "finalizar",
        modulo="actualizaciones",
        entidad=locked,
        descripcion=(
            "Se canceló una campaña global de actualización."
            if cancelar
            else "Se finalizó una campaña global de actualización."
        ),
        datos_anteriores={"estado": previous},
        datos_nuevos={"estado": locked.estado},
        request=request,
    )
    desactivar_comunicacion_campania(
        locked,
        actor=admin_user,
        request=request,
    )
    cerrar_notificaciones_actualizacion_campania(
        locked,
        now=locked.finalizada_at,
    )
    return locked


def recalcular_participante(participant):
    """Actualiza pendientes y progreso después de una edición del usuario."""
    diagnosis = diagnosticar_usuario_para_campania(participant.usuario, participant.campania)
    pending = diagnosis.get("campos_pendientes", [])
    now = timezone.now()

    if not pending:
        state = CampaniaActualizacionUsuario.ESTADO_COMPLETADA
        completed_at = participant.completada_at or now
    else:
        state = (
            CampaniaActualizacionUsuario.ESTADO_EN_PROGRESO
            if participant.iniciada_at
            else CampaniaActualizacionUsuario.ESTADO_PENDIENTE
        )
        completed_at = None

    CampaniaActualizacionUsuario.objects.filter(pk=participant.pk).update(
        estado=state,
        campos_pendientes=pending,
        resumen_pendientes=diagnosis.get("resumen", {}),
        completada_at=completed_at,
        updated_at=now,
    )
    participant.refresh_from_db()

    if not pending:
        cerrar_notificaciones_actualizacion_participante(
            participant,
            now=now,
        )

    return participant


def campanias_activas_para_usuario(usuario, *, tipo=None):
    now = timezone.now()
    qs = CampaniaActualizacionUsuario.objects.filter(
        usuario=usuario,
        campania__estado=CampaniaActualizacion.ESTADO_ACTIVA,
    ).filter(Q(campania__fecha_inicio__isnull=True) | Q(campania__fecha_inicio__lte=now)).filter(
        Q(campania__fecha_fin__isnull=True) | Q(campania__fecha_fin__gt=now)
    )
    if tipo:
        qs = qs.filter(campania__tipo=tipo)
    return qs.select_related("campania", "usuario").order_by("campania__fecha_fin", "campania_id")


def usuario_puede_editar_campo_por_campania(usuario, *, tipo, campo):
    """Devuelve una participación vigente que habilite el campo indicado."""
    for participant in campanias_activas_para_usuario(usuario, tipo=tipo):
        if participant.estado == CampaniaActualizacionUsuario.ESTADO_OMITIDA:
            continue
        if campo in (participant.campania.campos_habilitados or []):
            return participant
    return None


def _normalizar_campos_registro(tipo, requested_fields):
    """Traduce campos auxiliares del frontend al contrato lógico de campaña."""
    aliases = {
        CampaniaActualizacion.TIPO_PUBLICACION: {
            "facultad": "carrera",
        },
        CampaniaActualizacion.TIPO_PROYECTO: {
            "facultad": "carrera",
        },
    }.get(tipo, {})

    return {
        aliases.get(str(field), str(field))
        for field in (requested_fields or [])
        if str(field or "").strip()
    }


def _registro_pertenece_al_usuario(usuario, *, tipo, registro):
    if usuario is None or registro is None or not getattr(usuario, "pk", None):
        return False

    if tipo == CampaniaActualizacion.TIPO_PUBLICACION:
        return getattr(registro, "usuario_creador_id", None) == usuario.pk

    if tipo == CampaniaActualizacion.TIPO_PROYECTO:
        return registro.participaciones.filter(
            autor__usuario_id=usuario.pk,
        ).exists()

    return False


def _diagnosticar_registro_para_campania(registro, campania):
    if campania.tipo == CampaniaActualizacion.TIPO_PUBLICACION:
        return diagnosticar_publicacion(registro, campania.campos_habilitados)
    if campania.tipo == CampaniaActualizacion.TIPO_PROYECTO:
        return diagnosticar_proyecto(registro, campania.campos_habilitados)
    return {"campos_pendientes": [], "resumen": {}}


def autorizacion_edicion_registro_por_campania(
    usuario,
    *,
    tipo,
    registro,
    requested_fields=None,
):
    """Resuelve edición extraordinaria de Publicación/Proyecto por campaña.

    La autorización exige simultáneamente:
    - usuario participante de una campaña vigente del tipo correcto;
    - pertenencia del registro al usuario (creador de publicación o integrante
      del proyecto);
    - para publicaciones, que el registro esté aprobado;
    - si la campaña es ``solo_incompletos``, que el registro aún tenga al
      menos un dato pendiente de esa campaña;
    - que todos los campos solicitados estén expresamente habilitados.
    """
    if not _registro_pertenece_al_usuario(usuario, tipo=tipo, registro=registro):
        return None

    # Una campaña de publicaciones nunca abre una vía extraordinaria de edición
    # para borradores, registros en revisión, observados o rechazados. Esos
    # estados deben resolverse dentro del flujo ordinario de la publicación.
    if (
        tipo == CampaniaActualizacion.TIPO_PUBLICACION
        and not publicacion_es_elegible_para_actualizacion(registro)
    ):
        return None

    eligible = []
    allowed = set()
    record_pending = set()

    for participant in campanias_activas_para_usuario(usuario, tipo=tipo):
        if participant.estado == CampaniaActualizacionUsuario.ESTADO_OMITIDA:
            continue

        campaign = participant.campania
        diagnosis = _diagnosticar_registro_para_campania(registro, campaign)
        pending = set(diagnosis.get("campos_pendientes", []))

        if campaign.solo_incompletos and not pending:
            continue

        eligible.append(participant)
        allowed.update(campaign.campos_habilitados or [])
        record_pending.update(pending)

    if not eligible:
        return None

    requested = _normalizar_campos_registro(tipo, requested_fields)
    unauthorized = sorted(requested - allowed)

    return {
        "authorized": not unauthorized,
        "allowed_fields": sorted(allowed),
        "requested_fields": sorted(requested),
        "unauthorized_fields": unauthorized,
        "pending_fields": sorted(record_pending),
        "participant_ids": [item.pk for item in eligible],
        "campaign_ids": [item.campania_id for item in eligible],
    }


def actualizar_progreso_participantes_campania(usuario, participant_ids):
    """Marca inicio y recalcula las campañas afectadas por una edición válida."""
    ids = [int(value) for value in (participant_ids or []) if value]
    if not ids:
        return []

    participants = list(
        CampaniaActualizacionUsuario.objects.filter(
            pk__in=ids,
            usuario=usuario,
        ).select_related("campania", "usuario")
    )
    now = timezone.now()

    for participant in participants:
        if participant.iniciada_at is None:
            participant.iniciada_at = now
            participant.estado = CampaniaActualizacionUsuario.ESTADO_EN_PROGRESO
            participant.save(
                update_fields=["iniciada_at", "estado", "updated_at"]
            )
        recalcular_participante(participant)

    return participants


def progreso_campania(campania):
    stats = campania.participantes.values("estado").annotate(total=Count("id"))
    counts = {row["estado"]: row["total"] for row in stats}
    total = sum(counts.values())
    completed = counts.get(CampaniaActualizacionUsuario.ESTADO_COMPLETADA, 0)
    percentage = round((completed / total) * 100, 2) if total else 0.0
    return {
        "total": total,
        "pendientes": counts.get(CampaniaActualizacionUsuario.ESTADO_PENDIENTE, 0),
        "en_progreso": counts.get(CampaniaActualizacionUsuario.ESTADO_EN_PROGRESO, 0),
        "completadas": completed,
        "omitidas": counts.get(CampaniaActualizacionUsuario.ESTADO_OMITIDA, 0),
        "porcentaje": percentage,
    }
