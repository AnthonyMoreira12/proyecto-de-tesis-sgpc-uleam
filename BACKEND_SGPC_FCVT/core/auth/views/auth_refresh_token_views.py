"""
View para renovar tokens JWT.

Responsabilidades:

- Validar la presencia y estructura del refresh token.
- Comprobar firma, tipo, expiración y lista negra.
- Verificar que el usuario asociado continúe existiendo.
- Impedir la renovación de cuentas inactivas.
- Respetar la rotación de refresh tokens configurada en SimpleJWT.
- Evitar que las respuestas con tokens sean almacenadas en caché.
"""

from django.contrib.auth import get_user_model

from rest_framework import permissions, serializers, status
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


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_REFRESH_TOKEN_LENGTH = 4096


# ============================================================
# SERIALIZER DE ENTRADA
# ============================================================

class RefreshTokenInputSerializer(
    serializers.Serializer
):
    """
    Valida la estructura básica de la solicitud.

    La validación criptográfica se realiza posteriormente
    mediante SimpleJWT.
    """

    refresh = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=MAX_REFRESH_TOKEN_LENGTH,
        write_only=True,
        error_messages={
            "required": (
                "El refresh token es obligatorio."
            ),
            "blank": (
                "El refresh token es obligatorio."
            ),
            "max_length": (
                "El refresh token recibido no es válido."
            ),
        },
    )

    def validate_refresh(
        self,
        value,
    ):
        normalized_token = str(
            value or ""
        ).strip()

        if not normalized_token:
            raise serializers.ValidationError(
                "El refresh token es obligatorio."
            )

        return normalized_token


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
        "no-store, no-cache, must-revalidate"
    )

    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


def _invalid_refresh_response():
    """
    Respuesta genérica para tokens inválidos, vencidos,
    revocados o pertenecientes a cuentas no disponibles.
    """
    return _no_store_response(
        {
            "detail": (
                "El refresh token es inválido, "
                "ha expirado o ya no está disponible."
            )
        },
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


# ============================================================
# USUARIO DEL TOKEN
# ============================================================

def _get_user_from_refresh_token(
    refresh_token,
):
    """
    Recupera el usuario asociado utilizando las configuraciones:

    - USER_ID_CLAIM
    - USER_ID_FIELD

    Esto evita asumir que el identificador siempre es `id`.
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
    Comprueba que el usuario continúe habilitado.

    Una cuenta eliminada o inactiva no puede generar nuevos
    access tokens aunque conserve un refresh token anterior.
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
    Renueva el access token mediante un refresh token válido.

    El endpoint es público porque el refresh token constituye
    la credencial utilizada en esta operación.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        # ====================================================
        # VALIDACIÓN DE LA SOLICITUD
        # ====================================================

        input_serializer = (
            RefreshTokenInputSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        if not input_serializer.is_valid():
            return _no_store_response(
                input_serializer.errors,
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        raw_refresh_token = (
            input_serializer.validated_data[
                "refresh"
            ]
        )

        try:
            # ================================================
            # VALIDACIÓN INICIAL DEL TOKEN
            # ================================================

            refresh_token = RefreshToken(
                raw_refresh_token
            )

            # RefreshToken comprueba:
            #
            # - Firma.
            # - Expiración.
            # - Tipo de token.
            # - Lista negra cuando está habilitada.

            # ================================================
            # VALIDACIÓN DEL USUARIO
            # ================================================

            user = _get_user_from_refresh_token(
                refresh_token
            )

            if not _user_can_refresh(
                user
            ):
                return _invalid_refresh_response()

            # ================================================
            # RENOVACIÓN OFICIAL DE SIMPLEJWT
            # ================================================

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

            response_payload = dict(
                token_serializer.validated_data
            )

        except (
            TokenError,
            InvalidToken,
            DRFValidationError,
        ):
            return _invalid_refresh_response()

        # TokenRefreshSerializer siempre devuelve access.
        # Cuando ROTATE_REFRESH_TOKENS=True también puede
        # devolver un refresh token nuevo.
        if not response_payload.get(
            "access"
        ):
            return _invalid_refresh_response()

        return _no_store_response(
            response_payload,
            status_code=status.HTTP_200_OK,
        )