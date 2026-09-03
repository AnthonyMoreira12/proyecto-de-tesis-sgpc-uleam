"""
Transiciones controladas del estado de una publicación.

FASE 3 — Flujo formal de revisión.

El campo ``estado`` no se trata como un atributo CRUD ordinario.
Las transiciones se ejecutan como casos de uso del dominio, dentro
de transacciones y bloqueando la fila con ``select_for_update()``.

Transiciones habilitadas:

    borrador -> en_revision
    en_revision -> observada
    en_revision -> aprobada
    en_revision -> rechazada
    observada -> en_revision

Toda decisión administrativa de revisión queda registrada mediante
``PublicacionRevision``. Observar y rechazar exigen comentario.
"""

from django.db import transaction
from django.utils import timezone

from core.models import (
    Publicacion,
    PublicacionRevision,
)
from core.notificaciones.services.notificaciones_services import (
    notificar_decision_revision,
    notificar_envio_revision,
    notificar_reenvio_revision,
)
from core.publicaciones.services.publicaciones_historial_services import (
    registrar_evento_publicacion,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    is_admin_user,
)


class PublicacionEstadoServiceError(Exception):
    def __init__(
        self,
        detail,
        *,
        status_code=400,
        code="estado_invalido",
    ):
        super().__init__(
            str(detail)
        )
        self.detail = detail
        self.status_code = int(
            status_code
        )
        self.code = str(
            code
            or "estado_invalido"
        )


def _normalize_comment(
    value,
):
    return (
        str(
            value
            or ""
        ).strip()
        or None
    )


def _assert_authenticated_active_user(
    actor,
):
    if (
        actor is None
        or not getattr(
            actor,
            "is_authenticated",
            False,
        )
        or not getattr(
            actor,
            "is_active",
            True,
        )
    ):
        raise PublicacionEstadoServiceError(
            "Debe autenticarse con una cuenta activa.",
            status_code=401,
            code="no_autenticado",
        )


def _assert_admin(
    actor,
    *,
    action_label,
):
    _assert_authenticated_active_user(
        actor
    )

    if not is_admin_user(
        actor
    ):
        raise PublicacionEstadoServiceError(
            (
                "Solo un administrador puede "
                f"{action_label} una publicación."
            ),
            status_code=403,
            code="sin_permisos",
        )


def _get_locked_publicacion(
    publicacion_id,
):
    try:
        publicacion_id = int(
            publicacion_id
        )

    except (
        TypeError,
        ValueError,
    ):
        raise PublicacionEstadoServiceError(
            {
                "publicacion_id": [
                    "Debe ser un número entero válido."
                ]
            },
            status_code=400,
            code="id_invalido",
        )

    if publicacion_id < 1:
        raise PublicacionEstadoServiceError(
            {
                "publicacion_id": [
                    "Debe ser mayor o igual a 1."
                ]
            },
            status_code=400,
            code="id_invalido",
        )

    try:
        return (
            Publicacion.objects
            .select_for_update(
                of=("self",)
            )
            .select_related(
                "tipo",
                "usuario_creador",
                "sede",
                "carrera",
                "carrera__facultad",
            )
            .get(
                pk=publicacion_id
            )
        )

    except Publicacion.DoesNotExist:
        raise PublicacionEstadoServiceError(
            "Publicación no encontrada.",
            status_code=404,
            code="no_encontrada",
        )


def _transition_state(
    *,
    publicacion,
    expected_state,
    new_state,
):
    current_state = str(
        publicacion.estado
        or ""
    ).strip().lower()

    if current_state != expected_state:
        raise PublicacionEstadoServiceError(
            {
                "estado": [
                    (
                        "La transición solicitada no es válida. "
                        f"Estado actual: "
                        f"{publicacion.get_estado_display()}."
                    )
                ],
                "estado_actual": current_state,
                "estado_requerido": expected_state,
            },
            status_code=409,
            code="transicion_invalida",
        )

    now = timezone.now()

    updated = (
        Publicacion.objects
        .filter(
            pk=publicacion.pk,
            estado=expected_state,
        )
        .update(
            estado=new_state,
            updated_at=now,
        )
    )

    if updated != 1:
        raise PublicacionEstadoServiceError(
            (
                "La publicación cambió de estado durante la "
                "operación. Actualice la información e "
                "inténtelo nuevamente."
            ),
            status_code=409,
            code="conflicto_concurrencia",
        )

    previous_state = current_state
    publicacion.estado = new_state
    publicacion.updated_at = now

    return (
        previous_state,
        publicacion,
    )


