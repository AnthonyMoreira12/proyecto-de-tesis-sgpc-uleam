"""
Servicio de sincronización entre Usuario y Autor.

Garantiza que cada usuario con rol académico compatible tenga
un único registro Autor asociado.

La sincronización:

- Bloquea exclusivamente la fila del usuario.
- Reutiliza autores existentes sin usuario.
- Detecta conflictos de identificación y correo.
- Evita asociaciones con usuarios diferentes.
- Sincroniza nombres, apellidos, correo e identificación.
- Mantiene correctamente el estado de autor externo.
- Evita joins nullable durante SELECT ... FOR UPDATE.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.models import Autor


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

SYNCABLE_ROLES = {
    "autor",
    "autor_externo",
}

LOCAL_AUTH_SOURCE = "local"
EXTERNAL_AUTHOR_ROLE = "autor_externo"


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    return str(value or "").strip()


def _normalize_optional_text(value):
    normalized = _normalize_text(value)
    return normalized or None


def _normalize_email(value):
    normalized = _normalize_optional_text(value)

    if normalized is None:
        return None

    return normalized.lower()


def _get_locked_user(user):
    """
    Bloquea únicamente la fila de Usuario.

    No se cargan carrera ni facultad mediante select_related()
    porque carrera es nullable y PostgreSQL no permite aplicar
    FOR UPDATE sobre el lado nullable de un OUTER JOIN.
    """
    if user is None:
        return None

    user_id = getattr(user, "pk", None)

    if not user_id:
        return None

    try:
        return (
            User.objects
            .select_for_update()
            .get(pk=user_id)
        )

    except User.DoesNotExist:
        return None


def _is_syncable_user(user):
    if user is None:
        return False

    role = _normalize_text(
        getattr(user, "rol", "")
    ).lower()

    return role in SYNCABLE_ROLES


def _is_external_author(user):
    if user is None:
        return False

    role = _normalize_text(
        getattr(user, "rol", "")
    ).lower()

    auth_source = _normalize_text(
        getattr(user, "auth_source", "")
    ).lower()

    return bool(
        role == EXTERNAL_AUTHOR_ROLE
        and auth_source == LOCAL_AUTH_SOURCE
    )


def _author_data_from_user(user):
    return {
        "nombres": _normalize_text(
            getattr(user, "nombres", "")
        ),

        "apellidos": _normalize_text(
            getattr(user, "apellidos", "")
        ),

        "correo": _normalize_email(
            getattr(user, "email", None)
        ),

        "identificacion": _normalize_optional_text(
            getattr(user, "identificacion", None)
        ),

        "es_externo": _is_external_author(user),
    }


# ============================================================
# RESOLUCIÓN DE AUTOR EXISTENTE
# ============================================================

def _get_author_by_identification(
    *,
    identification,
):
    if not identification:
        return None

    return (
        Autor.objects
        .select_for_update()
        .filter(
            identificacion__iexact=identification
        )
        .first()
    )


def _get_author_by_email(
    *,
    email,
):
    if not email:
        return None

    return (
        Autor.objects
        .select_for_update()
        .filter(
            correo__iexact=email
        )
        .first()
    )


def _resolve_unlinked_author(
    *,
    user,
    identification,
    email,
):
    author_by_identification = (
        _get_author_by_identification(
            identification=identification,
        )
    )

    author_by_email = (
        _get_author_by_email(
            email=email,
        )
    )

    if (
        author_by_identification is not None
        and author_by_email is not None
        and author_by_identification.pk
        != author_by_email.pk
    ):
        raise ValidationError(
            {
                "autor": (
                    "La identificación y el correo del usuario "
                    "pertenecen a dos autores diferentes. "
                    "Revise los registros antes de continuar."
                )
            }
        )

    author = (
        author_by_identification
        or author_by_email
    )

    if author is None:
        return None

    linked_user_id = getattr(
        author,
        "usuario_id",
        None,
    )

    if linked_user_id not in (
        None,
        user.pk,
    ):
        raise ValidationError(
            {
                "autor": (
                    "El autor encontrado ya está vinculado "
                    "a otro usuario."
                )
            }
        )

    return author


# ============================================================
# CREACIÓN
# ============================================================

def _create_author(
    *,
    user,
    author_data,
):
    try:
        with transaction.atomic():
            return Autor.objects.create(
                usuario=user,
                nombres=author_data["nombres"],
                apellidos=author_data["apellidos"],
                correo=author_data["correo"],
                identificacion=(
                    author_data["identificacion"]
                ),
                es_externo=(
                    author_data["es_externo"]
                ),
            )

    except IntegrityError:
        concurrent_author = (
            _resolve_unlinked_author(
                user=user,
                identification=(
                    author_data["identificacion"]
                ),
                email=author_data["correo"],
            )
        )

        if concurrent_author is None:
            raise ValidationError(
                {
                    "autor": (
                        "No se pudo crear el autor debido "
                        "a un conflicto de integridad."
                    )
                }
            )

        return concurrent_author


# ============================================================
# ACTUALIZACIÓN
# ============================================================

def _sync_author_fields(
    *,
    author,
    user,
    author_data,
):
    changed_fields = []

    field_values = {
        "nombres": author_data["nombres"],
        "apellidos": author_data["apellidos"],
        "correo": author_data["correo"],
        "identificacion": (
            author_data["identificacion"]
        ),
        "es_externo": author_data["es_externo"],
    }

    if author.usuario_id != user.pk:
        author.usuario = user
        changed_fields.append("usuario")

    for field_name, new_value in field_values.items():
        current_value = getattr(
            author,
            field_name,
            None,
        )

        if current_value != new_value:
            setattr(
                author,
                field_name,
                new_value,
            )

            changed_fields.append(
                field_name
            )

    if changed_fields:
        author.save(
            update_fields=list(
                dict.fromkeys(
                    changed_fields
                )
            )
        )

    return author


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

def asegurar_autor_para_usuario(user):
    """
    Garantiza que un Usuario con rol académico tenga un único
    Autor asociado y sincronizado.
    """
    if user is None:
        return None

    if not getattr(user, "pk", None):
        return None

    with transaction.atomic():
        locked_user = _get_locked_user(
            user
        )

        if locked_user is None:
            return None

        if not _is_syncable_user(
            locked_user
        ):
            return None

        author_data = (
            _author_data_from_user(
                locked_user
            )
        )

        # Bloquea solamente la fila Autor.
        # usuario_id ya está disponible sin JOIN.
        author = (
            Autor.objects
            .select_for_update()
            .filter(
                usuario_id=locked_user.pk
            )
            .first()
        )

        if author is None:
            author = (
                _resolve_unlinked_author(
                    user=locked_user,
                    identification=(
                        author_data[
                            "identificacion"
                        ]
                    ),
                    email=(
                        author_data[
                            "correo"
                        ]
                    ),
                )
            )

        if author is None:
            author = _create_author(
                user=locked_user,
                author_data=author_data,
            )

        return _sync_author_fields(
            author=author,
            user=locked_user,
            author_data=author_data,
        )