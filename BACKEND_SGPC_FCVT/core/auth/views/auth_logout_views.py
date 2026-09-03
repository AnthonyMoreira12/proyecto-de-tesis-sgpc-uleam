"""
View para cerrar la sesión JWT del usuario.

Responsabilidades:

- Recuperar el refresh token desde la cookie HttpOnly.
- Revocar el refresh token mediante la blacklist de SimpleJWT.
- Permitir cerrar sesión aunque el access token ya haya expirado.
- Eliminar siempre la cookie HttpOnly del navegador.
- Mantener el cierre como una operación idempotente.
- Evitar que la respuesta se almacene en caché.

El endpoint no necesita un access token válido: la cookie de refresh
representa la sesión que se está cerrando. Esto evita que un usuario
quede atrapado con una cookie HttpOnly que JavaScript no puede borrar.
"""

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import DatabaseError

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.auditoria.services.auditoria_services import (
    registrar_evento_auditoria,
)
from core.auth.services.auth_token_cookie_services import (
    delete_refresh_cookie,
    get_refresh_token_from_request,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

TOKEN_BLACKLIST_APP = (
    "rest_framework_simplejwt.token_blacklist"
)


# ============================================================
# UTILIDADES
# ============================================================


def _no_store_response(
    payload,
    *,
    status_code=status.HTTP_200_OK,
):
    """
    Construye una respuesta que no debe almacenarse en caché y
    elimina la cookie de refresh del navegador.
    """
    response = Response(
        payload,
        status=status_code,
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    delete_refresh_cookie(
        response
    )

    return response


def _blacklist_is_available():
    """
    Comprueba si la aplicación de blacklist de SimpleJWT está
    instalada en el proyecto.
    """
    return apps.is_installed(
        TOKEN_BLACKLIST_APP
    )


def _blacklist_refresh_token(
    refresh_token,
):
    """
    Incluye el refresh token en la lista negra.
    """
    blacklist_method = getattr(
        refresh_token,
        "blacklist",
        None,
    )

    if not callable(
        blacklist_method
    ):
        return False

    blacklist_method()

    return True


# ============================================================
# VIEW
# ============================================================


class LogoutView(APIView):
    """
    Cierra la sesión asociada a la cookie HttpOnly actual.

    El cuerpo puede estar vacío:

    POST /api/auth/logout/
    {}

    La operación es idempotente. Si la cookie no existe, ya expiró o
    ya fue revocada, se considera igualmente cerrada en el navegador.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        raw_refresh_token = (
            get_refresh_token_from_request(
                request
            )
        )

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

        try:
            refresh_token = RefreshToken(
                raw_refresh_token
            )
            audit_user = User.objects.filter(
                pk=refresh_token.get("user_id")
            ).first()

        except TokenError:
            # Un token vencido, inválido o ya revocado no debe
            # impedir que el navegador elimine su cookie.
            return _no_store_response(
                {
                    "detail": (
                        "Sesión cerrada correctamente."
                    ),
                    "server_revoked": True,
                    "clear_client_tokens": True,
                },
                status_code=status.HTTP_200_OK,
            )

        if not _blacklist_is_available():
            logger.warning(
                (
                    "La sesión se cerró en el navegador, pero "
                    "token_blacklist no está instalado."
                )
            )

            return _no_store_response(
                {
                    "detail": (
                        "Sesión cerrada en este dispositivo."
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
            server_revoked = True

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al revocar un "
                    "refresh token durante el cierre de sesión."
                )
            )

            return _no_store_response(
                {
                    "detail": (
                        "La sesión se eliminó del navegador, "
                        "pero no fue posible completar la "
                        "revocación en el servidor."
                    ),
                    "server_revoked": False,
                    "clear_client_tokens": True,
                },
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        registrar_evento_auditoria(
            actor=audit_user,
            accion="logout",
            modulo="autenticacion",
            entidad=audit_user,
            descripcion="Cierre de sesión correcto.",
            request=request,
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
