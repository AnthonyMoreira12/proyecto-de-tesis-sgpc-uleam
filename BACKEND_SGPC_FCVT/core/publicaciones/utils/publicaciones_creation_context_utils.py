"""
Utilidades para resolver el contexto de creación
de una publicación.

Distingue correctamente entre:

1. Registro realizado directamente por un autor.
2. Registro realizado por un administrador.
3. Registro administrativo realizado en nombre de otro usuario.

El modelo Publicacion conserva:

- usuario_creador:
    autor al que corresponde el registro.

- registrado_por_admin:
    indica si hubo intervención administrativa.

- admin_registrador:
    administrador responsable del registro.
"""

from rest_framework.exceptions import ValidationError


def _is_authenticated(user):
    return bool(
        user
        and getattr(
            user,
            "is_authenticated",
            False,
        )
    )


def _is_active(user):
    return bool(
        user
        and getattr(
            user,
            "is_active",
            False,
        )
    )


def _is_admin(user):
    if not _is_authenticated(user):
        return False

    return bool(
        getattr(
            user,
            "is_staff",
            False,
        )
        or getattr(
            user,
            "is_superuser",
            False,
        )
    )


def _normalize_role(user):
    return str(
        getattr(
            user,
            "rol",
            "",
        )
        or ""
    ).strip().lower()


def _validate_usuario_creador(
    usuario,
):
    if not _is_authenticated(
        usuario
    ):
        raise ValidationError(
            {
                "usuario_creador": [
                    "No se pudo resolver un "
                    "usuario creador válido."
                ]
            }
        )

    if not _is_active(
        usuario
    ):
        raise ValidationError(
            {
                "usuario_creador": [
                    "El usuario creador está inactivo."
                ]
            }
        )

    rol = _normalize_role(
        usuario
    )

    if rol not in {
        "autor",
        "autor_externo",
    }:
        raise ValidationError(
            {
                "usuario_creador": [
                    "El usuario creador debe ser "
                    "un autor válido."
                ]
            }
        )

    return usuario


def _validate_admin(
    admin,
):
    if not _is_authenticated(
        admin
    ):
        raise ValidationError(
            {
                "admin_registrador": [
                    "No se pudo resolver "
                    "el administrador registrador."
                ]
            }
        )

    if not _is_active(
        admin
    ):
        raise ValidationError(
            {
                "admin_registrador": [
                    "El administrador registrador "
                    "está inactivo."
                ]
            }
        )

    if not _is_admin(
        admin
    ):
        raise ValidationError(
            {
                "admin_registrador": [
                    "El usuario registrador debe "
                    "tener privilegios administrativos."
                ]
            }
        )

    return admin


def resolve_publicacion_creation_context(
    serializer,
):
    """
    Devuelve:

        (
            usuario_creador,
            admin_registrador,
            registrado_por_admin,
        )

    Contextos admitidos
    -------------------

    Registro normal:

        context={
            "request": request,
        }

    Registro administrativo para otro usuario:

        context={
            "request": request,
            "usuario_creador_override": usuario,
            "registrado_por_admin": True,
        }

    También puede proporcionarse explícitamente:

        "admin_registrador": usuario_admin
    """

    context = (
        getattr(
            serializer,
            "context",
            None,
        )
        or {}
    )

    request = context.get(
        "request"
    )

    request_user = getattr(
        request,
        "user",
        None,
    )

    if not _is_authenticated(
        request_user
    ):
        raise ValidationError(
            {
                "detail": [
                    "Debe existir un usuario "
                    "autenticado para registrar "
                    "la publicación."
                ]
            }
        )

    if not _is_active(
        request_user
    ):
        raise ValidationError(
            {
                "detail": [
                    "El usuario autenticado "
                    "se encuentra inactivo."
                ]
            }
        )

    # ---------------------------------------------------------
    # Usuario propietario/creador de la publicación
    # ---------------------------------------------------------

    usuario_override = context.get(
        "usuario_creador_override"
    )

    usuario_creador = (
        usuario_override
        if usuario_override is not None
        else request_user
    )

    usuario_creador = (
        _validate_usuario_creador(
            usuario_creador
        )
    )

    # ---------------------------------------------------------
    # Estado administrativo
    # ---------------------------------------------------------

    registrado_por_admin = bool(
        context.get(
            "registrado_por_admin",
            False,
        )
    )

    admin_registrador = context.get(
        "admin_registrador"
    )

    # Un admin explícito implica automáticamente
    # registro administrativo.
    if admin_registrador is not None:
        registrado_por_admin = True

    # Si el usuario autenticado registra para otro
    # usuario, necesariamente es una acción administrativa.
    if (
        getattr(
            usuario_creador,
            "pk",
            None,
        )
        != getattr(
            request_user,
            "pk",
            None,
        )
    ):
        if not _is_admin(
            request_user
        ):
            raise ValidationError(
                {
                    "usuario_creador": [
                        "Solo un administrador puede "
                        "registrar publicaciones en "
                        "nombre de otro usuario."
                    ]
                }
            )

        registrado_por_admin = True

        if admin_registrador is None:
            admin_registrador = (
                request_user
            )

    # ---------------------------------------------------------
    # Registro administrativo explícito
    # ---------------------------------------------------------

    if registrado_por_admin:
        if admin_registrador is None:
            admin_registrador = (
                request_user
            )

        admin_registrador = (
            _validate_admin(
                admin_registrador
            )
        )

    else:
        # Una publicación normal no debe conservar
        # accidentalmente un administrador.
        admin_registrador = None

    return (
        usuario_creador,
        admin_registrador,
        registrado_por_admin,
    )