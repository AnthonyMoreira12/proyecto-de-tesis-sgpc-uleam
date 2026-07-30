"""
Servicio de sincronización entre Usuario y Autor.

Garantiza que cada Usuario con un rol académico compatible tenga
un único registro Autor asociado.

La sincronización:

- Bloquea exclusivamente la fila del Usuario.
- No utiliza joins nullable durante SELECT ... FOR UPDATE.
- Reutiliza autores existentes que todavía no tienen Usuario.
- Detecta conflictos entre cédula y correo.
- Impide vincular un Autor perteneciente a otro Usuario.
- Sincroniza nombres, apellidos, correo e identificación.
- Mantiene correctamente el indicador es_externo.
- Controla conflictos de concurrencia e integridad.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q

from core.models import Autor


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_AUTHOR = "autor"
ROLE_EXTERNAL_AUTHOR = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _normalize_text(value):
    """
    Normaliza un texto obligatorio o vacío.
    """
    return str(value or "").strip()


def _normalize_optional_text(value):
    """
    Normaliza un texto opcional.

    Retorna None cuando el valor está vacío.
    """
    normalized = _normalize_text(value)

    return normalized or None


def _normalize_email(value):
    """
    Normaliza un correo electrónico opcional.
    """
    normalized = _normalize_optional_text(value)

    if normalized is None:
        return None

    return normalized.lower()


def _normalized_role(user):
    """
    Obtiene el rol normalizado del Usuario.
    """
    return _normalize_text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()


def _normalized_auth_source(user):
    """
    Obtiene el origen de autenticación normalizado.
    """
    return _normalize_text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()


# ============================================================
# CLASIFICACIÓN
# ============================================================

def _is_syncable_user(user):
    """
    Determina si el Usuario debe tener un registro Autor.

    Combinaciones admitidas:

    - autor + microsoft:
      Autor institucional.

    - autor_externo + local:
      Autor externo.

    - autor + local:
      Cuenta local de compatibilidad, utilizada principalmente
      por administradores creados directamente en el sistema.

    No se admite autor_externo + microsoft.
    """
    if user is None:
        return False

    role = _normalized_role(user)
    auth_source = _normalized_auth_source(user)

    if role == ROLE_EXTERNAL_AUTHOR:
        return auth_source == AUTH_SOURCE_LOCAL

    if role == ROLE_AUTHOR:
        return auth_source in {
            AUTH_SOURCE_LOCAL,
            AUTH_SOURCE_MICROSOFT,
        }

    return False


def _is_external_author(user):
    """
    Determina si el Autor debe marcarse como externo.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_EXTERNAL_AUTHOR
        and _normalized_auth_source(user)
        == AUTH_SOURCE_LOCAL
    )


# ============================================================
# DATOS DEL AUTOR
# ============================================================

def _author_data_from_user(user):
    """
    Construye los campos del Autor a partir del Usuario.
    """
    return {
        "nombres": _normalize_text(
            getattr(
                user,
                "nombres",
                "",
            )
        ),

        "apellidos": _normalize_text(
            getattr(
                user,
                "apellidos",
                "",
            )
        ),

        "correo": _normalize_email(
            getattr(
                user,
                "email",
                None,
            )
        ),

        "identificacion": _normalize_optional_text(
            getattr(
                user,
                "identificacion",
                None,
            )
        ),

        "es_externo": _is_external_author(
            user
        ),
    }


def _validate_author_data(author_data):
    """
    Comprueba que los datos mínimos requeridos por Autor estén
    disponibles antes de acceder a la base de datos.
    """
    errors = {}

    if not author_data.get("nombres"):
        errors["nombres"] = (
            "Los nombres del usuario son obligatorios "
            "para sincronizar el autor."
        )

    if not author_data.get("apellidos"):
        errors["apellidos"] = (
            "Los apellidos del usuario son obligatorios "
            "para sincronizar el autor."
        )

    if not (
        author_data.get("identificacion")
        or author_data.get("correo")
    ):
        errors["autor"] = (
            "El usuario debe tener una cédula o un correo "
            "para crear su registro de autor."
        )

    if errors:
        raise ValidationError(errors)


# ============================================================
# BLOQUEO DEL USUARIO
# ============================================================

