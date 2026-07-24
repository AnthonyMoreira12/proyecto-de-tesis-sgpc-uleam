"""
View para cerrar la sesión JWT del usuario autenticado.

Responsabilidades:

- Mantener compatibilidad con el cierre de sesión actual.
- Aceptar opcionalmente el refresh token.
- Verificar que el token pertenezca al usuario autenticado.
- Incluir el refresh token en la lista negra cuando SimpleJWT
  tenga habilitada esa funcionalidad.
- Evitar que la respuesta se almacene en caché.
- Indicar al frontend que debe eliminar sus tokens locales.

Importante:

El access token no puede revocarse directamente mediante el
mecanismo estándar de SimpleJWT. El frontend debe eliminar tanto
el access token como el refresh token después de esta respuesta.
"""

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import DatabaseError

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_REFRESH_TOKEN_LENGTH = 4096

TOKEN_BLACKLIST_APP = (
    "rest_framework_simplejwt.token_blacklist"
)


# ============================================================
# SERIALIZER
# ============================================================

class LogoutSerializer(serializers.Serializer):
    """
    Valida el refresh token enviado al cerrar sesión.

    El campo es opcional para conservar compatibilidad con el
    frontend actual, que podría cerrar la sesión eliminando
    únicamente los tokens almacenados localmente.
    """

    refresh = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        max_length=MAX_REFRESH_TOKEN_LENGTH,
        write_only=True,
        error_messages={
            "max_length": (
                "El refresh token recibido no es válido."
            ),
        },
    )

    def validate_refresh(self, value):
        if value in (None, ""):
            return None

        normalized_token = str(value).strip()

        if not normalized_token:
            return None

        return normalized_token


# ============================================================
# UTILIDADES
# ============================================================

def _no_store_response(
    payload,
    *,
    status_code=status.HTTP_200_OK,
):
    """
    Construye una respuesta que no debe almacenarse en caché.
    """
    response = Response(
        payload,
        status=status_code,
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate"
    )
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


def _blacklist_is_available():
    """
    Comprueba si el proyecto tiene instalada la aplicación de
    lista negra de SimpleJWT.
    """
    return apps.is_installed(
        TOKEN_BLACKLIST_APP
    )


def _get_token_user_identifier(refresh_token):
    """
    Obtiene el identificador del usuario contenido en el token
    utilizando la configuración real de SimpleJWT.
    """
    user_id_claim = api_settings.USER_ID_CLAIM

    return refresh_token.get(
        user_id_claim
    )


def _get_request_user_identifier(user):
    """
    Obtiene del usuario autenticado el campo configurado como
    identificador por SimpleJWT.
    """
    user_id_field = api_settings.USER_ID_FIELD

    return getattr(
        user,
        user_id_field,
        None,
    )


def _token_belongs_to_user(
    *,
    refresh_token,
    user,
):
    """
    Comprueba que el refresh token pertenezca al usuario que
    está solicitando el cierre de sesión.
    """
    token_user_identifier = (
        _get_token_user_identifier(
            refresh_token
        )
    )

    request_user_identifier = (
        _get_request_user_identifier(
            user
        )
    )

    if (
        token_user_identifier is None
        or request_user_identifier is None
    ):
        return False

    return str(
        token_user_identifier
    ) == str(
        request_user_identifier
    )


def _blacklist_refresh_token(refresh_token):
    """
    Incluye el refresh token en la lista negra.

    Retorna True cuando la revocación fue realizada.
    """
    blacklist_method = getattr(
        refresh_token,
        "blacklist",
        None,
    )

    if not callable(blacklist_method):
        return False

    blacklist_method()

    return True


# ============================================================
# VIEW
# ============================================================

class LogoutView(APIView):
    """
    Cierra la sesión del usuario autenticado.

    El refresh token puede enviarse mediante:

    {
        "refresh": "TOKEN"
    }

    Cuando no se envía, el endpoint conserva el comportamiento
    anterior y solicita al frontend eliminar sus tokens locales.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        raw_refresh_token = (
            serializer.validated_data.get(
                "refresh"
            )
        )

        # ====================================================
        # CIERRE SOLO EN EL CLIENTE
        # ====================================================

        if not raw_refresh_token:
            return _no_store_response(
                {
                    "detail": (
                        "Sesión cerrada correctamente."
                    ),
                    "server_revoked": False,
                    "clear_client_tokens": True,
                },
                status_code=status.HTTP_200_OK,
            )

        # ====================================================
        # VALIDACIÓN DEL REFRESH TOKEN
        # ====================================================

        try:
            refresh_token = RefreshToken(
                raw_refresh_token
            )

        except TokenError:
            return _no_store_response(
                {
                    "detail": (
                        "El refresh token es inválido "
                        "o ha expirado."
                    ),
                    "server_revoked": False,
                    "clear_client_tokens": True,
                },
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ====================================================
        # PROPIEDAD DEL TOKEN
        # ====================================================

        if not _token_belongs_to_user(
            refresh_token=refresh_token,
            user=request.user,
        ):
            logger.warning(
                (
                    "El usuario %s intentó cerrar sesión "
                    "utilizando un refresh token que no "
                    "le pertenece."
                ),
                request.user.pk,
            )

            return _no_store_response(
                {
                    "detail": (
                        "El refresh token no corresponde "
                        "al usuario autenticado."
                    ),
                    "server_revoked": False,
                    "clear_client_tokens": True,
                },
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        # ====================================================
        # LISTA NEGRA
        # ====================================================

        if not _blacklist_is_available():
            logger.warning(
                (
                    "No se pudo revocar el refresh token del "
                    "usuario %s porque token_blacklist no está "
                    "instalado."
                ),
                request.user.pk,
            )

            return _no_store_response(
                {
                    "detail": (
                        "Sesión cerrada en este dispositivo. "
                        "El servidor no tiene habilitada la "
                        "revocación de refresh tokens."
                    ),
                    "server_revoked": False,
                    "clear_client_tokens": True,
                },
                status_code=status.HTTP_200_OK,
            )

        try:
            server_revoked = (
                _blacklist_refresh_token(
                    refresh_token
                )
            )

        except TokenError:
            return _no_store_response(
                {
                    "detail": (
                        "El refresh token ya no está "
                        "disponible."
                    ),
                    "server_revoked": True,
                    "clear_client_tokens": True,
                },
                status_code=status.HTTP_200_OK,
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al revocar el "
                    "refresh token del usuario %s."
                ),
                request.user.pk,
            )

            return _no_store_response(
                {
                    "detail": (
                        "No fue posible revocar la sesión "
                        "en el servidor debido a un error "
                        "temporal."
                    ),
                    "server_revoked": False,
                    "clear_client_tokens": True,
                },
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return _no_store_response(
            {
                "detail": (
                    "Sesión cerrada correctamente."
                ),
                "server_revoked": bool(
                    server_revoked
                ),
                "clear_client_tokens": True,
            },
            status_code=status.HTTP_200_OK,
        )