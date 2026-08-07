"""
Servicios de búsqueda y sincronización entre Autor y Usuario.

El Autor se crea primero como registro científico. En la misma
transacción se crea o reutiliza una cuenta local pendiente y se
vincula mediante Autor.usuario. Las participaciones siempre
permanecen asociadas al mismo Autor, incluso cuando el Usuario
recibe acceso posteriormente.
"""

import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework import status

from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario as asegurar_autor_auth,
)
from core.models import Autor


User = get_user_model()

AUTH_SOURCE_LOCAL = User.AuthSource.LOCAL
AUTH_SOURCE_MICROSOFT = User.AuthSource.MICROSOFT
ROLE_EXTERNAL_AUTHOR = User.Rol.AUTOR_EXTERNO
CEDULA_PATTERN = re.compile(r"^\d{10}$")
ORCID_PATTERN = re.compile(
    r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
)

try:
    AUTHOR_IDENTIFICATION_MAX_LENGTH = int(
        getattr(
            Autor._meta.get_field("identificacion"),
            "max_length",
            50,
        )
        or 50
    )
except Exception:
    AUTHOR_IDENTIFICATION_MAX_LENGTH = 50


class AutorUsuarioSyncError(Exception):
    """Error controlado durante la vinculación Autor ↔ Usuario."""

    def __init__(
        self,
        detail,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def _normalize_text(value):
    return " ".join(str(value or "").split())


def _normalize_optional_text(value):
    normalized = _normalize_text(value)
    return normalized or None


def _normalize_identification(value):
    normalized = str(value or "").strip()
    return normalized or None


def _normalize_email(value):
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None

    return (
        User.objects.normalize_email(normalized)
        .strip()
        .lower()
    )


def _normalize_orcid(value):
    normalized = _normalize_optional_text(value)

    return (
        normalized.upper()
        if normalized
        else None
    )


def _normalize_account_value(value):
    return str(value or "").strip().lower()


def _django_validation_payload(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"detail": list(exc.messages)}
    return {"detail": str(exc)}


def _unique_fields(fields):
    return list(dict.fromkeys(field for field in fields if field))


def _validate_external_identification(value):
    """
    Valida el documento del Autor externo.

    La Cédula/DNI es opcional. Si se informa, puede ser un
    documento extranjero y por ello no se restringe a diez
    dígitos.
    """
    normalized = _normalize_identification(value)

    if normalized is None:
        return None

    if len(normalized) > AUTHOR_IDENTIFICATION_MAX_LENGTH:
        raise AutorUsuarioSyncError(
            {
                "identificacion": (
                    "La Cédula / DNI no puede superar "
                    f"los {AUTHOR_IDENTIFICATION_MAX_LENGTH} caracteres."
                )
            }
        )

    return normalized


def _user_cedula_from_external_identification(value):
    """
    Usuario.identificacion conserva la regla de cédula ecuatoriana
    de 10 dígitos. Un DNI extranjero permanece únicamente en Autor.
    """
    normalized = _normalize_identification(value)

    if (
        normalized is not None
        and CEDULA_PATTERN.fullmatch(normalized)
    ):
        return normalized

    return None


def _has_usable_password(user):
    if user is None:
        return False
    try:
        return bool(user.has_usable_password())
    except (AttributeError, TypeError, ValueError):
        return False


def _is_external_local_user(user):
    if user is None:
        return False

    return bool(
        _normalize_account_value(getattr(user, "rol", ""))
        == _normalize_account_value(ROLE_EXTERNAL_AUTHOR)
        and _normalize_account_value(getattr(user, "auth_source", ""))
        == _normalize_account_value(AUTH_SOURCE_LOCAL)
    )


def _is_pending_external_user(user):
    """
    Pendiente significa que la cuenta aún no recibió acceso.
    Una cuenta desactivada que conserva contraseña es inactiva,
    no pendiente.
    """
    return bool(
        _is_external_local_user(user)
        and not getattr(user, "is_active", False)
        and not _has_usable_password(user)
    )


def _resolve_user_state(user):
    if user is None:
        return "sin_usuario"
    if _is_pending_external_user(user):
        return "pendiente"
    if bool(getattr(user, "is_active", False)):
        return "activo"
    return "inactivo"


def buscar_autor_existente(
    *,
    identificacion=None,
    correo=None,
    orcid=None,
    nombres="",
    apellidos="",
    exclude_autor_id=None,
):
    """
    Busca primero por ORCID, luego por Cédula/DNI, correo y finalmente
    por nombres y apellidos. La coincidencia por nombre es solo una
    advertencia; no debe bloquear por sí sola la creación.
    """
    identification = _normalize_identification(identificacion)
    email = _normalize_email(correo)
    academic_orcid = _normalize_orcid(orcid)
    names = _normalize_text(nombres)
    surnames = _normalize_text(apellidos)

    queryset = Autor.objects.select_related("usuario").order_by("pk")

    if exclude_autor_id:
        queryset = queryset.exclude(pk=exclude_autor_id)

    if academic_orcid:
        author = queryset.filter(
            orcid__iexact=academic_orcid
        ).first()
        if author is not None:
            return {
                "exists": True,
                "match_type": "orcid",
                "autor": author,
            }

    if identification:
        author = queryset.filter(
            Q(identificacion__iexact=identification)
            | Q(usuario__identificacion__iexact=identification)
        ).first()
        if author is not None:
            return {
                "exists": True,
                "match_type": "identificacion",
                "autor": author,
            }

    if email:
        author = queryset.filter(
            Q(correo__iexact=email)
            | Q(usuario__email__iexact=email)
        ).first()
        if author is not None:
            return {
                "exists": True,
                "match_type": "correo",
                "autor": author,
            }

    if names and surnames:
        author = queryset.filter(
            nombres__iexact=names,
            apellidos__iexact=surnames,
        ).first()
        if author is not None:
            return {
                "exists": True,
                "match_type": "nombre_apellido",
                "autor": author,
            }

    return {"exists": False, "match_type": None, "autor": None}


def serializar_autor_match(autor, match_type=None):
    if autor is None:
        return {
            "exists": False,
            "match_type": match_type,
            "blocking": False,
            "warning_only": False,
            "input_incomplete": False,
            "message": None,
            "autor": None,
        }

    user = getattr(autor, "usuario", None)
    resolved_email = (
        _normalize_email(getattr(user, "email", None))
        if user is not None
        else None
    ) or _normalize_email(getattr(autor, "correo", None))

    full_name = " ".join(
        part
        for part in [
            _normalize_text(getattr(autor, "nombres", "")),
            _normalize_text(getattr(autor, "apellidos", "")),
        ]
        if part
    )

    blocking = match_type in {
        "identificacion",
        "correo",
        "orcid",
    }
    warning_only = match_type == "nombre_apellido"

    messages = {
        "identificacion": (
            "Ya existe un autor registrado con esta Cédula / DNI."
        ),
        "correo": (
            "Ya existe un autor registrado con este correo electrónico."
        ),
        "orcid": (
            "Ya existe un autor registrado con este ORCID."
        ),
        "nombre_apellido": (
            "Existe un autor con los mismos nombres y apellidos. "
            "Revise la coincidencia antes de continuar."
        ),
    }

    return {
        "exists": True,
        "match_type": match_type,
        "blocking": blocking,
        "warning_only": warning_only,
        "input_incomplete": False,
        "message": messages.get(match_type),
        "autor": {
            "id": autor.pk,
            "nombre_completo": full_name,
            "nombres": autor.nombres,
            "apellidos": autor.apellidos,
            "identificacion": autor.identificacion,
            "correo": autor.correo,
            "correo_resuelto": resolved_email,
            "institucion": autor.institucion,
            "orcid": getattr(autor, "orcid", None),
            "registro_senescyt": getattr(
                autor,
                "registro_senescyt",
                None,
            ),
            "google_scholar": getattr(
                autor,
                "google_scholar",
                None,
            ),
            "scopus_id": getattr(
                autor,
                "scopus_id",
                None,
            ),
            "es_externo": bool(autor.es_externo),
            "usuario_id": autor.usuario_id,
            "usuario_activo": bool(
                getattr(user, "is_active", False)
                if user is not None
                else False
            ),
            "usuario_pendiente": _is_pending_external_user(user),
            "usuario_estado": _resolve_user_state(user),
            "usuario_tiene_password_utilizable": _has_usable_password(user),
            "usuario_creado_desde_selector": bool(
                getattr(user, "creado_desde_selector", False)
                if user is not None
                else False
            ),
        },
    }


def asegurar_autor_para_usuario(user):
    """Compatibilidad con importaciones antiguas."""
    return asegurar_autor_auth(user)


def _find_matching_locked_user(*, author, identification, email):
    query = Q()

    if identification:
        query |= Q(identificacion__iexact=identification)
    if email:
        query |= Q(email__iexact=email)
    if author.usuario_id:
        query |= Q(pk=author.usuario_id)

    if not query:
        return None

    candidates = list(
        User.objects.select_for_update().filter(query).order_by("pk")
    )

    by_identification = None
    by_email = None
    linked = None

    for candidate in candidates:
        candidate_identification = _normalize_identification(
            getattr(candidate, "identificacion", None)
        )
        candidate_email = _normalize_email(
            getattr(candidate, "email", None)
        )

        if identification and candidate_identification == identification:
            if (
                by_identification is not None
                and by_identification.pk != candidate.pk
            ):
                raise AutorUsuarioSyncError(
                    {
                        "identificacion": (
                            "Existen varios usuarios con este número "
                            "de cédula."
                        )
                    },
                    status_code=status.HTTP_409_CONFLICT,
                )
            by_identification = candidate

        if email and candidate_email == email:
            if by_email is not None and by_email.pk != candidate.pk:
                raise AutorUsuarioSyncError(
                    {
                        "correo": (
                            "Existen varios usuarios con este correo "
                            "electrónico."
                        )
                    },
                    status_code=status.HTTP_409_CONFLICT,
                )
            by_email = candidate

        if author.usuario_id and candidate.pk == author.usuario_id:
            linked = candidate

    matched = {
        candidate.pk: candidate
        for candidate in (by_identification, by_email, linked)
        if candidate is not None
    }

    if len(matched) > 1:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "La identificación, el correo y el Usuario vinculado "
                    "corresponden a cuentas diferentes."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return next(iter(matched.values()), None)


def _validate_existing_user(*, user, author, identification, email):
    auth_source = _normalize_account_value(
        getattr(user, "auth_source", "")
    )
    role = _normalize_account_value(getattr(user, "rol", ""))

    if auth_source == _normalize_account_value(AUTH_SOURCE_MICROSOFT):
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "Ya existe un usuario institucional con este "
                    "correo o identificación. No puede vincularse como autor "
                    "externo."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    if auth_source != _normalize_account_value(AUTH_SOURCE_LOCAL):
        raise AutorUsuarioSyncError(
            {"detail": "El usuario encontrado no utiliza autenticación local."},
            status_code=status.HTTP_409_CONFLICT,
        )

    if role != _normalize_account_value(ROLE_EXTERNAL_AUTHOR):
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "El usuario encontrado no corresponde al rol "
                    "de autor externo."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    other_author = (
        Autor.objects.select_for_update()
        .filter(usuario_id=user.pk)
        .exclude(pk=author.pk)
        .first()
    )
    if other_author is not None:
        raise AutorUsuarioSyncError(
            {"detail": "El usuario ya está vinculado a otro autor."},
            status_code=status.HTTP_409_CONFLICT,
        )

    user_identification = _normalize_identification(
        getattr(user, "identificacion", None)
    )
    user_email = _normalize_email(getattr(user, "email", None))

    if (
        identification
        and user_identification
        and user_identification != identification
    ):
        raise AutorUsuarioSyncError(
            {
                "identificacion": (
                    "La cédula ecuatoriana no coincide con el "
                    "usuario externo existente."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    if user_email and user_email != email:
        raise AutorUsuarioSyncError(
            {
                "correo": (
                    "El correo no coincide con el usuario externo existente."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return _resolve_user_state(user)


def _update_pending_user(
    *, user, email, identification, names, surnames
):
    """
    Actualiza solo una cuenta realmente pendiente. Nunca activa,
    desactiva, asigna o elimina contraseñas.
    """
    if not _is_pending_external_user(user):
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "La cuenta ya no está pendiente y no puede "
                    "modificarse mediante este flujo."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    changed = []

    if user.email != email:
        user.email = email
        changed.append("email")
    if (
        identification is not None
        and _normalize_identification(user.identificacion)
        != identification
    ):
        user.identificacion = identification
        changed.append("identificacion")
    if user.nombres != names:
        user.nombres = names
        changed.append("nombres")
    if user.apellidos != surnames:
        user.apellidos = surnames
        changed.append("apellidos")

    if changed:
        user.save(update_fields=_unique_fields(changed))

    return user


def _link_author_to_user(
    *, author, user, email, author_identification, names, surnames
):
    changed = []

    if author.usuario_id != user.pk:
        author.usuario = user
        changed.append("usuario")
    if author.identificacion != author_identification:
        author.identificacion = author_identification
        changed.append("identificacion")
    if author.correo != email:
        author.correo = email
        changed.append("correo")
    if author.nombres != names:
        author.nombres = names
        changed.append("nombres")
    if author.apellidos != surnames:
        author.apellidos = surnames
        changed.append("apellidos")
    if not author.es_externo:
        author.es_externo = True
        changed.append("es_externo")

    if changed:
        author.save(update_fields=_unique_fields(changed))

    return author


def _create_pending_user(*, email, identification, names, surnames):
    return User.objects.create_user(
        email=email,
        nombres=names,
        apellidos=surnames,
        password=None,
        identificacion=identification,
        rol=ROLE_EXTERNAL_AUTHOR,
        auth_source=AUTH_SOURCE_LOCAL,
        carrera=None,
        is_active=False,
        is_staff=False,
        is_superuser=False,
        perfil_completo=False,
        creado_desde_selector=True,
    )


def asegurar_usuario_pendiente_para_autor(autor):
    """
    Garantiza el vínculo permanente Autor ↔ Usuario.

    Se evita combinar select_for_update() con select_related()
    sobre Autor.usuario, porque la relación es nullable y
    PostgreSQL no permite bloquear el lado nullable de ese
    LEFT OUTER JOIN.
    """
    if autor is None or not getattr(autor, "pk", None):
        raise AutorUsuarioSyncError(
            {"detail": "El autor debe estar guardado antes de vincularlo."}
        )

    try:
        with transaction.atomic():
            locked_author = (
                Autor.objects.select_for_update().get(pk=autor.pk)
            )

            author_identification = (
                _validate_external_identification(
                    locked_author.identificacion
                )
            )
            user_identification = (
                _user_cedula_from_external_identification(
                    author_identification
                )
            )
            email = _normalize_email(locked_author.correo)
            names = _normalize_text(locked_author.nombres)
            surnames = _normalize_text(locked_author.apellidos)

            if not email:
                raise AutorUsuarioSyncError(
                    {"correo": "El correo electrónico es obligatorio."}
                )
            if not names:
                raise AutorUsuarioSyncError(
                    {"nombres": "Los nombres son obligatorios."}
                )
            if not surnames:
                raise AutorUsuarioSyncError(
                    {"apellidos": "Los apellidos son obligatorios."}
                )

            user = _find_matching_locked_user(
                author=locked_author,
                identification=user_identification,
                email=email,
            )

            if user is None:
                user = _create_pending_user(
                    email=email,
                    identification=user_identification,
                    names=names,
                    surnames=surnames,
                )
            else:
                state = _validate_existing_user(
                    user=user,
                    author=locked_author,
                    identification=user_identification,
                    email=email,
                )

                if state == "pendiente":
                    user = _update_pending_user(
                        user=user,
                        email=email,
                        identification=user_identification,
                        names=names,
                        surnames=surnames,
                    )
                else:
                    # Usuario activo o previamente activado: se
                    # conservan su estado y contraseña.
                    email = _normalize_email(user.email) or email
                    user_identification = (
                        _normalize_identification(
                            user.identificacion
                        )
                        or user_identification
                    )
                    names = _normalize_text(user.nombres) or names
                    surnames = _normalize_text(user.apellidos) or surnames

            _link_author_to_user(
                author=locked_author,
                user=user,
                email=email,
                author_identification=author_identification,
                names=names,
                surnames=surnames,
            )

            return user

    except AutorUsuarioSyncError:
        raise
    except Autor.DoesNotExist as exc:
        raise AutorUsuarioSyncError(
            {"detail": "El autor ya no existe."},
            status_code=status.HTTP_404_NOT_FOUND,
        ) from exc
    except DjangoValidationError as exc:
        raise AutorUsuarioSyncError(
            _django_validation_payload(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from exc
    except (IntegrityError, ValueError) as exc:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "No fue posible vincular el autor y el usuario "
                    "por un conflicto de identificación, correo o vínculo."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        ) from exc