def _register_review(
    *,
    publicacion,
    reviewer,
    decision,
    previous_state,
    resulting_state,
    comment=None,
):
    revision = PublicacionRevision(
        publicacion=publicacion,
        revisor=reviewer,
        decision=decision,
        comentario=_normalize_comment(
            comment
        ),
        estado_anterior=previous_state,
        estado_resultante=resulting_state,
    )

    try:
        revision.save()

    except Exception as exc:
        # La transacción externa revierte también el cambio de estado.
        raise PublicacionEstadoServiceError(
            {
                "revision": [
                    "No fue posible registrar la decisión "
                    "de revisión."
                ],
                "detail": str(exc),
            },
            status_code=400,
            code="revision_invalida",
        ) from exc

    return revision


def can_enviar_a_revision(
    actor,
    publicacion,
):
    if (
        actor is None
        or not getattr(
            actor,
            "is_authenticated",
            False,
        )
        or not getattr(
            actor,
            "is_active",
            True,
        )
        or publicacion is None
    ):
        return False

    if (
        str(
            getattr(
                publicacion,
                "estado",
                "",
            )
            or ""
        ).strip().lower()
        != Publicacion.ESTADO_BORRADOR
    ):
        return False

    if is_admin_user(
        actor
    ):
        return True

    return (
        getattr(
            publicacion,
            "usuario_creador_id",
            None,
        )
        == getattr(
            actor,
            "pk",
            None,
        )
    )


def can_reenviar_a_revision(
    actor,
    publicacion,
):
    """
    Una publicación observada puede reenviarse a revisión por:

    - su usuario creador;
    - un administrador.

    Los autores bibliográficos vinculados no adquieren este permiso
    únicamente por figurar en PublicacionAutor.
    """

    if (
        actor is None
        or not getattr(
            actor,
            "is_authenticated",
            False,
        )
        or not getattr(
            actor,
            "is_active",
            True,
        )
        or publicacion is None
    ):
        return False

    if (
        str(
            getattr(
                publicacion,
                "estado",
                "",
            )
            or ""
        ).strip().lower()
        != Publicacion.ESTADO_OBSERVADA
    ):
        return False

    if is_admin_user(
        actor
    ):
        return True

    return (
        getattr(
            publicacion,
            "usuario_creador_id",
            None,
        )
        == getattr(
            actor,
            "pk",
            None,
        )
    )


def can_revisar_publicacion(
    actor,
    publicacion,
):
    if (
        not is_admin_user(
            actor
        )
        or publicacion is None
    ):
        return False

    return (
        str(
            getattr(
                publicacion,
                "estado",
                "",
            )
            or ""
        ).strip().lower()
        == Publicacion.ESTADO_EN_REVISION
    )


def enviar_a_revision(
    *,
    publicacion_id,
    actor,
):
    _assert_authenticated_active_user(
        actor
    )

    with transaction.atomic():
        publicacion = (
            _get_locked_publicacion(
                publicacion_id
            )
        )

        if not can_enviar_a_revision(
            actor,
            publicacion,
        ):
            if (
                publicacion.estado
                != Publicacion.ESTADO_BORRADOR
            ):
                raise PublicacionEstadoServiceError(
                    {
                        "estado": [
                            (
                                "Solo una publicación en estado "
                                "Borrador puede enviarse a revisión."
                            )
                        ],
                        "estado_actual": (
                            publicacion.estado
                        ),
                    },
                    status_code=409,
                    code="transicion_invalida",
                )

            raise PublicacionEstadoServiceError(
                (
                    "No tiene permisos para enviar esta "
                    "publicación a revisión."
                ),
                status_code=403,
                code="sin_permisos",
            )

        previous_state, publicacion = (
            _transition_state(
                publicacion=publicacion,
                expected_state=(
                    Publicacion.ESTADO_BORRADOR
                ),
                new_state=(
                    Publicacion.ESTADO_EN_REVISION
                ),
            )
        )

        registrar_evento_publicacion(
            publicacion=publicacion,
            actor=actor,
            evento="enviada_revision",
            estado_anterior=previous_state,
            estado_resultante=(
                publicacion.estado
            ),
        )

        notificar_envio_revision(
            publicacion=publicacion,
        )

    return {
        "publicacion": publicacion,
        "estado_anterior": previous_state,
        "estado_nuevo": publicacion.estado,
        "accion": "enviar_revision",
        "revision": None,
    }