def _get_locked_user(user):
    """
    Recupera y bloquea exclusivamente la fila del Usuario.

    No se utiliza select_related() con Carrera o Facultad porque
    Carrera es nullable. PostgreSQL no permite aplicar
    SELECT ... FOR UPDATE sobre el lado nullable de un OUTER JOIN.
    """
    if user is None:
        return None

    user_id = getattr(
        user,
        "pk",
        None,
    )

    if not user_id:
        return None

    try:
        return (
            User.objects
            .select_for_update()
            .get(
                pk=user_id
            )
        )

    except User.DoesNotExist:
        return None


# ============================================================
# BLOQUEO Y RESOLUCIÓN DE AUTORES
# ============================================================

def _lock_relevant_authors(
    *,
    user,
    identification,
    email,
):
    """
    Bloquea, en orden estable por clave primaria, todos los
    autores relevantes para la sincronización.

    Se consideran relevantes:

    - El Autor ya vinculado al Usuario.
    - El Autor que tenga la misma cédula.
    - El Autor que tenga el mismo correo.

    Bloquear todas las filas en un orden estable reduce el riesgo
    de interbloqueos durante operaciones concurrentes.
    """
    query = Q(
        usuario_id=user.pk
    )

    if identification:
        query |= Q(
            identificacion=identification
        )

    if email:
        query |= Q(
            correo__iexact=email
        )

    return list(
        Autor.objects
        .select_for_update()
        .filter(query)
        .order_by("pk")
    )


def _authors_matching_identification(
    authors,
    identification,
):
    """
    Obtiene los autores que coinciden exactamente con la cédula.
    """
    if not identification:
        return []

    return [
        author
        for author in authors
        if _normalize_optional_text(
            getattr(
                author,
                "identificacion",
                None,
            )
        )
        == identification
    ]


def _authors_matching_email(
    authors,
    email,
):
    """
    Obtiene los autores que coinciden con el correo normalizado.
    """
    if not email:
        return []

    return [
        author
        for author in authors
        if _normalize_email(
            getattr(
                author,
                "correo",
                None,
            )
        )
        == email
    ]


def _single_author_or_error(
    authors,
    *,
    field_name,
    message,
):
    """
    Exige que una identidad coincida con un solo Autor.
    """
    if len(authors) > 1:
        raise ValidationError(
            {
                field_name: message,
            }
        )

    return (
        authors[0]
        if authors
        else None
    )


def _resolve_author_for_user(
    *,
    user,
    identification,
    email,
):
    """
    Resuelve el Autor que debe vincularse al Usuario.

    Retorna:

    - El Autor ya vinculado al Usuario.
    - Un Autor sin Usuario que coincida por cédula o correo.
    - None cuando se debe crear un Autor nuevo.
    """
    relevant_authors = _lock_relevant_authors(
        user=user,
        identification=identification,
        email=email,
    )

    linked_authors = [
        author
        for author in relevant_authors
        if getattr(
            author,
            "usuario_id",
            None,
        )
        == user.pk
    ]

    linked_author = _single_author_or_error(
        linked_authors,
        field_name="autor",
        message=(
            "El usuario tiene más de un registro de autor "
            "vinculado. Revise la integridad de la base de datos."
        ),
    )

    identification_author = _single_author_or_error(
        _authors_matching_identification(
            relevant_authors,
            identification,
        ),
        field_name="identificacion",
        message=(
            "La cédula está asociada con más de un autor. "
            "Revise la integridad de la base de datos."
        ),
    )

    email_author = _single_author_or_error(
        _authors_matching_email(
            relevant_authors,
            email,
        ),
        field_name="email",
        message=(
            "El correo está asociado con más de un autor. "
            "Revise la integridad de la base de datos."
        ),
    )

    if (
        identification_author is not None
        and email_author is not None
        and identification_author.pk
        != email_author.pk
    ):
        raise ValidationError(
            {
                "autor": (
                    "La cédula y el correo del usuario "
                    "pertenecen a dos autores diferentes. "
                    "Revise los registros antes de continuar."
                )
            }
        )

    identity_author = (
        identification_author
        or email_author
    )

    # ========================================================
    # EL USUARIO YA TIENE AUTOR
    # ========================================================

    if linked_author is not None:
        if (
            identity_author is not None
            and identity_author.pk
            != linked_author.pk
        ):
            errors = {}

            if (
                identification_author is not None
                and identification_author.pk
                != linked_author.pk
            ):
                errors["identificacion"] = (
                    "La cédula ya pertenece a otro autor."
                )

            if (
                email_author is not None
                and email_author.pk
                != linked_author.pk
            ):
                errors["email"] = (
                    "El correo ya pertenece a otro autor."
                )

            if not errors:
                errors["autor"] = (
                    "Los datos del usuario entran en conflicto "
                    "con otro registro de autor."
                )

            raise ValidationError(errors)

        return linked_author

    # ========================================================
    # AUTOR ENCONTRADO POR IDENTIDAD
    # ========================================================

    if identity_author is not None:
        linked_user_id = getattr(
            identity_author,
            "usuario_id",
            None,
        )

        if linked_user_id not in {
            None,
            user.pk,
        }:
            raise ValidationError(
                {
                    "autor": (
                        "El autor que coincide con la cédula "
                        "o el correo ya está vinculado a otro "
                        "usuario."
                    )
                }
            )

        return identity_author

    return None


