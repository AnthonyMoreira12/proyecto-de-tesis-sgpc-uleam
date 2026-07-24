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
"""

import logging

from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import (
    DatabaseError,
    IntegrityError,
)

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
from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.auth.services.auth_profile_services import (
    get_profile_edit_status,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# CONSTANTES
# ============================================================

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"

SYNCABLE_AUTHOR_ROLES = {
    "autor",
    "autor_externo",
}


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza valores textuales opcionales.
    """
    return str(
        value or ""
    ).strip()


def _get_user_with_relations(user_id):
    """
    Recupera al usuario con su relación académica precargada.
    """
    if not user_id:
        return None

    return (
        User.objects
        .select_related(
            "carrera",
            "carrera__facultad",
        )
        .filter(
            pk=user_id
        )
        .first()
    )


def _get_career(user):
    """
    Obtiene de forma segura la carrera del usuario.
    """
    if user is None:
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
    Obtiene la facultad derivada desde carrera.facultad.
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


# ============================================================
# PAYLOAD DEL USUARIO
# ============================================================

def build_local_auth_user_payload(
    user,
    request=None,
):
    """
    Construye la información básica del usuario autenticado.

    Se conserva el formato utilizado actualmente por el
    frontend y se agregan datos derivados seguros.
    """
    career = _get_career(
        user
    )

    faculty = _get_faculty(
        user
    )

    edit_status = get_profile_edit_status(
        user
    )

    full_name = _normalize_text(
        getattr(
            user,
            "get_full_name",
            lambda: "",
        )()
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

    return {
        "id": user.pk,

        "email": user.email,

        "nombres": user.nombres,

        "apellidos": user.apellidos,

        "full_name": full_name,

        "rol": user.rol,

        "auth_source": getattr(
            user,
            "auth_source",
            AUTH_SOURCE_LOCAL,
        ),

        "perfil_completo": bool(
            getattr(
                user,
                "perfil_completo",
                False,
            )
        ),

        "is_active": bool(
            getattr(
                user,
                "is_active",
                False,
            )
        ),

        "is_staff": bool(
            getattr(
                user,
                "is_staff",
                False,
            )
        ),

        "is_superuser": bool(
            getattr(
                user,
                "is_superuser",
                False,
            )
        ),

        "es_admin": bool(
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
        ),

        # Facultad derivada desde la carrera.
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
            user,
            "carrera_id",
            None,
        ),

        "carrera": getattr(
            career,
            "nombre",
            None,
        ),

        "avatar_url": _avatar_url(
            user,
            request=request,
        ),

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
    }


# ============================================================
# RESPUESTAS
# ============================================================

def _invalid_credentials_response():
    """
    Respuesta genérica para no revelar si el correo existe.
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

    Este endpoint es público y no debe intentar autenticar un
    token enviado previamente por el navegador.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
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

        credentials = {
            User.USERNAME_FIELD: email,
            "password": password,
        }

        user = authenticate(
            request=request,
            **credentials,
        )

        if user is None:
            return _invalid_credentials_response()

        # Se consulta nuevamente para obtener las relaciones
        # académicas y el estado definitivo de la cuenta.
        authenticated_user = (
            _get_user_with_relations(
                user.pk
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
            return Response(
                {
                    "detail": (
                        "La cuenta se encuentra inactiva. "
                        "Comuníquese con el administrador."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        auth_source = _normalize_text(
            getattr(
                authenticated_user,
                "auth_source",
                AUTH_SOURCE_LOCAL,
            )
        ).lower()

        if auth_source == AUTH_SOURCE_MICROSOFT:
            return Response(
                {
                    "detail": (
                        "Esta cuenta debe iniciar sesión "
                        "mediante Microsoft 365."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if auth_source != AUTH_SOURCE_LOCAL:
            logger.warning(
                (
                    "Intento de inicio local para el usuario "
                    "%s con auth_source desconocido: %s"
                ),
                authenticated_user.pk,
                auth_source,
            )

            return _invalid_credentials_response()

        role = _normalize_text(
            getattr(
                authenticated_user,
                "rol",
                "",
            )
        ).lower()

        # ====================================================
        # SINCRONIZACIÓN DEL AUTOR
        # ====================================================

        try:
            author = asegurar_autor_para_usuario(
                authenticated_user
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

        if (
            role in SYNCABLE_AUTHOR_ROLES
            and author is None
        ):
            logger.error(
                (
                    "El Usuario %s inició autenticación, pero "
                    "no fue posible obtener su Autor."
                ),
                authenticated_user.pk,
            )

            return _author_sync_error_response()

        # Se vuelve a consultar por si la sincronización actualizó
        # datos relacionados con el usuario.
        authenticated_user = (
            _get_user_with_relations(
                authenticated_user.pk
            )
        )

        if authenticated_user is None:
            return _invalid_credentials_response()

        tokens = _generate_tokens(
            authenticated_user
        )

        response = Response(
            {
                "message": (
                    "Inicio de sesión correcto."
                ),

                "tokens": tokens,

                "user": (
                    build_local_auth_user_payload(
                        authenticated_user,
                        request=request,
                    )
                ),
            },
            status=status.HTTP_200_OK,
        )

        # Impide que navegadores o proxies almacenen tokens.
        response[
            "Cache-Control"
        ] = "no-store"

        response[
            "Pragma"
        ] = "no-cache"

        return response