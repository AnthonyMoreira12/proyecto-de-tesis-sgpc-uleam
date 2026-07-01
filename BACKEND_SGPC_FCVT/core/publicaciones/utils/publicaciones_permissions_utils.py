"""
Utilidades de permisos para lectura y edición de publicaciones.
"""

from core.models import PublicacionAutor


def _normalize_role(value):
    return str(value or "").strip().lower()


def is_admin_user(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False

    rol = _normalize_role(getattr(user, "rol", None))

    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
        or getattr(user, "es_admin", False)
        or rol in {"admin", "administrador"}
    )


def resolve_user_autor_id(user):
    if not user or not getattr(user, "is_authenticated", False):
        return None

    direct_id = getattr(user, "autor_id", None)
    if direct_id:
        return direct_id

    author_id = getattr(user, "author_id", None)
    if author_id:
        return author_id

    try:
        autor_rel = getattr(user, "autor", None)
    except Exception:
        autor_rel = None

    if autor_rel is not None:
        rel_id = getattr(autor_rel, "id", None)
        if rel_id:
            return rel_id

    return None


def can_edit_publicacion(user, publicacion) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False

    if is_admin_user(user):
        return True

    autor_id = resolve_user_autor_id(user)
    if not autor_id:
        return False

    return PublicacionAutor.objects.filter(
        publicacion=publicacion,
        autor_id=autor_id,
    ).exists()