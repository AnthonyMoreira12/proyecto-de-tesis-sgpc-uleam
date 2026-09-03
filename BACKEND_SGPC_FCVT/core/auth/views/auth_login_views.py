"""
View para el inicio de sesión mediante credenciales locales.

Responsabilidades:

- Validar las credenciales recibidas.
- Autenticar utilizando el USERNAME_FIELD del modelo.
- Impedir el acceso local de cuentas Microsoft.
- Verificar que la cuenta esté activa.
- Garantizar la existencia del registro Autor asociado.
- Generar tokens JWT.
- Construir una respuesta compatible con el frontend.
- No exponer información académica de cuentas externas.
"""

import logging
import re

from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError as DjangoValidationError,
)
from django.db import (
    DatabaseError,
    IntegrityError,
    transaction,
)
from django.utils import timezone

from rest_framework import (
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from core.auth.serializers.auth_login_serializers import (
    LoginSerializer,
)
from core.auditoria.services.auditoria_services import (
    registrar_evento_auditoria,
)
from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.auth.services.auth_profile_services import (
    get_profile_edit_status,
)
from core.auth.services.auth_token_cookie_services import (
    set_refresh_cookie,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# CONSTANTES
# ============================================================

ROLE_INSTITUTIONAL = "autor"
ROLE_EXTERNAL = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"

CEDULA_PATTERN = re.compile(r"^\d{10}$")

SYNCABLE_AUTHOR_ROLES = {
    ROLE_INSTITUTIONAL,
    ROLE_EXTERNAL,
}


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _normalize_email(value):
    """
    Normaliza un correo electrónico utilizando el manager del
    modelo de usuario.
    """
    return (
        User.objects.normalize_email(
            str(
                value or ""
            )
        )
        .strip()
        .lower()
    )


def _normalized_role(user):
    """
    Obtiene el rol normalizado del usuario.
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


def _is_external_user(user):
    """
    Una cuenta es externa únicamente cuando:

    - rol = autor_externo
    - auth_source = local
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_EXTERNAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_LOCAL
    )


def _is_institutional_user(user):
    """
    Una cuenta es institucional únicamente cuando:

    - rol = autor
    - auth_source = microsoft
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_INSTITUTIONAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_MICROSOFT
    )


def _has_valid_cedula(user):
    """
    Comprueba que la cédula contenga exactamente 10 dígitos.
    """
    cedula = _normalize_text(
        getattr(
            user,
            "identificacion",
            "",
        )
    )

    return bool(
        CEDULA_PATTERN.fullmatch(
            cedula
        )
    )


def _calculate_profile_complete(user):
    """
    Calcula la completitud efectiva del perfil utilizando, cuando está
    disponible, la regla central del modelo Usuario.
    """
    if user is None:
        return False

    calcular = getattr(
        user,
        "calcular_perfil_completo",
        None,
    )

    if callable(calcular):
        return bool(calcular())

    if _is_external_user(user):
        return True

    if _is_institutional_user(user):
        return bool(
            _has_valid_cedula(user)
            and getattr(user, "sede_id", None)
            and getattr(user, "carrera_id", None)
        )

    return False

def _get_user_queryset():
    """
    Queryset utilizado durante el inicio de sesión.

    Precarga únicamente relaciones de lectura. No se utiliza con
    select_for_update().
    """
    return User.objects.select_related(
        "sede",
        "carrera",
        "carrera__facultad",
        "autor",
    )


def _get_user_with_relations(user_id):
    """
    Recupera al usuario por su identificador con las relaciones
    necesarias para construir la respuesta.
    """
    if not user_id:
        return None

    return (
        _get_user_queryset()
        .filter(
            pk=user_id
        )
        .first()
    )


def _get_user_by_email(email):
    """
    Recupera al usuario por correo antes de autenticar.

    Esto permite informar correctamente cuando una cuenta está
    inactiva o debe utilizar Microsoft 365.
    """
    normalized_email = _normalize_email(
        email
    )

    if not normalized_email:
        return None

    return (
        _get_user_queryset()
        .filter(
            email__iexact=normalized_email
        )
        .first()
    )


def _get_site(user):
    """
    Obtiene la Sede únicamente cuando el usuario es institucional.
    """
    if not _is_institutional_user(user):
        return None

    if not getattr(user, "sede_id", None):
        return None

    return getattr(user, "sede", None)


def _get_career(user):
    """
    Obtiene la Carrera únicamente cuando el usuario es
    institucional.

    De esta forma no se exponen relaciones académicas residuales
    de usuarios externos o cuentas inconsistentes.
    """
    if not _is_institutional_user(
        user
    ):
        return None

    if not getattr(
        user,
        "carrera_id",
        None,
    ):
        return None

    return getattr(
        user,
        "carrera",
        None,
    )


def _get_faculty(user):
    """
    Obtiene la Facultad derivada desde Carrera.
    """
    career = _get_career(
        user
    )

    if career is None:
        return None

    return getattr(
        career,
        "facultad",
        None,
    )


def _get_author_id(user):
    """
    Obtiene el identificador del Autor relacionado.
    """
    if user is None:
        return None

    try:
        author = user.autor

    except (
        ObjectDoesNotExist,
        AttributeError,
    ):
        return None

    return getattr(
        author,
        "pk",
        None,
    )


def _avatar_url(
    user,
    request=None,
):
    """
    Obtiene la URL del avatar.

    Cuando existe request, devuelve una URL absoluta.
    """
    avatar = getattr(
        user,
        "avatar",
        None,
    )

    if not avatar:
        return None

    avatar_name = getattr(
        avatar,
        "name",
        None,
    )

    if not avatar_name:
        return None

    try:
        url = avatar.url

    except (
        ValueError,
        OSError,
    ):
        return None

    if request is None:
        return url

    try:
        return request.build_absolute_uri(
            url
        )

    except (
        ValueError,
        TypeError,
    ):
        return url


def _generate_tokens(user):
    """
    Genera los tokens JWT del usuario.
    """
    refresh = RefreshToken.for_user(
        user
    )

    return {
        "access": str(
            refresh.access_token
        ),
        "refresh": str(
            refresh
        ),
    }


def _profile_seconds_remaining(
    edit_status,
):
    """
    Calcula los segundos restantes del periodo de edición.
    """
    deadline = edit_status.get(
        "profile_edit_until"
    )

    if (
        deadline is None
        or edit_status.get(
            "expired",
            False,
        )
    ):
        return 0

    try:
        remaining = (
            deadline
            - timezone.now()
        ).total_seconds()

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return 0

    return max(
        0,
        int(
            remaining
        ),
    )


# ============================================================
# PAYLOAD DEL USUARIO
# ============================================================

def build_local_auth_user_payload(
    user,
    request=None,
):
    """
    Construye la información del usuario autenticado.

    El payload utiliza las mismas reglas de clasificación que el
    serializer de lectura del perfil.
    """
    role = _normalized_role(
        user
    )

    auth_source = (
        _normalized_auth_source(
            user
        )
        or AUTH_SOURCE_LOCAL
    )

    is_external = _is_external_user(
        user
    )

    is_institutional = (
        _is_institutional_user(
            user
        )
    )

    site = _get_site(
        user
    )

    career = _get_career(
        user
    )

    faculty = _get_faculty(
        user
    )

    edit_status = (
        get_profile_edit_status(
            user
        )
    )

    full_name = ""

    get_full_name = getattr(
        user,
        "get_full_name",
        None,
    )

    if callable(
        get_full_name
    ):
        full_name = _normalize_text(
            get_full_name()
        )

    if not full_name:
        full_name = " ".join(
            part
            for part in [
                _normalize_text(
                    getattr(
                        user,
                        "nombres",
                        "",
                    )
                ),
                _normalize_text(
                    getattr(
                        user,
                        "apellidos",
                        "",
                    )
                ),
            ]
            if part
        )

    if is_external:
        type_label = "Cuenta externa"
        role_label = "Autor externo"
        auth_source_label = "Cuenta local"

    elif is_institutional:
        type_label = "Cuenta institucional"
        role_label = "Autor institucional"
        auth_source_label = "Microsoft 365"

    else:
        type_label = (
            "Cuenta sin clasificación válida"
        )

        role_label = (
            _normalize_text(
                getattr(
                    user,
                    "get_rol_display",
                    lambda: role,
                )()
            )
            or role
            or "Usuario"
        )

        auth_source_label = (
            _normalize_text(
                getattr(
                    user,
                    "get_auth_source_display",
                    lambda: auth_source,
                )()
            )
            or auth_source
        )

    is_staff = bool(
        getattr(
            user,
            "is_staff",
            False,
        )
    )

    is_superuser = bool(
        getattr(
            user,
            "is_superuser",
            False,
        )
    )

    is_admin = bool(
        is_staff
        or is_superuser
    )

    snooze_until = getattr(
        user,
        "perfil_banner_snooze_until",
        None,
    )

    perfil_banner_snoozed = bool(
        snooze_until is not None
        and snooze_until
        > timezone.now()
    )

    return {
        # ====================================================
        # IDENTIDAD
        # ====================================================

        "id": user.pk,

        "email": getattr(
            user,
            "email",
            None,
        ),

        "nombres": getattr(
            user,
            "nombres",
            "",
        ),

        "apellidos": getattr(
            user,
            "apellidos",
            "",
        ),

        "full_name": full_name,

        "identificacion": getattr(
            user,
            "identificacion",
            None,
        ),

        # ====================================================
        # CLASIFICACIÓN
        # ====================================================

        "rol": role,

        "rol_label": role_label,

        "auth_source": auth_source,

        "auth_source_label": (
            auth_source_label
        ),

        "es_externo": is_external,

        "es_institucional": (
            is_institutional
        ),

        "tipo_cuenta_label": (
            type_label
        ),

        # ====================================================
        # PERFIL
        # ====================================================

        "perfil_completo": (
            _calculate_profile_complete(
                user
            )
        ),

        "perfil_banner_snooze_until": (
            snooze_until
        ),

        "perfil_banner_snoozed": (
            perfil_banner_snoozed
        ),

        "fecha_registro": getattr(
            user,
            "fecha_registro",
            None,
        ),

        # ====================================================
        # ESTADO Y PERMISOS
        # ====================================================

        "is_active": bool(
            getattr(
                user,
                "is_active",
                False,
            )
        ),

        "is_staff": is_staff,

        "is_superuser": (
            is_superuser
        ),

        "es_admin": is_admin,

        "is_admin": is_admin,

        # ====================================================
        # RELACIÓN ACADÉMICA
        # ====================================================

        "sede_id": getattr(
            site,
            "pk",
            None,
        ),

        "sede": getattr(
            site,
            "nombre",
            None,
        ),

        "facultad_id": getattr(
            career,
            "facultad_id",
            None,
        ),

        "facultad": getattr(
            faculty,
            "nombre",
            None,
        ),

        "carrera_id": getattr(
            career,
            "pk",
            None,
        ),

        "carrera": getattr(
            career,
            "nombre",
            None,
        ),

        # ====================================================
        # AUTOR Y AVATAR
        # ====================================================

        "autor_id": _get_author_id(
            user
        ),

        "avatar_url": _avatar_url(
            user,
            request=request,
        ),

        # ====================================================
        # MICROSOFT
        # ====================================================

        "ms_display_name": getattr(
            user,
            "ms_display_name",
            None,
        ),

        "ms_last_sync": getattr(
            user,
            "ms_last_sync",
            None,
        ),

        # ====================================================
        # CONTROL DE EDICIÓN
        # ====================================================

        "profile_edit_locked": bool(
            edit_status.get(
                "profile_edit_locked",
                False,
            )
        ),

        "profile_edit_lock_reason": (
            edit_status.get(
                "profile_edit_lock_reason"
            )
        ),

        "profile_edit_attempts_left": int(
            edit_status.get(
                "attempts_left",
                0,
            )
            or 0
        ),

        "profile_edit_until": (
            edit_status.get(
                "profile_edit_until"
            )
        ),

        "profile_edit_available": bool(
            edit_status.get(
                "available",
                False,
            )
        ),

        "profile_edit_expired": bool(
            edit_status.get(
                "expired",
                False,
            )
        ),

        "profile_edit_seconds_remaining": (
            _profile_seconds_remaining(
                edit_status
            )
        ),
    }


# ============================================================
# RESPUESTAS
# ============================================================

def _invalid_credentials_response():
    """
    Respuesta genérica para credenciales inválidas.
    """
    return Response(
        {
            "detail": (
                "El correo electrónico o la contraseña "
                "son incorrectos."
            )
        },
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _inactive_account_response():
    """
    Respuesta para una cuenta inactiva.
    """
    return Response(
        {
            "detail": (
                "La cuenta se encuentra inactiva. "
                "Comuníquese con el administrador."
            )
        },
        status=status.HTTP_403_FORBIDDEN,
    )


def _microsoft_account_response():
    """
    Respuesta para cuentas que deben utilizar Microsoft.
    """
    return Response(
        {
            "detail": (
                "Esta cuenta debe iniciar sesión "
                "mediante Microsoft 365."
            )
        },
        status=status.HTTP_403_FORBIDDEN,
    )


def _invalid_account_classification_response():
    """
    Respuesta para combinaciones inconsistentes de rol y origen
    de autenticación.
    """
    return Response(
        {
            "detail": (
                "La cuenta presenta una clasificación "
                "inconsistente. Solicite una revisión "
                "al administrador."
            )
        },
        status=status.HTTP_409_CONFLICT,
    )


def _author_sync_error_response():
    """
    Respuesta controlada cuando existe un conflicto entre
    Usuario y Autor.
    """
    return Response(
        {
            "detail": (
                "La cuenta fue autenticada, pero existe un "
                "conflicto con su registro de autor. "
                "Solicite una revisión al administrador."
            )
        },
        status=status.HTTP_409_CONFLICT,
    )


# ============================================================
# LOGIN
# ============================================================

class LoginView(APIView):
    """
    Inicio de sesión mediante correo y contraseña.

    Este endpoint es público y no intenta autenticar un token
    previamente guardado por el navegador.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(
        self,
        request,
    ):
        serializer = LoginSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data[
            "email"
        ]

        password = serializer.validated_data[
            "password"
        ]

        # ====================================================
        # COMPROBACIÓN PREVIA DE LA CUENTA
        # ====================================================

        candidate_user = (
            _get_user_by_email(
                email
            )
        )

        if candidate_user is None:
            return _invalid_credentials_response()

        candidate_auth_source = (
            _normalized_auth_source(
                candidate_user
            )
        )

        if (
            candidate_auth_source
            == AUTH_SOURCE_MICROSOFT
        ):
            return _microsoft_account_response()

        if (
            candidate_auth_source
            != AUTH_SOURCE_LOCAL
        ):
            logger.warning(
                (
                    "Intento de inicio local para el Usuario "
                    "%s con auth_source desconocido: %s"
                ),
                candidate_user.pk,
                candidate_auth_source,
            )

            return (
                _invalid_account_classification_response()
            )

        if not bool(
            getattr(
                candidate_user,
                "is_active",
                False,
            )
        ):
            return _inactive_account_response()

        candidate_role = _normalized_role(
            candidate_user
        )

        if (
            candidate_role
            not in SYNCABLE_AUTHOR_ROLES
        ):
            logger.error(
                (
                    "El Usuario %s tiene una combinación "
                    "de rol y autenticación no reconocida: "
                    "rol=%s, auth_source=%s."
                ),
                candidate_user.pk,
                candidate_role,
                candidate_auth_source,
            )

            return (
                _invalid_account_classification_response()
            )

        # ====================================================
        # AUTENTICACIÓN
        # ====================================================

        credentials = {
            User.USERNAME_FIELD: email,
            "password": password,
        }

        authenticated = authenticate(
            request=request,
            **credentials,
        )

        if authenticated is None:
            return _invalid_credentials_response()

        authenticated_user = (
            _get_user_with_relations(
                authenticated.pk
            )
        )

        if authenticated_user is None:
            return _invalid_credentials_response()

        if not bool(
            getattr(
                authenticated_user,
                "is_active",
                False,
            )
        ):
            return _inactive_account_response()

        auth_source = (
            _normalized_auth_source(
                authenticated_user
            )
        )

        if (
            auth_source
            == AUTH_SOURCE_MICROSOFT
        ):
            return _microsoft_account_response()

        if (
            auth_source
            != AUTH_SOURCE_LOCAL
        ):
            return (
                _invalid_account_classification_response()
            )

        role = _normalized_role(
            authenticated_user
        )

        if role not in SYNCABLE_AUTHOR_ROLES:
            return (
                _invalid_account_classification_response()
            )

        # ====================================================
        # SINCRONIZACIÓN DEL AUTOR
        # ====================================================

        try:
            with transaction.atomic():
                author = (
                    asegurar_autor_para_usuario(
                        authenticated_user
                    )
                )

                if author is None:
                    raise DjangoValidationError(
                        (
                            "No fue posible obtener el "
                            "Autor relacionado."
                        )
                    )

        except (
            DjangoValidationError,
            IntegrityError,
            DatabaseError,
        ):
            logger.exception(
                (
                    "No se pudo sincronizar el Autor durante "
                    "el inicio de sesión del Usuario %s."
                ),
                authenticated_user.pk,
            )

            return _author_sync_error_response()

        # Se consulta nuevamente para obtener posibles cambios
        # realizados durante la sincronización.
        authenticated_user = (
            _get_user_with_relations(
                authenticated_user.pk
            )
        )

        if authenticated_user is None:
            return _invalid_credentials_response()

        # ====================================================
        # TOKENS Y RESPUESTA
        # ====================================================

        tokens = _generate_tokens(
            authenticated_user
        )

        refresh_token = tokens.get(
            "refresh",
            "",
        )

        response = Response(
            {
                "message": (
                    "Inicio de sesión correcto."
                ),

                "tokens": {
                    "access": tokens.get(
                        "access",
                        "",
                    ),
                },

                "user": (
                    build_local_auth_user_payload(
                        authenticated_user,
                        request=request,
                    )
                ),
            },
            status=status.HTTP_200_OK,
        )

        set_refresh_cookie(
            response,
            refresh_token,
        )

        # Evita que navegadores o proxies almacenen los tokens.
        response[
            "Cache-Control"
        ] = "no-store"

        response[
            "Pragma"
        ] = "no-cache"

        registrar_evento_auditoria(
            actor=authenticated_user,
            accion="login",
            modulo="autenticacion",
            entidad=authenticated_user,
            descripcion="Inicio de sesión local correcto.",
            contexto={"origen": "local"},
            request=request,
        )

        return response 