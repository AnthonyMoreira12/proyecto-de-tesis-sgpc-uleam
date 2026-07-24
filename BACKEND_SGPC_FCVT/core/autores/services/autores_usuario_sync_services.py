"""
Servicios para búsqueda, vinculación y sincronización entre
los modelos Autor y Usuario.

Responsabilidades:

- Buscar autores existentes por identificación, correo o nombre.
- Serializar coincidencias para formularios y selectores.
- Reutilizar el servicio oficial de sincronización Usuario → Autor.
- Crear usuarios externos pendientes desde autores manuales.
- Evitar conflictos entre correos, identificaciones y vínculos.
- Proteger las operaciones concurrentes mediante transacciones.

La sincronización principal Usuario → Autor se encuentra en:

    core.auth.services.auth_author_sync_services
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from django.db.models import Q

from rest_framework import status

from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario as asegurar_autor_auth,
)
from core.models import Autor


User = get_user_model()


# ============================================================
# CONSTANTES
# ============================================================

AUTH_SOURCE_LOCAL = User.AuthSource.LOCAL
AUTH_SOURCE_MICROSOFT = User.AuthSource.MICROSOFT

ROLE_EXTERNAL_AUTHOR = User.Rol.AUTOR_EXTERNO


# ============================================================
# EXCEPCIÓN
# ============================================================

class AutorUsuarioSyncError(Exception):
    """
    Error controlado durante la vinculación entre Autor
    y Usuario.
    """

    def __init__(
        self,
        detail,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        self.detail = detail
        self.status_code = status_code

        super().__init__(
            str(detail)
        )


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _normalize_text(value):
    """
    Normaliza un texto obligatorio o general.
    """
    return " ".join(
        str(value or "").split()
    )


def _normalize_optional_text(value):
    """
    Normaliza un texto opcional.
    """
    normalized = _normalize_text(
        value
    )

    return normalized or None


def _normalize_email(value):
    """
    Normaliza un correo mediante el manager del modelo Usuario.
    """
    normalized = _normalize_optional_text(
        value
    )

    if normalized is None:
        return None

    return (
        User.objects
        .normalize_email(normalized)
        .strip()
        .lower()
    )


def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    adecuada para Django REST Framework.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": str(exc),
    }


# ============================================================
# BÚSQUEDA DE AUTORES
# ============================================================

def buscar_autor_existente(
    *,
    identificacion=None,
    correo=None,
    nombres="",
    apellidos="",
    exclude_autor_id=None,
):
    """
    Busca un autor existente utilizando el siguiente orden:

    1. Identificación.
    2. Correo.
    3. Nombres y apellidos.

    La búsqueda también considera los datos del Usuario
    relacionado, porque el correo o la identificación podrían
    estar almacenados en el perfil del usuario vinculado.

    Retorna:

    {
        "exists": True,
        "match_type": "identificacion",
        "autor": Autor(...)
    }
    """
    normalized_identification = (
        _normalize_optional_text(
            identificacion
        )
    )

    normalized_email = _normalize_email(
        correo
    )

    normalized_names = _normalize_text(
        nombres
    )

    normalized_surnames = _normalize_text(
        apellidos
    )

    queryset = (
        Autor.objects
        .select_related("usuario")
        .order_by("pk")
    )

    if exclude_autor_id:
        queryset = queryset.exclude(
            pk=exclude_autor_id
        )

    # ========================================================
    # IDENTIFICACIÓN
    # ========================================================

    if normalized_identification:
        author = (
            queryset
            .filter(
                Q(
                    identificacion=(
                        normalized_identification
                    )
                )
                | Q(
                    usuario__identificacion=(
                        normalized_identification
                    )
                )
            )
            .first()
        )

        if author is not None:
            return {
                "exists": True,
                "match_type": "identificacion",
                "autor": author,
            }

    # ========================================================
    # CORREO
    # ========================================================

    if normalized_email:
        author = (
            queryset
            .filter(
                Q(
                    correo__iexact=(
                        normalized_email
                    )
                )
                | Q(
                    usuario__email__iexact=(
                        normalized_email
                    )
                )
            )
            .first()
        )

        if author is not None:
            return {
                "exists": True,
                "match_type": "correo",
                "autor": author,
            }

    # ========================================================
    # NOMBRES Y APELLIDOS
    # ========================================================

    if (
        normalized_names
        and normalized_surnames
    ):
        author = (
            queryset
            .filter(
                nombres__iexact=(
                    normalized_names
                ),
                apellidos__iexact=(
                    normalized_surnames
                ),
            )
            .first()
        )

        if author is not None:
            return {
                "exists": True,
                "match_type": "nombre_apellido",
                "autor": author,
            }

    return {
        "exists": False,
        "match_type": None,
        "autor": None,
    }


# ============================================================
# SERIALIZACIÓN DE COINCIDENCIAS
# ============================================================

def serializar_autor_match(
    autor,
    match_type=None,
):
    """
    Convierte una coincidencia de Autor en una estructura
    segura para el frontend.
    """
    if autor is None:
        return {
            "exists": False,
            "match_type": match_type,
            "autor": None,
        }

    user = getattr(
        autor,
        "usuario",
        None,
    )

    resolved_email = None

    if user is not None:
        resolved_email = _normalize_email(
            getattr(
                user,
                "email",
                None,
            )
        )

    if resolved_email is None:
        resolved_email = _normalize_email(
            getattr(
                autor,
                "correo",
                None,
            )
        )

    full_name = " ".join(
        part
        for part in [
            _normalize_text(
                getattr(
                    autor,
                    "nombres",
                    "",
                )
            ),
            _normalize_text(
                getattr(
                    autor,
                    "apellidos",
                    "",
                )
            ),
        ]
        if part
    )

    return {
        "exists": True,
        "match_type": match_type,
        "autor": {
            "id": autor.pk,
            "nombre_completo": full_name,
            "nombres": autor.nombres,
            "apellidos": autor.apellidos,
            "identificacion": (
                autor.identificacion
            ),
            "correo_resuelto": (
                resolved_email
            ),
            "institucion": (
                autor.institucion
            ),
            "usuario_id": (
                autor.usuario_id
            ),
            "usuario_activo": bool(
                getattr(
                    user,
                    "is_active",
                    False,
                )
                if user is not None
                else False
            ),
            "es_externo": bool(
                autor.es_externo
            ),
        },
    }


# ============================================================
# SINCRONIZACIÓN USUARIO → AUTOR
# ============================================================

def asegurar_autor_para_usuario(user):
    """
    Mantiene esta función por compatibilidad con importaciones
    antiguas.

    La implementación real se encuentra centralizada en el
    módulo de autenticación para evitar dos comportamientos
    diferentes de sincronización.
    """
    return asegurar_autor_auth(
        user
    )


# ============================================================
# BÚSQUEDA DE USUARIOS COINCIDENTES
# ============================================================

def _find_matching_locked_user(
    *,
    author,
    identification,
    email,
):
    """
    Busca y bloquea usuarios que coincidan con la identificación,
    correo o vínculo actual del autor.

    Detecta cuando la identificación y el correo corresponden a
    usuarios diferentes.
    """
    query = Q()

    if identification:
        query |= Q(
            identificacion=identification
        )

    if email:
        query |= Q(
            email__iexact=email
        )

    if author.usuario_id:
        query |= Q(
            pk=author.usuario_id
        )

    if not query:
        return None

    candidates = list(
        User.objects
        .select_for_update()
        .filter(query)
        .order_by("pk")
    )

    user_by_identification = None
    user_by_email = None
    currently_linked_user = None

    for candidate in candidates:
        candidate_identification = (
            _normalize_optional_text(
                getattr(
                    candidate,
                    "identificacion",
                    None,
                )
            )
        )

        candidate_email = _normalize_email(
            getattr(
                candidate,
                "email",
                None,
            )
        )

        if (
            identification
            and candidate_identification
            == identification
        ):
            if (
                user_by_identification is not None
                and user_by_identification.pk
                != candidate.pk
            ):
                raise AutorUsuarioSyncError(
                    {
                        "identificacion": (
                            "Existen varios usuarios con "
                            "esta identificación."
                        )
                    },
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                )

            user_by_identification = candidate

        if (
            email
            and candidate_email == email
        ):
            if (
                user_by_email is not None
                and user_by_email.pk
                != candidate.pk
            ):
                raise AutorUsuarioSyncError(
                    {
                        "correo": (
                            "Existen varios usuarios con "
                            "este correo."
                        )
                    },
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                )

            user_by_email = candidate

        if (
            author.usuario_id
            and candidate.pk
            == author.usuario_id
        ):
            currently_linked_user = candidate

    matched_users = {
        candidate.pk: candidate
        for candidate in [
            user_by_identification,
            user_by_email,
            currently_linked_user,
        ]
        if candidate is not None
    }

    if len(matched_users) > 1:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "La identificación, el correo y el "
                    "usuario vinculado corresponden a "
                    "cuentas diferentes. Revise los datos."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    if not matched_users:
        return None

    return next(
        iter(
            matched_users.values()
        )
    )


# ============================================================
# VALIDACIÓN DEL USUARIO ENCONTRADO
# ============================================================

def _validate_existing_user(
    *,
    user,
    author,
    identification,
    email,
):
    """
    Verifica que el usuario pueda vincularse al autor externo.
    """
    auth_source = _normalize_text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()

    role = _normalize_text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()

    if auth_source == AUTH_SOURCE_MICROSOFT:
        raise AutorUsuarioSyncError(
            {
                "correo": (
                    "Ya existe un usuario institucional "
                    "con este correo o identificación. "
                    "No puede registrarse como autor "
                    "externo pendiente."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    if role != ROLE_EXTERNAL_AUTHOR:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "Ya existe un usuario con esos datos, "
                    "pero no corresponde al rol de autor "
                    "externo."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    linked_author = (
        Autor.objects
        .select_for_update()
        .filter(
            usuario_id=user.pk
        )
        .exclude(
            pk=author.pk
        )
        .first()
    )

    if linked_author is not None:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "El usuario encontrado ya está "
                    "vinculado a otro autor."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    user_identification = (
        _normalize_optional_text(
            getattr(
                user,
                "identificacion",
                None,
            )
        )
    )

    user_email = _normalize_email(
        getattr(
            user,
            "email",
            None,
        )
    )

    is_pending_user = bool(
        not user.is_active
        and getattr(
            user,
            "creado_desde_selector",
            False,
        )
    )

    # Un usuario activo no debe ser modificado silenciosamente
    # desde el formulario de creación de autores.
    if user.is_active:
        if (
            user_identification
            and user_identification
            != identification
        ):
            raise AutorUsuarioSyncError(
                {
                    "identificacion": (
                        "La identificación no coincide con "
                        "el usuario externo existente."
                    )
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        if (
            user_email
            and user_email != email
        ):
            raise AutorUsuarioSyncError(
                {
                    "correo": (
                        "El correo no coincide con el "
                        "usuario externo existente."
                    )
                },
                status_code=status.HTTP_409_CONFLICT,
            )

    elif not is_pending_user:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "Existe una cuenta externa inactiva "
                    "con estos datos, pero no fue creada "
                    "como usuario pendiente desde el "
                    "selector."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return is_pending_user


# ============================================================
# ACTUALIZACIÓN DEL USUARIO PENDIENTE
# ============================================================

def _update_pending_user(
    *,
    user,
    email,
    identification,
    names,
    surnames,
):
    """
    Actualiza únicamente usuarios pendientes creados desde el
    selector.

    No modifica automáticamente los datos de usuarios activos.
    """
    changed_fields = []

    if user.email != email:
        user.email = email
        changed_fields.append(
            "email"
        )

    if (
        _normalize_optional_text(
            user.identificacion
        )
        != identification
    ):
        user.identificacion = identification
        changed_fields.append(
            "identificacion"
        )

    if user.nombres != names:
        user.nombres = names
        changed_fields.append(
            "nombres"
        )

    if user.apellidos != surnames:
        user.apellidos = surnames
        changed_fields.append(
            "apellidos"
        )

    if user.rol != ROLE_EXTERNAL_AUTHOR:
        user.rol = ROLE_EXTERNAL_AUTHOR
        changed_fields.append(
            "rol"
        )

    if user.auth_source != AUTH_SOURCE_LOCAL:
        user.auth_source = AUTH_SOURCE_LOCAL
        changed_fields.append(
            "auth_source"
        )

    if user.is_active:
        user.is_active = False
        changed_fields.append(
            "is_active"
        )

    if not getattr(
        user,
        "creado_desde_selector",
        False,
    ):
        user.creado_desde_selector = True
        changed_fields.append(
            "creado_desde_selector"
        )

    if user.has_usable_password():
        user.set_unusable_password()
        changed_fields.append(
            "password"
        )

    if changed_fields:
        user.save(
            update_fields=list(
                dict.fromkeys(
                    changed_fields
                )
            )
        )

    return user


# ============================================================
# ACTUALIZACIÓN DEL AUTOR
# ============================================================

def _link_author_to_user(
    *,
    author,
    user,
    email,
    identification,
    names,
    surnames,
):
    """
    Vincula el autor al usuario y mantiene los campos básicos
    coherentes.
    """
    changed_fields = []

    if author.usuario_id != user.pk:
        author.usuario = user
        changed_fields.append(
            "usuario"
        )

    if author.identificacion != identification:
        author.identificacion = identification
        changed_fields.append(
            "identificacion"
        )

    if author.correo != email:
        author.correo = email
        changed_fields.append(
            "correo"
        )

    if author.nombres != names:
        author.nombres = names
        changed_fields.append(
            "nombres"
        )

    if author.apellidos != surnames:
        author.apellidos = surnames
        changed_fields.append(
            "apellidos"
        )

    if not author.es_externo:
        author.es_externo = True
        changed_fields.append(
            "es_externo"
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
# SERVICIO PRINCIPAL AUTOR → USUARIO PENDIENTE
# ============================================================

def asegurar_usuario_pendiente_para_autor(
    autor,
):
    """
    Garantiza que un autor externo tenga un usuario local
    pendiente asociado.

    Cuando no existe usuario:

    - Crea una cuenta local inactiva.
    - Asigna rol autor_externo.
    - Establece contraseña inutilizable.
    - Marca creado_desde_selector=True.

    Cuando ya existe:

    - Rechaza cuentas Microsoft.
    - Rechaza roles diferentes.
    - Rechaza vínculos con otro autor.
    - Solo actualiza automáticamente cuentas pendientes.
    - No modifica silenciosamente cuentas activas.
    """
    if autor is None or not getattr(
        autor,
        "pk",
        None,
    ):
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "El autor debe estar guardado antes "
                    "de crear su usuario pendiente."
                )
            }
        )

    try:
        with transaction.atomic():
            locked_author = (
                Autor.objects
                .select_for_update()
                .select_related("usuario")
                .get(
                    pk=autor.pk
                )
            )

            identification = (
                _normalize_optional_text(
                    locked_author.identificacion
                )
            )

            email = _normalize_email(
                locked_author.correo
            )

            names = (
                _normalize_text(
                    locked_author.nombres
                )
                or "Autor"
            )

            surnames = _normalize_text(
                locked_author.apellidos
            )

            if not identification:
                raise AutorUsuarioSyncError(
                    {
                        "identificacion": (
                            "Para registrar el usuario "
                            "pendiente, la identificación "
                            "es obligatoria."
                        )
                    }
                )

            if not email:
                raise AutorUsuarioSyncError(
                    {
                        "correo": (
                            "Para registrar el usuario "
                            "pendiente, el correo es "
                            "obligatorio."
                        )
                    }
                )

            user = _find_matching_locked_user(
                author=locked_author,
                identification=identification,
                email=email,
            )

            if user is None:
                user = User.objects.create_user(
                    email=email,
                    nombres=names,
                    apellidos=surnames,
                    password=None,
                    identificacion=identification,
                    rol=ROLE_EXTERNAL_AUTHOR,
                    auth_source=AUTH_SOURCE_LOCAL,
                    is_active=False,
                    is_staff=False,
                    is_superuser=False,
                    perfil_completo=False,
                    creado_desde_selector=True,
                )

            else:
                is_pending_user = (
                    _validate_existing_user(
                        user=user,
                        author=locked_author,
                        identification=identification,
                        email=email,
                    )
                )

                if is_pending_user:
                    user = _update_pending_user(
                        user=user,
                        email=email,
                        identification=identification,
                        names=names,
                        surnames=surnames,
                    )

                else:
                    # El usuario activo conserva sus datos como
                    # fuente principal.
                    names = (
                        _normalize_text(
                            user.nombres
                        )
                        or names
                    )

                    surnames = (
                        _normalize_text(
                            user.apellidos
                        )
                        or surnames
                    )

                    identification = (
                        _normalize_optional_text(
                            user.identificacion
                        )
                        or identification
                    )

                    email = (
                        _normalize_email(
                            user.email
                        )
                        or email
                    )

            _link_author_to_user(
                author=locked_author,
                user=user,
                email=email,
                identification=identification,
                names=names,
                surnames=surnames,
            )

            return user

    except AutorUsuarioSyncError:
        raise

    except Autor.DoesNotExist as exc:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "El autor ya no existe en la "
                    "base de datos."
                )
            },
            status_code=status.HTTP_404_NOT_FOUND,
        ) from exc

    except DjangoValidationError as exc:
        raise AutorUsuarioSyncError(
            _django_validation_payload(
                exc
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from exc

    except IntegrityError as exc:
        raise AutorUsuarioSyncError(
            {
                "detail": (
                    "No fue posible vincular el autor y "
                    "el usuario porque existe un conflicto "
                    "con el correo, identificación o vínculo."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        ) from exc