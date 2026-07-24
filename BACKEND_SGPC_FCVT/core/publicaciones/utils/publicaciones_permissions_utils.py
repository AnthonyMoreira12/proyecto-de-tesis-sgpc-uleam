"""
Utilidades de permisos de publicaciones.

Reglas de edición:

1. Administradores:
   pueden gestionar cualquier publicación.

2. Usuario creador:
   puede gestionar la publicación que creó.

3. Autor vinculado:
   puede gestionar una publicación en la que
   aparece mediante PublicacionAutor.
"""

from core.models import PublicacionAutor


def is_admin_user(
    user,
) -> bool:
    """
    En Usuario los roles funcionales son:

        autor
        autor_externo

    Por tanto, el carácter administrativo se determina
    mediante is_staff / is_superuser.
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

    Por compatibilidad se conservan las comprobaciones
    de autor_id / author_id si alguna capa anterior
    las proporciona.
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

    user_id = getattr(
        user,
        "pk",
        None,
    )

    # ---------------------------------------------------------
    # Usuario creador
    # ---------------------------------------------------------

    if (
        user_id is not None
        and getattr(
            publicacion,
            "usuario_creador_id",
            None,
        )
        == user_id
    ):
        return True

    # ---------------------------------------------------------
    # Autor asociado
    # ---------------------------------------------------------

    autor_id = (
        resolve_user_autor_id(
            user
        )
    )

    if not autor_id:
        return False

    # ---------------------------------------------------------
    # Aprovechar prefetch si está disponible
    # ---------------------------------------------------------

    participaciones_ordenadas = getattr(
        publicacion,
        "participaciones_ordenadas",
        None,
    )

    if (
        participaciones_ordenadas
        is not None
    ):
        return any(
            getattr(
                participacion,
                "autor_id",
                None,
            )
            == autor_id
            for participacion
            in participaciones_ordenadas
        )

    prefetched = getattr(
        publicacion,
        "_prefetched_objects_cache",
        {},
    )

    if "participaciones" in prefetched:
        return any(
            getattr(
                participacion,
                "autor_id",
                None,
            )
            == autor_id
            for participacion
            in prefetched[
                "participaciones"
            ]
        )

    # ---------------------------------------------------------
    # Consulta de respaldo
    # ---------------------------------------------------------

    return (
        PublicacionAutor.objects
        .filter(
            publicacion_id=(
                publicacion.pk
            ),
            autor_id=autor_id,
        )
        .exists()
    )