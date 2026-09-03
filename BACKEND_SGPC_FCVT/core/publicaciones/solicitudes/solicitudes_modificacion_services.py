"""Flujo controlado para modificar datos sensibles de publicaciones aprobadas."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.models import (
    Notificacion,
    Publicacion,
    SolicitudModificacionPublicacion,
)
from core.notificaciones.services.notificaciones_services import crear_notificacion
from core.publicaciones.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)

User = get_user_model()

BASE_SENSITIVE_FIELDS = {
    "anio_publicacion",
    "mes_publicacion",
    "origen_tipo",
    "origen_grado",
    "autores",
}

TYPE_SENSITIVE_FIELDS = {
    "ponencia": {
        "nombre_evento",
        "nombre_ponencia",
        "codigo_issn_isbn",
        "tipo_presentacion",
        "tipo_presentacion_otro",
        "link_evento",
        "revisor_par_arbitraje",
    },
    "articulo": {
        "nombre_articulo",
        "base_datos_indexada",
        "base_datos_otra",
        "codigo_doi",
        "codigo_issn",
        "nombre_revista",
        "numero_revista",
        "link_publicacion",
        "link_revista",
        "factor_impacto",
        "cuartil",
        "sjr",
        "jcr",
    },
    "libro": {
        "nombre_libro",
        "codigo_isbn",
        "editorial_compilador",
        "revisor_par_arbitraje",
        "link_libro",
    },
    "capitulo": {
        "nombre_capitulo",
        "nombre_libro",
        "codigo_isbn",
        "editor_compilador",
        "revisor_par_arbitraje",
        "link_capitulo",
    },
}


class SolicitudModificacionError(Exception):
    def __init__(self, detail, status_code=400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def _categoria(publicacion):
    codigo = str(getattr(getattr(publicacion, "tipo", None), "codigo", "") or "").lower()
    categoria = str(getattr(getattr(publicacion, "tipo", None), "categoria", "") or "").lower()
    if codigo in {"articulo", "articulo_regional", "articulo_alto_impacto"} or categoria == "articulo":
        return "articulo"
    if codigo in {"capitulo", "capitulo_libro"} or categoria == "capitulo":
        return "capitulo"
    if codigo == "ponencia" or categoria == "ponencia":
        return "ponencia"
    if codigo == "libro" or categoria == "libro":
        return "libro"
    return categoria or codigo


def campos_sensibles_permitidos(publicacion):
    return sorted(BASE_SENSITIVE_FIELDS | TYPE_SENSITIVE_FIELDS.get(_categoria(publicacion), set()))


def _current_value(publicacion, field):
    if field == "autores":
        return list(
            publicacion.participaciones.order_by("orden", "id").values(
                "autor_id", "orden"
            )
        )

    if field in BASE_SENSITIVE_FIELDS:
        return getattr(publicacion, field, None)

    relation_name = {
        "ponencia": "ponencia",
        "articulo": "articulo",
        "libro": "libro",
        "capitulo": "capitulo_libro",
    }.get(_categoria(publicacion))
    related = None
    if relation_name:
        try:
            related = getattr(publicacion, relation_name)
        except Exception:
            related = None
    return getattr(related, field, None) if related is not None else None


def snapshot_campos(publicacion, fields):
    return {field: _current_value(publicacion, field) for field in fields}


def validar_cambios_solicitados(publicacion, cambios):
    if not isinstance(cambios, dict) or not cambios:
        raise ValidationError({"cambios_solicitados": ["Debe indicar al menos un cambio."]})

    allowed = set(campos_sensibles_permitidos(publicacion))
    requested = {str(key).strip() for key in cambios.keys() if str(key).strip()}
    unauthorized = sorted(requested - allowed)
    if unauthorized:
        raise ValidationError({
            "cambios_solicitados": [
                "Uno o más campos no pueden modificarse mediante este flujo."
            ],
            "campos_no_permitidos": unauthorized,
            "campos_permitidos": sorted(allowed),
        })

    # Reutiliza todas las validaciones de la edición real sin guardar nada.
    serializer = PublicacionActualizacionSerializer(
        instance=publicacion,
        data=cambios,
        partial=True,
        context={"permitir_edicion_campania": True},
    )
    serializer.is_valid(raise_exception=True)

    before = snapshot_campos(publicacion, requested)
    # Evita solicitudes que no cambian ningún valor de forma efectiva.
    changed = []
    for field in sorted(requested):
        old = before.get(field)
        new = cambios.get(field)
        if field == "autores":
            old = [dict(item) for item in old or []]
        if old != new:
            changed.append(field)
    if not changed:
        raise ValidationError({"cambios_solicitados": ["Los valores enviados son iguales a los actuales."]})

    return changed, before


def _admins_activos():
    return User.objects.filter(is_active=True).filter(is_staff=True) | User.objects.filter(
        is_active=True, is_superuser=True
    )


def notificar_nueva_solicitud(solicitud):
    for admin in _admins_activos().distinct().iterator():
        crear_notificacion(
            destinatario=admin,
            tipo=Notificacion.TIPO_SOLICITUD_MODIFICACION_PUBLICACION,
            titulo="Solicitud de modificación de publicación",
            mensaje=(
                f"Se registró una solicitud para modificar la publicación "
                f"#{solicitud.publicacion_id}."
            ),
            publicacion=solicitud.publicacion,
            metadata={"solicitud_modificacion_id": solicitud.pk},
            enviar_email=True,
        )


def crear_solicitud(*, publicacion, solicitante, motivo, cambios, request=None):
    if publicacion.usuario_creador_id != getattr(solicitante, "pk", None):
        raise SolicitudModificacionError(
            {"detail": "Solo el usuario creador puede solicitar cambios sobre esta publicación."}, 403
        )
    if publicacion.estado != Publicacion.ESTADO_APROBADA:
        raise SolicitudModificacionError(
            {"detail": "Este flujo se utiliza únicamente para publicaciones aprobadas."}, 409
        )
    if SolicitudModificacionPublicacion.objects.filter(
        publicacion=publicacion,
        solicitante=solicitante,
        estado=SolicitudModificacionPublicacion.ESTADO_PENDIENTE,
    ).exists():
        raise SolicitudModificacionError(
            {"detail": "Ya existe una solicitud pendiente para esta publicación."}, 409
        )

    fields, before = validar_cambios_solicitados(publicacion, cambios)
    motivo = str(motivo or "").strip()
    if not motivo:
        raise SolicitudModificacionError({"motivo": ["Debe indicar el motivo de la modificación."]})

    with transaction.atomic():
        solicitud = SolicitudModificacionPublicacion.objects.create(
            publicacion=publicacion,
            solicitante=solicitante,
            motivo=motivo,
            campos_solicitados=fields,
            cambios_solicitados=cambios,
            datos_anteriores=before,
            publicacion_updated_at_solicitud=publicacion.updated_at,
        )
        registrar_evento_auditoria(
            actor=solicitante,
            accion="enviar",
            modulo="publicaciones",
            entidad=solicitud,
            descripcion="Se solicitó una modificación controlada de una publicación aprobada.",
            datos_anteriores=before,
            datos_nuevos=cambios,
            contexto={"publicacion_id": publicacion.pk, "campos": fields},
            request=request,
        )
        notificar_nueva_solicitud(solicitud)
    return solicitud


def cancelar_solicitud(solicitud, *, usuario, request=None):
    if solicitud.solicitante_id != getattr(usuario, "pk", None):
        raise SolicitudModificacionError({"detail": "No puede cancelar esta solicitud."}, 403)
    if solicitud.estado != SolicitudModificacionPublicacion.ESTADO_PENDIENTE:
        raise SolicitudModificacionError({"detail": "La solicitud ya fue resuelta."}, 409)
    solicitud.estado = SolicitudModificacionPublicacion.ESTADO_CANCELADA
    solicitud.resuelto_at = timezone.now()
    solicitud.save(update_fields=["estado", "resuelto_at", "updated_at"])
    registrar_evento_auditoria(
        actor=usuario,
        accion="cancelar",
        modulo="publicaciones",
        entidad=solicitud,
        descripcion="El usuario canceló su solicitud de modificación de publicación.",
        contexto={"publicacion_id": solicitud.publicacion_id},
        request=request,
    )
    return solicitud


def resolver_solicitud(solicitud, *, admin_user, aprobar, comentario="", request=None):
    with transaction.atomic():
        solicitud = (
            SolicitudModificacionPublicacion.objects.select_for_update()
            .select_related("publicacion", "publicacion__tipo", "solicitante")
            .get(pk=solicitud.pk)
        )
        if solicitud.estado != SolicitudModificacionPublicacion.ESTADO_PENDIENTE:
            raise SolicitudModificacionError({"detail": "La solicitud ya fue resuelta."}, 409)

        publicacion = Publicacion.objects.select_for_update(of=("self",)).select_related(
            "tipo", "ponencia", "articulo", "libro", "capitulo_libro"
        ).get(pk=solicitud.publicacion_id)

        if aprobar and publicacion.updated_at != solicitud.publicacion_updated_at_solicitud:
            raise SolicitudModificacionError(
                {
                    "detail": (
                        "La publicación cambió después de crear la solicitud. "
                        "Revise nuevamente los valores antes de aprobarla."
                    )
                },
                409,
            )

        now = timezone.now()
        comentario = str(comentario or "").strip()
        if aprobar:
            serializer = PublicacionActualizacionSerializer(
                instance=publicacion,
                data=solicitud.cambios_solicitados,
                partial=True,
                context={
                    "request": request,
                    "permitir_edicion_campania": True,
                    "origen_edicion": "solicitud_modificacion_aprobada",
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            solicitud.estado = SolicitudModificacionPublicacion.ESTADO_APROBADA
            solicitud.aplicado_at = now
            notif_type = Notificacion.TIPO_MODIFICACION_PUBLICACION_APROBADA
            notif_title = "Modificación de publicación aprobada"
            notif_message = "Su solicitud fue aprobada y los cambios autorizados ya fueron aplicados."
            audit_action = "aprobar"
        else:
            if not comentario:
                raise SolicitudModificacionError(
                    {"comentario": ["Debe indicar el motivo del rechazo."]}, 400
                )
            solicitud.estado = SolicitudModificacionPublicacion.ESTADO_RECHAZADA
            notif_type = Notificacion.TIPO_MODIFICACION_PUBLICACION_RECHAZADA
            notif_title = "Modificación de publicación rechazada"
            notif_message = f"Su solicitud fue rechazada. Motivo: {comentario}"
            audit_action = "rechazar"

        solicitud.revisor = admin_user
        solicitud.comentario_resolucion = comentario or None
        solicitud.resuelto_at = now
        solicitud.save(
            update_fields=[
                "estado",
                "revisor",
                "comentario_resolucion",
                "resuelto_at",
                "aplicado_at",
                "updated_at",
            ]
        )
        crear_notificacion(
            destinatario=solicitud.solicitante,
            tipo=notif_type,
            titulo=notif_title,
            mensaje=notif_message,
            publicacion=publicacion,
            metadata={"solicitud_modificacion_id": solicitud.pk},
            enviar_email=True,
        )
        registrar_evento_auditoria(
            actor=admin_user,
            accion=audit_action,
            modulo="publicaciones",
            entidad=solicitud,
            descripcion=(
                "Se aprobó y aplicó una solicitud de modificación de publicación."
                if aprobar
                else "Se rechazó una solicitud de modificación de publicación."
            ),
            datos_anteriores=solicitud.datos_anteriores,
            datos_nuevos=solicitud.cambios_solicitados if aprobar else {},
            contexto={
                "publicacion_id": publicacion.pk,
                "campos": solicitud.campos_solicitados,
                "comentario": comentario,
            },
            request=request,
        )
        return solicitud
