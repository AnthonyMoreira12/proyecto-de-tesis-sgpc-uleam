"""
Política central de visibilidad de publicaciones.

Reglas oficiales:

PUBLICACIÓN APROBADA
    - visible en superficies generales;
    - visible para cualquier usuario autenticado;
    - puede formar parte de búsqueda pública y Scholar.

PUBLICACIÓN NO APROBADA
    - visible para administradores;
    - visible para su usuario creador;
    - visible para autores bibliográficos vinculados;
    - no visible para terceros.

La capacidad de LEER una publicación no concede capacidad de EDITARLA.
Las reglas de edición siguen viviendo en publicaciones_permissions_utils.
"""

from django.db.models import Q

from core.models import Publicacion
from core.publicaciones.utils.publicaciones_permissions_utils import (
    is_admin_user,
    resolve_user_autor_id,
)


def is_publicacion_publica(
    publicacion,
) -> bool:
    """
    Una publicación se considera pública únicamente cuando
    ha finalizado el flujo administrativo como Aprobada.
    """

    if publicacion is None:
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
        == Publicacion.ESTADO_APROBADA
    )


def build_publicacion_visibility_q(
    user,
    *,
    prefix="",
):
    """
    Construye un Q reutilizable para limitar publicaciones visibles.

    ``prefix`` permite reutilizar la regla desde modelos relacionados.

    Ejemplos:
        Publicacion:
            prefix=""

        PublicacionArchivo:
            prefix="publicacion__"
    """

    state_field = f"{prefix}estado"
    creator_field = f"{prefix}usuario_creador_id"
    linked_user_field = f"{prefix}participaciones__autor__usuario_id"
    linked_author_field = f"{prefix}participaciones__autor_id"

    visibility = Q(
        **{
            state_field: Publicacion.ESTADO_APROBADA,
        }
    )

    if (
        not user
        or not getattr(user, "is_authenticated", False)
        or not getattr(user, "is_active", True)
    ):
        return visibility

    if is_admin_user(user):
        return Q()

    user_id = getattr(user, "pk", None)

    if user_id is not None:
        visibility |= Q(
            **{
                creator_field: user_id,
            }
        )
        visibility |= Q(
            **{
                linked_user_field: user_id,
            }
        )

    autor_id = resolve_user_autor_id(user)

    if autor_id:
        visibility |= Q(
            **{
                linked_author_field: autor_id,
            }
        )

    return visibility


def apply_public_publicaciones_scope(
    queryset,
):
    """
    Aplica el alcance oficial de una superficie pública/general.
    """

    return queryset.filter(
        estado=Publicacion.ESTADO_APROBADA
    )


def apply_user_visible_publicaciones_scope(
    queryset,
    *,
    user,
    prefix="",
):
    """
    Aplica la política de lectura para un usuario autenticado.

    Administrador:
        todo.

    Usuario normal:
        aprobadas
        + creadas por él
        + publicaciones donde figura como Autor.
    """

    if is_admin_user(user):
        return queryset

    return (
        queryset
        .filter(
            build_publicacion_visibility_q(
                user,
                prefix=prefix,
            )
        )
        .distinct()
    )


def can_view_publicacion(
    user,
    publicacion,
) -> bool:
    """
    Evaluación puntual de la misma política de visibilidad.
    """

    if publicacion is None:
        return False

    if is_publicacion_publica(publicacion):
        return True

    if (
        not user
        or not getattr(user, "is_authenticated", False)
        or not getattr(user, "is_active", True)
    ):
        return False

    if is_admin_user(user):
        return True

    user_id = getattr(user, "pk", None)

    if (
        user_id is not None
        and getattr(publicacion, "usuario_creador_id", None) == user_id
    ):
        return True

    autor_id = resolve_user_autor_id(user)

    if not autor_id:
        return False

    prefetched = getattr(
        publicacion,
        "participaciones_ordenadas",
        None,
    )

    if prefetched is not None:
        return any(
            getattr(relation, "autor_id", None) == autor_id
            for relation in prefetched
        )

    return (
        publicacion.participaciones
        .filter(autor_id=autor_id)
        .exists()
    )