"""
View para actualizar el avatar del usuario autenticado.

Responsabilidades:

- Recibir imágenes mediante multipart/form-data.
- Validar el archivo con AvatarUpdateSerializer.
- Bloquear la fila del usuario durante la actualización.
- Modificar exclusivamente el campo avatar.
- Evitar sincronizaciones innecesarias del registro Autor.
- Devolver la URL absoluta del avatar actualizado.
- Impedir que la respuesta con información del perfil se almacene
  en caché.

La validación del formato, contenido, peso y dimensiones se realiza
en AvatarUpdateSerializer.
"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import DatabaseError, transaction

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.auth.serializers.auth_avatar_serializers import (
    AvatarUpdateSerializer,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# UTILIDADES
# ============================================================

def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una respuesta
    compatible con Django REST Framework.
    """
    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {
            "detail": list(exc.messages),
        }

    return {
        "detail": str(exc),
    }


def _get_avatar_url(
    user,
    request=None,
):
    """
    Obtiene la URL del avatar almacenado.

    Cuando existe una request, devuelve una URL absoluta.
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
        avatar_url = avatar.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return avatar_url

    try:
        return request.build_absolute_uri(
            avatar_url
        )

    except (
        ValueError,
        TypeError,
    ):
        return avatar_url


def _get_uploaded_avatar(request):
    """
    Obtiene el archivo recibido en el campo avatar.
    """
    uploaded_avatar = request.FILES.get(
        "avatar"
    )

    if uploaded_avatar is None:
        uploaded_avatar = request.data.get(
            "avatar"
        )

    return uploaded_avatar


def _get_user_after_update(user_id):
    """
    Recupera el usuario después de confirmar la actualización.
    """
    if not user_id:
        return None

    return (
        User.objects
        .only(
            "id",
            "avatar",
        )
        .filter(
            pk=user_id
        )
        .first()
    )


# ============================================================
# VISTA
# ============================================================

class UpdateAvatarView(APIView):
    """
    Actualización del avatar del usuario autenticado.

    Se admiten PATCH y POST para mantener compatibilidad con el
    frontend existente.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def patch(self, request):
        return self._update_avatar(
            request
        )

    def post(self, request):
        return self._update_avatar(
            request
        )

    def _update_avatar(self, request):
        """
        Valida y actualiza exclusivamente el campo avatar.
        """
        user_id = getattr(
            request.user,
            "pk",
            None,
        )

        if not user_id:
            return Response(
                {
                    "detail": (
                        "No fue posible determinar "
                        "el usuario autenticado."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        uploaded_avatar = _get_uploaded_avatar(
            request
        )

        if uploaded_avatar is None:
            return Response(
                {
                    "avatar": [
                        "Debe adjuntar una imagen."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                locked_user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=user_id
                    )
                )

                serializer = (
                    AvatarUpdateSerializer(
                        locked_user,
                        data={
                            "avatar": uploaded_avatar,
                        },
                        partial=False,
                        context={
                            "request": request,
                        },
                    )
                )

                serializer.is_valid(
                    raise_exception=True
                )

                # No se utiliza serializer.save() porque el
                # ModelSerializer ejecutaría instance.save()
                # sin update_fields.
                #
                # Guardar explícitamente solo "avatar" permite
                # que el signal de Usuario ignore este cambio.
                locked_user.avatar = (
                    serializer.validated_data[
                        "avatar"
                    ]
                )

                locked_user.save(
                    update_fields=[
                        "avatar",
                    ]
                )

                updated_user_id = (
                    locked_user.pk
                )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario autenticado "
                        "ya no existe."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except OSError:
            logger.exception(
                (
                    "No se pudo almacenar el avatar "
                    "del usuario %s."
                ),
                user_id,
            )

            return Response(
                {
                    "detail": (
                        "No se pudo almacenar la imagen. "
                        "Revise la configuración del "
                        "almacenamiento e inténtelo nuevamente."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al actualizar "
                    "el avatar del usuario %s."
                ),
                user_id,
            )

            return Response(
                {
                    "detail": (
                        "No se pudo actualizar el avatar "
                        "debido a un error temporal de la "
                        "base de datos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        updated_user = _get_user_after_update(
            updated_user_id
        )

        if updated_user is None:
            return Response(
                {
                    "detail": (
                        "El avatar fue procesado, pero no "
                        "fue posible recuperar el perfil "
                        "actualizado."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        avatar_url = _get_avatar_url(
            updated_user,
            request=request,
        )

        response = Response(
            {
                "detail": (
                    "Avatar actualizado correctamente."
                ),
                "avatar_url": avatar_url,
            },
            status=status.HTTP_200_OK,
        )

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate"
        )

        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response