# ============================================================
# CREACIÓN
# ============================================================

def _create_author(
    *,
    user,
    author_data,
):
    """
    Crea un Autor nuevo.

    El bloque atomic interno crea un savepoint. Cuando otra
    operación concurrente crea primero el mismo Autor, el
    savepoint se revierte y se intenta resolver el registro
    existente.
    """
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

    except IntegrityError as exc:
        concurrent_author = (
            _resolve_author_for_user(
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
            ) from exc

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
    """
    Sincroniza únicamente los campos que realmente cambiaron.
    """
    changed_fields = []

    expected_values = {
        "nombres": author_data["nombres"],
        "apellidos": author_data["apellidos"],
        "correo": author_data["correo"],
        "identificacion": (
            author_data["identificacion"]
        ),
        "es_externo": (
            author_data["es_externo"]
        ),
    }

    if getattr(
        author,
        "usuario_id",
        None,
    ) != user.pk:
        author.usuario = user

        changed_fields.append(
            "usuario"
        )

    for field_name, expected_value in expected_values.items():
        current_value = getattr(
            author,
            field_name,
            None,
        )

        if field_name == "correo":
            current_value = _normalize_email(
                current_value
            )

        elif field_name == "identificacion":
            current_value = _normalize_optional_text(
                current_value
            )

        if current_value != expected_value:
            setattr(
                author,
                field_name,
                expected_value,
            )

            changed_fields.append(
                field_name
            )

    if not changed_fields:
        return author

    try:
        author.save(
            update_fields=list(
                dict.fromkeys(
                    changed_fields
                )
            )
        )

    except IntegrityError as exc:
        raise ValidationError(
            {
                "autor": (
                    "No se pudo sincronizar el autor porque "
                    "la cédula o el correo ya pertenecen "
                    "a otro registro."
                )
            }
        ) from exc

    return author


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

def asegurar_autor_para_usuario(user):
    """
    Garantiza que un Usuario compatible tenga un único Autor
    vinculado y sincronizado.

    Retorna:
        Autor:
            Registro creado, recuperado o actualizado.

        None:
            Cuando el Usuario no existe, no está guardado o su
            combinación de rol y autenticación no es compatible.
    """
    if user is None:
        return None

    if not getattr(
        user,
        "pk",
        None,
    ):
        return None

    with transaction.atomic():
        # ====================================================
        # BLOQUEO EXCLUSIVO DEL USUARIO
        # ====================================================

        locked_user = _get_locked_user(
            user
        )

        if locked_user is None:
            return None

        # ====================================================
        # CLASIFICACIÓN
        # ====================================================

        if not _is_syncable_user(
            locked_user
        ):
            return None

        # ====================================================
        # DATOS ESPERADOS
        # ====================================================

        author_data = _author_data_from_user(
            locked_user
        )

        _validate_author_data(
            author_data
        )

        # ====================================================
        # RESOLUCIÓN
        # ====================================================

        author = _resolve_author_for_user(
            user=locked_user,
            identification=(
                author_data["identificacion"]
            ),
            email=author_data["correo"],
        )

        # ====================================================
        # CREACIÓN
        # ====================================================

        if author is None:
            author = _create_author(
                user=locked_user,
                author_data=author_data,
            )

        # ====================================================
        # SINCRONIZACIÓN
        # ====================================================

        return _sync_author_fields(
            author=author,
            user=locked_user,
            author_data=author_data,
        )