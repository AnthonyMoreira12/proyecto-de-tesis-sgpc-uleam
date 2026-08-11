"""
Utilidades de permisos de publicaciones.

Reglas de edición:

1. Administradores:
   pueden gestionar cualquier publicación.

2. Usuario creador:
   puede gestionar la publicación que creó.

Los autores vinculados mediante PublicacionAutor no adquieren
permiso de edición únicamente por figurar como autores. El permiso
se concede al usuario que registró la publicación y a los
administradores.
"""


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


def can_edit_publicacion(
    user,
    publicacion,
) -> bool:
    """
    Determina si un usuario puede modificar una publicación.

    Regla institucional:

    - un administrador puede editar cualquier publicación;
    - el usuario que creó la publicación puede editarla;
    - los demás usuarios no pueden editarla, aunque aparezcan
      como autores bibliográficos de la publicación.
    """

    if (
        not user
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
        or publicacion is None
    ):
        return False

    # ---------------------------------------------------------
    # Administrador
    # ---------------------------------------------------------

    if is_admin_user(
        user
    ):
        return True

    # ---------------------------------------------------------
    # Usuario creador de la publicación
    # ---------------------------------------------------------

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