def reenviar_a_revision(
    *,
    publicacion_id,
    actor,
):
    """
    Reenvía una publicación observada después de que el autor
    haya tenido oportunidad de corregir su contenido.

    Transición:
        observada -> en_revision

    No crea una nueva PublicacionRevision porque el reenvío no es
    una decisión del revisor. La auditoría general de esta acción se
    incorporará en la fase de historial/auditoría.
    """

    _assert_authenticated_active_user(
        actor
    )

    with transaction.atomic():
        publicacion = (
            _get_locked_publicacion(
                publicacion_id
            )
        )

        if not can_reenviar_a_revision(
            actor,
            publicacion,
        ):
            if (
                publicacion.estado
                != Publicacion.ESTADO_OBSERVADA
            ):
                raise PublicacionEstadoServiceError(
                    {
                        "estado": [
                            (
                                "Solo una publicación en estado "
                                "Observada puede reenviarse a revisión."
                            )
                        ],
                        "estado_actual": (
                            publicacion.estado
                        ),
                    },
                    status_code=409,
                    code="transicion_invalida",
                )

            raise PublicacionEstadoServiceError(
                (
                    "No tiene permisos para reenviar esta "
                    "publicación a revisión."
                ),
                status_code=403,
                code="sin_permisos",
            )

        # Defensa de integridad:
        # una publicación Observada debe provenir de una decisión
        # formal registrada en PublicacionRevision.
        ultima_observacion = (
            PublicacionRevision.objects
            .select_related(
                "revisor"
            )
            .filter(
                publicacion=publicacion,
                decision=(
                    PublicacionRevision
                    .DECISION_OBSERVADA
                ),
                estado_resultante=(
                    Publicacion
                    .ESTADO_OBSERVADA
                ),
            )
            .order_by(
                "-created_at",
                "-id",
            )
            .first()
        )

        if ultima_observacion is None:
            raise PublicacionEstadoServiceError(
                {
                    "revision": [
                        (
                            "La publicación figura como Observada, "
                            "pero no posee una observación formal "
                            "registrada. Debe revisarse la integridad "
                            "del registro antes de reenviarlo."
                        )
                    ]
                },
                status_code=409,
                code="observacion_no_registrada",
            )

        previous_state, publicacion = (
            _transition_state(
                publicacion=publicacion,
                expected_state=(
                    Publicacion.ESTADO_OBSERVADA
                ),
                new_state=(
                    Publicacion.ESTADO_EN_REVISION
                ),
            )
        )

        registrar_evento_publicacion(
            publicacion=publicacion,
            actor=actor,
            evento="reenviada_revision",
            estado_anterior=previous_state,
            estado_resultante=(
                publicacion.estado
            ),
            detalle={
                "revision_observacion_id": (
                    ultima_observacion.id
                ),
            },
        )

        notificar_reenvio_revision(
            publicacion=publicacion,
            revision_observacion_id=(
                ultima_observacion.id
            ),
        )

    return {
        "publicacion": publicacion,
        "estado_anterior": previous_state,
        "estado_nuevo": publicacion.estado,
        "accion": "reenviar_revision",
        "revision": None,
        "revision_referencia": (
            ultima_observacion
        ),
    }


