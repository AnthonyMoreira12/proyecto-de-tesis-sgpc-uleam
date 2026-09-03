"""Flujo de solicitudes de extensión del plazo de edición del perfil.

La solicitud se guarda en base de datos y las notificaciones internas son el
canal principal. Los correos se programan mediante el servicio de
notificaciones después del COMMIT y nunca revierten una solicitud o decisión.
"""

from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status

from core.auth.services.auth_profile_services import (
    get_profile_edit_deadline,
    get_profile_edit_status,
)
from core.models.notificaciones import (
    Notificacion,
    SolicitudExtensionPerfil,
)
from core.notificaciones.services.notificaciones_services import (
    notificar_resultado_extension_perfil,
    notificar_solicitud_extension_perfil,
)


class ProfileExtensionRequestError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def _text(value):
    return str(value or "").strip()


def _get_user_display_name(user):
    full_name = _text(
        getattr(user, "get_full_name", lambda: "")()
    )
    return (
        full_name
        or _text(getattr(user, "email", None))
        or f"Usuario #{getattr(user, 'pk', '—')}"
    )


def _get_current_edit_limit(user):
    """Devuelve el plazo real vigente antes de crear la solicitud.

    Reutiliza la misma regla del servicio principal del perfil:

    1. ``profile_edit_until`` cuando existe.
    2. ``fecha_registro + 48 horas`` para el periodo inicial.
    3. ``None`` cuando no hay una fecha de referencia.

    Esto evita guardar ``fecha_registro`` como si fuera la fecha límite.
    """
    return get_profile_edit_deadline(user)


def _profile_edit_is_available(user):
    """Usa una única fuente de verdad para el permiso de edición."""
    return bool(
        get_profile_edit_status(user).get(
            "available",
            False,
        )
    )


def _client_ip(request):
    if request is None:
        return None
    forwarded = _text(request.META.get("HTTP_X_FORWARDED_FOR", ""))
    raw = forwarded.split(",")[0].strip() if forwarded else _text(
        request.META.get("REMOTE_ADDR", "")
    )
    return raw or None


def serialize_profile_extension_request(solicitud):
    user = getattr(solicitud, "usuario", None)
    resolver = getattr(solicitud, "resuelta_por", None)
    return {
        "id": solicitud.pk,
        "usuario_id": solicitud.usuario_id,
        "usuario_nombre": _get_user_display_name(user),
        "usuario_email": _text(getattr(user, "email", None)),
        "horas_solicitadas": solicitud.horas_solicitadas,
        "horas_aprobadas": solicitud.horas_aprobadas,
        "motivo": solicitud.motivo,
        "estado": solicitud.estado,
        "estado_label": solicitud.get_estado_display(),
        "plazo_anterior": solicitud.plazo_anterior,
        "nuevo_plazo": solicitud.nuevo_plazo,
        "solicitada_at": solicitud.solicitada_at,
        "resuelta_at": solicitud.resuelta_at,
        "resuelta_por_id": solicitud.resuelta_por_id,
        "resuelta_por_nombre": (
            _get_user_display_name(resolver)
            if resolver is not None
            else ""
        ),
        "motivo_resolucion": solicitud.motivo_resolucion,
    }


def get_current_profile_extension_request(user):
    """Retorna la pendiente actual o, si no existe, la última solicitud."""
    qs = (
        SolicitudExtensionPerfil.objects
        .select_related("usuario", "resuelta_por")
        .filter(usuario=user)
    )
    pending = qs.filter(
        estado=SolicitudExtensionPerfil.ESTADO_PENDIENTE
    ).first()
    return pending or qs.first()


