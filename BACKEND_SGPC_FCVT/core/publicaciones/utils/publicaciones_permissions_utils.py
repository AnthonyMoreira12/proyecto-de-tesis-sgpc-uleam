"""
Utilidades de permisos de publicaciones.

Reglas del ciclo de gestión:

- Administrador:
  puede modificar cualquier publicación en cualquier estado.

- Usuario creador:
  puede modificar únicamente publicaciones en Borrador u Observada.

- En revisión, Aprobada y Rechazada:
  quedan bloqueadas para el usuario creador, pero no para el
  administrador.

Los autores bibliográficos vinculados mediante PublicacionAutor no
adquieren permiso de edición únicamente por figurar como autores.
El permiso ordinario de edición corresponde al usuario creador; los
administradores conservan capacidad de edición durante todo el ciclo.
"""

from core.models import Publicacion


PUBLICACION_EDITABLE_STATES = frozenset(
    {
        Publicacion.ESTADO_BORRADOR,
        Publicacion.ESTADO_OBSERVADA,
    }
)

PUBLICACION_DELETABLE_STATES = frozenset(
    {
        Publicacion.ESTADO_BORRADOR,
    }
)


def is_admin_user(
    user,
) -> bool:
    """
    Determina si el usuario autenticado tiene privilegios
    administrativos dentro del sistema.

    En Usuario los roles funcionales son:

        autor
        autor_externo

    Por tanto, el carácter administrativo se determina mediante
    is_staff / is_superuser.
    """

    if (
        not user
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        return False

    if not getattr(
        user,
        "is_active",
        True,
    ):
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


def resolve_user_autor_id(
    user,
):
    """
    Obtiene el Autor asociado al Usuario.

    Relación actual del modelo:

        Autor.usuario
            OneToOneField
            related_name="autor"

    Esta utilidad se conserva porque otras partes del proyecto
    la utilizan para resolver la relación Usuario -> Autor.
    No se utiliza para conceder permisos de edición de publicaciones.
    """

    if (
        not user
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        return None

    direct_id = getattr(
        user,
        "autor_id",
        None,
    )

    if direct_id:
        return direct_id

    legacy_id = getattr(
        user,
        "author_id",
        None,
    )

    if legacy_id:
        return legacy_id

    try:
        autor = getattr(
            user,
            "autor",
            None,
        )

    except Exception:
        autor = None

    if autor is None:
        return None

    return getattr(
        autor,
        "id",
        None,
    )


def get_publicacion_state(
    publicacion,
):
    """
    Devuelve el estado normalizado de la publicación.

    Un valor vacío o desconocido no se interpreta como editable.
    """

    if publicacion is None:
        return ""

    return str(
        getattr(
            publicacion,
            "estado",
            "",
        )
        or ""
    ).strip().lower()


def is_publicacion_content_editable(
    publicacion,
) -> bool:
    """
    Indica si el estado actual admite modificaciones de contenido.
    """

    return (
        get_publicacion_state(
            publicacion
        )
        in PUBLICACION_EDITABLE_STATES
    )


def get_publicacion_edit_block_reason(
    publicacion,
):
    """
    Devuelve el motivo institucional por el cual el contenido está
    bloqueado. Retorna None cuando el estado sí permite edición.
    """

    state = get_publicacion_state(
        publicacion
    )

    if state in PUBLICACION_EDITABLE_STATES:
        return None

    messages = {
        Publicacion.ESTADO_EN_REVISION: (
            "La publicación se encuentra en revisión y no puede "
            "modificarse mientras el proceso de revisión esté activo."
        ),
        Publicacion.ESTADO_APROBADA: (
            "La publicación está aprobada y no admite edición directa."
        ),
        Publicacion.ESTADO_RECHAZADA: (
            "La publicación está rechazada y no admite edición directa."
        ),
    }

    return messages.get(
        state,
        (
            "El estado actual de la publicación no permite "
            "modificar su contenido."
        ),
    )


def can_edit_publicacion(
    user,
    publicacion,
) -> bool:
    """
    Determina si un usuario puede modificar el contenido.

    Reglas:

    1. Un administrador autenticado y activo puede editar la
       publicación en cualquier estado.
    2. El usuario creador solo puede editarla cuando se encuentre
       en Borrador u Observada.

    Los cambios de estado no se realizan mediante esta función; se
    mantienen como acciones controladas del flujo de revisión.
    """

    if (
        not user
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
        or not getattr(
            user,
            "is_active",
            True,
        )
        or publicacion is None
    ):
        return False

    # El administrador conserva capacidad de edición durante todo
    # el ciclo de revisión, independientemente del estado actual.
    if is_admin_user(
        user
    ):
        return True

    # Para el usuario creador sí se aplica el bloqueo por estado.
    if not is_publicacion_content_editable(
        publicacion
    ):
        return False

    user_id = getattr(
        user,
        "pk",
        None,
    )

    if user_id is None:
        return False

    return (
        getattr(
            publicacion,
            "usuario_creador_id",
            None,
        )
        == user_id
    )


def can_delete_publicacion(
    user,
    publicacion,
) -> bool:
    """
    La eliminación directa se limita a administradores y únicamente
    mientras la publicación siga siendo Borrador.

    Una vez que una publicación entra al flujo de revisión no debe
    eliminarse mediante CRUD ordinario, porque su trazabilidad deberá
    conservarse.
    """

    if (
        not is_admin_user(
            user
        )
        or publicacion is None
    ):
        return False

    return (
        get_publicacion_state(
            publicacion
        )
        in PUBLICACION_DELETABLE_STATES
    )


def get_publicacion_delete_block_reason(
    publicacion,
):
    """
    Devuelve un mensaje adecuado cuando una publicación ya no puede
    eliminarse mediante CRUD ordinario.
    """

    state = get_publicacion_state(
        publicacion
    )

    if state in PUBLICACION_DELETABLE_STATES:
        return None

    return (
        "Solo las publicaciones en estado Borrador pueden eliminarse "
        "directamente. Los registros que ya ingresaron al flujo de "
        "revisión deben conservarse para mantener su trazabilidad."
    )