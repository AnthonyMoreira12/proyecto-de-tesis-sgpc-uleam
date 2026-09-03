"""
Servicio central de auditoría de publicaciones.

Toda capa que produzca una acción relevante debe registrar el evento
mediante ``registrar_evento_publicacion``. El modelo conserva además
una copia del nombre y correo del actor para no perder el dato
histórico si posteriormente la cuenta se elimina.
"""

from core.models import (
    Publicacion,
    PublicacionHistorial,
)


def _text(value):
    return str(
        value
        or ""
    ).strip()


def _actor_snapshot(
    actor,
):
    if actor is None:
        return (
            None,
            None,
        )

    name = ""

    try:
        name = _text(
            actor.get_full_name()
        )
    except Exception:
        name = ""

    if not name:
        name = _text(
            (
                f"{getattr(actor, 'nombres', '')} "
                f"{getattr(actor, 'apellidos', '')}"
            )
        )

    email = _text(
        getattr(
            actor,
            "email",
            None,
        )
    )

    return (
        name or None,
        email or None,
    )


def registrar_evento_publicacion(
    *,
    publicacion,
    evento,
    actor=None,
    estado_anterior=None,
    estado_resultante=None,
    comentario=None,
    detalle=None,
):
    """
    Registra un evento de auditoría.

    Se ejecuta de forma síncrona para que, cuando la llamada se
    encuentre dentro de ``transaction.atomic()``, cualquier fallo
    de auditoría revierta también la operación principal.
    """

    if publicacion is None:
        raise ValueError(
            "La publicación es obligatoria para registrar auditoría."
        )

    actor_name, actor_email = (
        _actor_snapshot(
            actor
        )
    )

    event_detail = (
        detalle
        if isinstance(
            detalle,
            dict,
        )
        else {}
    )

    history = PublicacionHistorial(
        publicacion=publicacion,
        actor=(
            actor
            if (
                actor is not None
                and getattr(
                    actor,
                    "pk",
                    None,
                )
            )
            else None
        ),
        actor_nombre=actor_name,
        actor_email=actor_email,
        evento=evento,
        estado_anterior=(
            _text(
                estado_anterior
            )
            or None
        ),
        estado_resultante=(
            _text(
                estado_resultante
            )
            or None
        ),
        comentario=(
            _text(
                comentario
            )
            or None
        ),
        detalle=event_detail,
    )

    history.save()

    return history


def registrar_creacion_publicacion(
    *,
    publicacion,
    actor,
):
    return registrar_evento_publicacion(
        publicacion=publicacion,
        actor=actor,
        evento=(
            PublicacionHistorial
            .EVENTO_CREADA
        ),
        estado_resultante=(
            publicacion.estado
        ),
        detalle={
            "tipo_id": (
                publicacion.tipo_id
            ),
            "sede_id": (
                publicacion.sede_id
            ),
            "carrera_id": (
                publicacion.carrera_id
            ),
            "proyecto_id": (
                publicacion.proyecto_id
            ),
            "registrado_por_admin": bool(
                publicacion.registrado_por_admin
            ),
        },
    )


def registrar_edicion_publicacion(
    *,
    publicacion,
    actor,
    campos_modificados=None,
    origen="api",
):
    fields = sorted(
        {
            _text(
                field
            )
            for field
            in (
                campos_modificados
                or []
            )
            if _text(
                field
            )
        }
    )

    return registrar_evento_publicacion(
        publicacion=publicacion,
        actor=actor,
        evento=(
            PublicacionHistorial
            .EVENTO_EDITADA
        ),
        estado_anterior=(
            publicacion.estado
        ),
        estado_resultante=(
            publicacion.estado
        ),
        detalle={
            "campos_modificados": fields,
            "origen": _text(
                origen
            )
            or "api",
        },
    )


def serializar_evento_historial(
    history,
):
    return {
        "id": history.pk,
        "publicacion_id": (
            history.publicacion_id
        ),
        "evento": (
            history.evento
        ),
        "evento_label": (
            history.get_evento_display()
        ),
        "actor_id": (
            history.actor_id
        ),
        "actor_nombre": (
            history.actor_nombre
        ),
        "actor_email": (
            history.actor_email
        ),
        "estado_anterior": (
            history.estado_anterior
        ),
        "estado_resultante": (
            history.estado_resultante
        ),
        "comentario": (
            history.comentario
        ),
        "detalle": (
            history.detalle
            or {}
        ),
        "created_at": (
            history.created_at
        ),
    }


def listar_historial_publicacion(
    *,
    publicacion_id,
):
    queryset = (
        PublicacionHistorial.objects
        .select_related(
            "actor"
        )
        .filter(
            publicacion_id=publicacion_id
        )
        .order_by(
            "-created_at",
            "-id",
        )
    )

    return [
        serializar_evento_historial(
            item
        )
        for item in queryset
    ]