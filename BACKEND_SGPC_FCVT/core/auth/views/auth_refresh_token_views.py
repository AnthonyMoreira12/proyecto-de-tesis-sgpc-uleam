"""
View para renovar el access token JWT mediante cookie HttpOnly.

Responsabilidades:

- Recuperar el refresh token exclusivamente desde una cookie HttpOnly.
- Comprobar firma, tipo, expiración y lista negra.
- Verificar que el usuario asociado continúe existiendo y activo.
- Respetar la rotación configurada en SimpleJWT.
- Reemplazar la cookie cuando SimpleJWT rote el refresh token.
- No exponer nunca el refresh token en el cuerpo de la respuesta.
- Eliminar la cookie cuando el refresh sea inválido o haya expirado.
- Evitar que las respuestas con credenciales sean almacenadas en caché.
"""

from django.contrib.auth import get_user_model

from rest_framework import permissions, status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.services.auth_token_cookie_services import (
    delete_refresh_cookie,
    get_refresh_token_from_request,
    set_refresh_cookie,
)


User = get_user_model()


# ============================================================
# RESPUESTAS
# ============================================================


def _no_store_response(
    payload,
    *,
    status_code,
):
    """
    Construye una respuesta que no debe almacenarse en caché.
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

    return response


def _invalid_refresh_response():
    """
    Respuesta genérica para refresh tokens inválidos, vencidos,
    revocados o asociados a cuentas no disponibles.

    La cookie se elimina para impedir intentos repetidos con una
    credencial que ya no puede utilizarse.
    """
    response = _no_store_response(
        {
            "detail": (
                "La sesión ha expirado o ya no está disponible."
            )
        },
        status_code=status.HTTP_401_UNAUTHORIZED,
    )

    delete_refresh_cookie(
        response
    )

    return response


# ============================================================
# USUARIO DEL TOKEN
# ============================================================


def _get_user_from_refresh_token(
    refresh_token,
):
    """
    Recupera el usuario asociado utilizando USER_ID_CLAIM y
    USER_ID_FIELD de la configuración real de SimpleJWT.
    """
    user_id_claim = (
        api_settings.USER_ID_CLAIM
    )

    user_id_field = (
        api_settings.USER_ID_FIELD
    )

    user_identifier = refresh_token.get(
        user_id_claim
    )

    if user_identifier in (
        None,
        "",
    ):
        return None

    try:
        return (
            User.objects
            .only(
                "pk",
                "is_active",
            )
            .filter(
                **{
                    user_id_field: (
                        user_identifier
                    )
                }
            )
            .first()
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def _user_can_refresh(user):
    """
    Una cuenta eliminada o inactiva no puede generar nuevos
    access tokens aunque conserve una cookie anterior.
    """
    if user is None:
        return False

    return bool(
        getattr(
            user,
            "is_active",
            False,
        )
    )


# ============================================================
# VISTA
# ============================================================


class RefreshTokenView(APIView):
    """
    Renueva el access token utilizando la cookie HttpOnly.

    El frontend debe llamar al endpoint con credenciales habilitadas
    (`withCredentials: true`). El cuerpo de la solicitud puede estar
    vacío y el refresh token nunca debe enviarse desde JavaScript.
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
            return _invalid_refresh_response()

        try:
            # ==================================================
            # VALIDACIÓN INICIAL DEL REFRESH
            # ==================================================

            refresh_token = RefreshToken(
                raw_refresh_token
            )

            # RefreshToken valida firma, expiración, tipo de token
            # y blacklist cuando esa aplicación está habilitada.

            # ==================================================
            # VALIDACIÓN DEL USUARIO
            # ==================================================

            user = _get_user_from_refresh_token(
                refresh_token
            )

            if not _user_can_refresh(
                user
            ):
                return _invalid_refresh_response()

            # ==================================================
            # ROTACIÓN OFICIAL DE SIMPLEJWT
            # ==================================================

            token_serializer = (
                TokenRefreshSerializer(
                    data={
                        "refresh": (
                            raw_refresh_token
                        )
                    },
                    context={
                        "request": request,
                    },
                )
            )

            token_serializer.is_valid(
                raise_exception=True
            )

            token_data = dict(
                token_serializer.validated_data
            )

        except (
            TokenError,
            InvalidToken,
            DRFValidationError,
        ):
            return _invalid_refresh_response()

        access_token = token_data.get(
            "access",
            "",
        )

        if not access_token:
            return _invalid_refresh_response()

        # Cuando ROTATE_REFRESH_TOKENS=True, SimpleJWT devuelve
        # un refresh nuevo y, con BLACKLIST_AFTER_ROTATION=True,
        # invalida el anterior.
        rotated_refresh_token = token_data.get(
            "refresh",
            "",
        )

        response = _no_store_response(
            {
                "access": access_token,
            },
            status_code=status.HTTP_200_OK,
        )

        if rotated_refresh_token:
            set_refresh_cookie(
                response,
                rotated_refresh_token,
            )

        return response