def create_profile_edit_extension_request(
    *, user, motivo, horas_solicitadas, request=None
):
    motivo = _text(motivo)
    try:
        hours = int(horas_solicitadas)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ProfileExtensionRequestError(
            {"horas_solicitadas": "El tiempo solicitado no es válido."}
        ) from exc

    if hours not in {24, 48, 72}:
        raise ProfileExtensionRequestError(
            {"horas_solicitadas": "Seleccione 24, 48 o 72 horas."}
        )

    if len(motivo) < 20:
        raise ProfileExtensionRequestError(
            {"motivo": "El motivo debe contener al menos 20 caracteres."}
        )
    if len(motivo) > 1000:
        raise ProfileExtensionRequestError(
            {"motivo": "El motivo no puede superar 1000 caracteres."}
        )

    if _profile_edit_is_available(user):
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "Su perfil todavía se encuentra dentro del periodo "
                    "habilitado de edición."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    try:
        with transaction.atomic():
            locked_user = (
                type(user).objects
                .select_for_update()
                .get(pk=user.pk)
            )

            # Revalidamos después de adquirir el bloqueo de fila. Entre la
            # comprobación inicial y esta transacción un administrador pudo
            # haber habilitado el perfil; en ese caso ya no corresponde crear
            # una solicitud pendiente.
            if _profile_edit_is_available(locked_user):
                raise ProfileExtensionRequestError(
                    {
                        "detail": (
                            "Su perfil ya se encuentra dentro del periodo "
                            "habilitado de edición."
                        )
                    },
                    status_code=status.HTTP_409_CONFLICT,
                )

            pending = (
                SolicitudExtensionPerfil.objects
                .select_for_update()
                .filter(
                    usuario=locked_user,
                    estado=SolicitudExtensionPerfil.ESTADO_PENDIENTE,
                )
                .first()
            )
            if pending is not None:
                raise ProfileExtensionRequestError(
                    {
                        "detail": (
                            "Ya tiene una solicitud de extensión pendiente "
                            "de revisión administrativa."
                        ),
                        "solicitud": serialize_profile_extension_request(
                            pending
                        ),
                    },
                    status_code=status.HTTP_409_CONFLICT,
                )

            solicitud = SolicitudExtensionPerfil.objects.create(
                usuario=locked_user,
                horas_solicitadas=hours,
                motivo=motivo,
                plazo_anterior=_get_current_edit_limit(locked_user),
                ip_solicitud=_client_ip(request),
            )

            # Canal principal: notificación interna. El correo asociado se
            # ejecuta después del commit y sus fallos no revierten la solicitud.
            notificar_solicitud_extension_perfil(
                solicitud=solicitud
            )

            return solicitud
    except ProfileExtensionRequestError:
        raise
    except IntegrityError as exc:
        raise ProfileExtensionRequestError(
            {
                "detail": (
                    "Ya existe una solicitud pendiente para este perfil."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        ) from exc


def list_profile_extension_requests(
    *,
    estado="pendiente",
    limit=20,
    usuario_id=None,
):
    estado = _text(estado).lower() or "pendiente"
    valid_states = {
        "todos",
        SolicitudExtensionPerfil.ESTADO_PENDIENTE,
        SolicitudExtensionPerfil.ESTADO_APROBADA,
        SolicitudExtensionPerfil.ESTADO_RECHAZADA,
    }
    if estado not in valid_states:
        raise ProfileExtensionRequestError(
            {"estado": "El estado solicitado no es válido."}
        )

    try:
        limit = max(1, min(int(limit or 20), 100))
    except (TypeError, ValueError, OverflowError):
        limit = 20

    qs = (
        SolicitudExtensionPerfil.objects
        .select_related("usuario", "resuelta_por")
        .all()
    )
    if estado != "todos":
        qs = qs.filter(estado=estado)

    if usuario_id not in (None, ""):
        try:
            normalized_user_id = int(usuario_id)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ProfileExtensionRequestError(
                {"usuario_id": "El usuario solicitado no es válido."}
            ) from exc

        if normalized_user_id < 1:
            raise ProfileExtensionRequestError(
                {"usuario_id": "El usuario solicitado no es válido."}
            )

        qs = qs.filter(usuario_id=normalized_user_id)

    total = qs.count()
    results = [
        serialize_profile_extension_request(item)
        for item in qs[:limit]
    ]
    return {"count": total, "results": results}


def get_profile_extension_request_for_admin(pk):
    try:
        return (
            SolicitudExtensionPerfil.objects
            .select_related("usuario", "resuelta_por")
            .get(pk=pk)
        )
    except SolicitudExtensionPerfil.DoesNotExist as exc:
        raise ProfileExtensionRequestError(
            {"detail": "La solicitud no existe."},
            status_code=status.HTTP_404_NOT_FOUND,
        ) from exc


def resolve_profile_edit_extension_request(
    *,
    solicitud_id,
    admin_user,
    decision,
    motivo_resolucion="",
    horas_aprobadas=None,
):
    decision = _text(decision).lower()
    motivo_resolucion = _text(motivo_resolucion)

    aliases = {
        "aprobar": SolicitudExtensionPerfil.ESTADO_APROBADA,
        "aprobada": SolicitudExtensionPerfil.ESTADO_APROBADA,
        "rechazar": SolicitudExtensionPerfil.ESTADO_RECHAZADA,
        "rechazada": SolicitudExtensionPerfil.ESTADO_RECHAZADA,
    }
    target_state = aliases.get(decision)
    if target_state is None:
        raise ProfileExtensionRequestError(
            {"decision": "Use 'aprobar' o 'rechazar'."}
        )

    approved_hours = None
    if target_state == SolicitudExtensionPerfil.ESTADO_APROBADA:
        if horas_aprobadas in (None, ""):
            approved_hours = None
        else:
            try:
                approved_hours = int(horas_aprobadas)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ProfileExtensionRequestError(
                    {
                        "horas_aprobadas": (
                            "El número de horas aprobadas no es válido."
                        )
                    }
                ) from exc

            if approved_hours not in {6, 12, 24, 48, 72}:
                raise ProfileExtensionRequestError(
                    {
                        "horas_aprobadas": (
                            "Seleccione 6, 12, 24, 48 o 72 horas."
                        )
                    }
                )

    if (
        target_state == SolicitudExtensionPerfil.ESTADO_RECHAZADA
        and len(motivo_resolucion) < 10
    ):
        raise ProfileExtensionRequestError(
            {
                "motivo_resolucion": (
                    "Indique un motivo de rechazo de al menos 10 caracteres."
                )
            }
        )

    # Leemos primero el usuario asociado sin bloquear. Dentro de la
    # transacción bloqueamos siempre en el mismo orden que los demás flujos:
    # usuario -> solicitud. Esto reduce el riesgo de interbloqueos cuando una
    # resolución coincide con una acción administrativa sobre el perfil.
    try:
        request_reference = (
            SolicitudExtensionPerfil.objects
            .only("id", "usuario_id")
            .get(pk=solicitud_id)
        )
    except SolicitudExtensionPerfil.DoesNotExist as exc:
        raise ProfileExtensionRequestError(
            {"detail": "La solicitud no existe."},
            status_code=status.HTTP_404_NOT_FOUND,
        ) from exc

    user_model = SolicitudExtensionPerfil._meta.get_field("usuario").remote_field.model

    with transaction.atomic():
        user = (
            user_model.objects
            .select_for_update()
            .get(pk=request_reference.usuario_id)
        )

        try:
            solicitud = (
                SolicitudExtensionPerfil.objects
                .select_for_update()
                .get(pk=solicitud_id)
            )
        except SolicitudExtensionPerfil.DoesNotExist as exc:
            raise ProfileExtensionRequestError(
                {"detail": "La solicitud no existe."},
                status_code=status.HTTP_404_NOT_FOUND,
            ) from exc

        if solicitud.usuario_id != user.pk:
            raise ProfileExtensionRequestError(
                {
                    "detail": (
                        "La solicitud cambió mientras se procesaba. "
                        "Actualice la vista e intente nuevamente."
                    )
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        if solicitud.estado != SolicitudExtensionPerfil.ESTADO_PENDIENTE:
            raise ProfileExtensionRequestError(
                {
                    "detail": (
                        "Esta solicitud ya fue resuelta y no puede "
                        "procesarse nuevamente."
                    ),
                    "solicitud": serialize_profile_extension_request(
                        solicitud
                    ),
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        now = timezone.now()
        if target_state == SolicitudExtensionPerfil.ESTADO_APROBADA:
            hours_to_apply = (
                approved_hours
                if approved_hours is not None
                else solicitud.horas_solicitadas
            )
            current_limit = getattr(user, "profile_edit_until", None)
            base = (
                current_limit
                if current_limit and current_limit > now
                else now
            )
            user.profile_edit_until = base + timedelta(
                hours=hours_to_apply
            )
            user.profile_edit_attempts_left = max(
                int(
                    getattr(user, "profile_edit_attempts_left", 0)
                    or 0
                ),
                3,
            )
            user.profile_edit_locked = False
            user.profile_edit_lock_reason = None
            user.save(
                update_fields=[
                    "profile_edit_until",
                    "profile_edit_attempts_left",
                    "profile_edit_locked",
                    "profile_edit_lock_reason",
                ]
            )
            solicitud.horas_aprobadas = hours_to_apply
            solicitud.nuevo_plazo = user.profile_edit_until
        else:
            solicitud.horas_aprobadas = None
            solicitud.nuevo_plazo = None

        solicitud.estado = target_state
        solicitud.resuelta_at = now
        solicitud.resuelta_por = admin_user
        solicitud.motivo_resolucion = motivo_resolucion
        solicitud.save(
            update_fields=[
                "estado",
                "horas_aprobadas",
                "nuevo_plazo",
                "resuelta_at",
                "resuelta_por",
                "motivo_resolucion",
            ]
        )

        # Una vez resuelta, las copias de la solicitud que recibieron
        # otros administradores dejan de contar como pendientes en la
        # campana. El registro se conserva para trazabilidad.
        (
            Notificacion.objects
            .filter(
                tipo=Notificacion.TIPO_SOLICITUD_EXTENSION_PERFIL,
                metadata__solicitud_extension_id=solicitud.pk,
                leida=False,
            )
            .update(
                leida=True,
                leida_at=now,
            )
        )

        notificar_resultado_extension_perfil(
            solicitud=solicitud
        )

        return solicitud


def send_profile_edit_extension_request(
    *, user, motivo, horas_solicitadas=48, request=None
):
    """Compatibilidad temporal con integraciones del flujo SMTP anterior.

    La solicitud ya no depende del envío directo de correo: se registra en
    base de datos y se distribuye mediante el sistema interno de
    notificaciones. El correo, cuando corresponde, queda programado por el
    servicio general de notificaciones después del commit.
    """
    solicitud = create_profile_edit_extension_request(
        user=user,
        motivo=motivo,
        horas_solicitadas=horas_solicitadas,
        request=request,
    )
    recipient_count = (
        Notificacion.objects
        .filter(
            tipo=Notificacion.TIPO_SOLICITUD_EXTENSION_PERFIL,
            metadata__solicitud_extension_id=solicitud.pk,
        )
        .count()
    )
    return {
        "sent_count": 0,
        "recipient_count": recipient_count,
        "requested_hours": solicitud.horas_solicitadas,
        "solicitud": serialize_profile_extension_request(solicitud),
    }