def _resolver_revision_administrativa(
    *,
    publicacion_id,
    actor,
    decision,
    resulting_state,
    action_name,
    action_label,
    comment=None,
    comment_required=False,
):
    _assert_admin(
        actor,
        action_label=action_label,
    )

    normalized_comment = (
        _normalize_comment(
            comment
        )
    )

    if (
        comment_required
        and not normalized_comment
    ):
        raise PublicacionEstadoServiceError(
            {
                "comentario": [
                    (
                        "Debe registrar un comentario o motivo "
                        f"para {action_label} la publicación."
                    )
                ]
            },
            status_code=400,
            code="comentario_obligatorio",
        )

    with transaction.atomic():
        publicacion = (
            _get_locked_publicacion(
                publicacion_id
            )
        )

        if not can_revisar_publicacion(
            actor,
            publicacion,
        ):
            raise PublicacionEstadoServiceError(
                {
                    "estado": [
                        (
                            "Solo una publicación en estado "
                            "En revisión puede recibir esta decisión."
                        )
                    ],
                    "estado_actual": (
                        publicacion.estado
                    ),
                },
                status_code=409,
                code="transicion_invalida",
            )

        previous_state, publicacion = (
            _transition_state(
                publicacion=publicacion,
                expected_state=(
                    Publicacion.ESTADO_EN_REVISION
                ),
                new_state=(
                    resulting_state
                ),
            )
        )

        revision = (
            _register_review(
                publicacion=publicacion,
                reviewer=actor,
                decision=decision,
                previous_state=previous_state,
                resulting_state=(
                    publicacion.estado
                ),
                comment=normalized_comment,
            )
        )

        event_by_action = {
            "aprobar": "aprobada",
            "observar": "observada",
            "rechazar": "rechazada",
        }

        registrar_evento_publicacion(
            publicacion=publicacion,
            actor=actor,
            evento=event_by_action[
                action_name
            ],
            estado_anterior=previous_state,
            estado_resultante=(
                publicacion.estado
            ),
            comentario=normalized_comment,
            detalle={
                "revision_id": (
                    revision.id
                ),
            },
        )

        notificar_decision_revision(
            publicacion=publicacion,
            decision=(
                publicacion.estado
            ),
            revision_id=(
                revision.id
            ),
        )

    return {
        "publicacion": publicacion,
        "estado_anterior": previous_state,
        "estado_nuevo": publicacion.estado,
        "accion": action_name,
        "revision": revision,
    }


def aprobar(
    *,
    publicacion_id,
    actor,
    comentario=None,
):
    return _resolver_revision_administrativa(
        publicacion_id=publicacion_id,
        actor=actor,
        decision=(
            PublicacionRevision.DECISION_APROBADA
        ),
        resulting_state=(
            Publicacion.ESTADO_APROBADA
        ),
        action_name="aprobar",
        action_label="aprobar",
        comment=comentario,
        comment_required=False,
    )


def observar(
    *,
    publicacion_id,
    actor,
    comentario,
):
    return _resolver_revision_administrativa(
        publicacion_id=publicacion_id,
        actor=actor,
        decision=(
            PublicacionRevision.DECISION_OBSERVADA
        ),
        resulting_state=(
            Publicacion.ESTADO_OBSERVADA
        ),
        action_name="observar",
        action_label="observar",
        comment=comentario,
        comment_required=True,
    )


def rechazar(
    *,
    publicacion_id,
    actor,
    comentario,
):
    return _resolver_revision_administrativa(
        publicacion_id=publicacion_id,
        actor=actor,
        decision=(
            PublicacionRevision.DECISION_RECHAZADA
        ),
        resulting_state=(
            Publicacion.ESTADO_RECHAZADA
        ),
        action_name="rechazar",
        action_label="rechazar",
        comment=comentario,
        comment_required=True,
    )


def _review_payload(
    revision,
):
    if revision is None:
        return None

    reviewer = (
        revision.revisor
    )

    reviewer_name = (
        getattr(
            reviewer,
            "get_full_name",
            lambda: "",
        )()
        or getattr(
            reviewer,
            "email",
            "",
        )
    )

    return {
        "id": revision.pk,
        "decision": (
            revision.decision
        ),
        "decision_label": (
            revision.get_decision_display()
        ),
        "comentario": (
            revision.comentario
        ),
        "estado_anterior": (
            revision.estado_anterior
        ),
        "estado_resultante": (
            revision.estado_resultante
        ),
        "revisor_id": (
            revision.revisor_id
        ),
        "revisor": (
            reviewer_name
        ),
        "created_at": (
            revision.created_at
        ),
    }


def build_transition_payload(
    result,
    *,
    message,
):
    publicacion = result[
        "publicacion"
    ]

    return {
        "ok": True,
        "message": message,
        "accion": result[
            "accion"
        ],
        "publicacion_id": (
            publicacion.pk
        ),
        "estado_anterior": result[
            "estado_anterior"
        ],
        "estado": (
            publicacion.estado
        ),
        "estado_label": (
            publicacion.get_estado_display()
        ),
        "revision": (
            _review_payload(
                result.get(
                    "revision"
                )
            )
        ),
        "revision_referencia": (
            _review_payload(
                result.get(
                    "revision_referencia"
                )
            )
        ),
        "updated_at": (
            publicacion.updated_at
        ),
    }