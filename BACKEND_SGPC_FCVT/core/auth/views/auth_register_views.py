"""
View para el registro público de usuarios externos.

La operación garantiza que:

- El usuario se cree como autor externo local.
- El registro Autor asociado se cree o sincronice.
- Usuario y Autor se guarden dentro de una misma transacción.
- Los tokens JWT solo se generen después de confirmar el registro.
- No se devuelvan tokens cuando el proceso quede incompleto.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction

from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.serializers.auth_register_serializers import (
    RegisterSerializer,
)
from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.auth.views.auth_login_views import (
    build_local_auth_user_payload,
)


User = get_user_model()


# ============================================================
# UTILIDADES
# ============================================================

def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
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


def _get_registered_user(user_id):
    """
    Recupera al usuario recién registrado con su relación
    académica precargada.
    """
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


def _build_tokens(user):
    """
    Genera los tokens JWT para el usuario registrado.
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
# REGISTRO
# ============================================================

class RegisterView(APIView):
    """
    Registra un autor externo y devuelve una sesión JWT.

    El endpoint es público y no utiliza una autenticación
    previamente establecida.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            with transaction.atomic():
                # ============================================
                # CREACIÓN DEL USUARIO
                # ============================================

                user = serializer.save()

                # ============================================
                # SINCRONIZACIÓN OBLIGATORIA DEL AUTOR
                # ============================================

                author = asegurar_autor_para_usuario(
                    user
                )

                if author is None:
                    raise ValidationError(
                        {
                            "detail": (
                                "No fue posible crear el "
                                "registro académico del autor."
                            )
                        }
                    )

                user_id = user.pk

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se pudo completar el registro "
                        "debido a un conflicto con información "
                        "existente."
                    )
                }
            ) from exc

        # La consulta se realiza después de confirmar la
        # transacción para trabajar únicamente con datos
        # persistidos correctamente.
        registered_user = _get_registered_user(
            user_id
        )

        if registered_user is None:
            return Response(
                {
                    "detail": (
                        "El usuario fue procesado, pero no "
                        "pudo recuperarse después del registro."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        tokens = _build_tokens(
            registered_user
        )

        response = Response(
            {
                "message": (
                    "Usuario registrado correctamente."
                ),

                "tokens": tokens,

                "user": (
                    build_local_auth_user_payload(
                        registered_user,
                        request=request,
                    )
                ),
            },
            status=status.HTTP_201_CREATED,
        )

        # Evita que navegadores o proxies almacenen tokens
        # sensibles dentro de caché.
        response[
            "Cache-Control"
        ] = "no-store"

        response[
            "Pragma"
        ] = "no-cache"

        return response