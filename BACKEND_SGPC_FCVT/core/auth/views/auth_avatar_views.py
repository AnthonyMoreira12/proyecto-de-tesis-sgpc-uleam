"""
Vista para gestionar el avatar del usuario autenticado.

Responsabilidades:

- Recibir imágenes mediante multipart/form-data.
- Validar el archivo con AvatarUpdateSerializer.
- Bloquear la fila del Usuario durante la operación.
- Actualizar exclusivamente el campo avatar.
- Eliminar de forma controlada el archivo anterior.
- Evitar la ejecución innecesaria del signal de Autor.
- Permitir eliminar el avatar mediante DELETE.
- Devolver la URL absoluta del avatar actualizado.
- Impedir que la respuesta quede almacenada en caché.
"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import (
    DatabaseError,
    transaction,
)

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
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

def _django_validation_payload(
    exc,
):
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


def _avatar_storage():
    """
    Obtiene el almacenamiento configurado para el campo avatar.
    """
    return User._meta.get_field(
        "avatar"
    ).storage


def _safe_delete_storage_file(
    file_name,
):
    """
    Elimina un archivo del almacenamiento sin interrumpir la
    respuesta al usuario cuando el archivo ya no existe.
    """
    normalized_name = str(
        file_name or ""
    ).strip()

    if not normalized_name:
        return

    storage = _avatar_storage()

    try:
        if storage.exists(
            normalized_name
        ):
            storage.delete(
                normalized_name
            )

    except (
        OSError,
        ValueError,
        NotImplementedError,
    ):
        logger.exception(
            (
                "No se pudo eliminar el archivo de avatar "
                "%s del almacenamiento."
            ),
            normalized_name,
        )


def _schedule_storage_file_deletion(
    file_name,
):
    """
    Programa la eliminación después de confirmar la transacción.

    Esto evita eliminar el avatar anterior cuando la modificación
    de la base de datos termina siendo revertida.
    """
    normalized_name = str(
        file_name or ""
    ).strip()

    if not normalized_name:
        return

    transaction.on_commit(
        lambda name=normalized_name: (
            _safe_delete_storage_file(
                name
            )
        )
    )


def _get_avatar_url(
    user,
    request=None,
):
    """
    Obtiene la URL del avatar almacenado.

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


def _get_uploaded_avatar(
    request,
):
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


def _get_user_after_update(
    user_id,
):
    """
    Recupera al Usuario después de confirmar la actualización.
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


def _disable_response_cache(
    response,
):
    """
    Impide que el navegador o los proxies almacenen la URL
    anterior del avatar.
    """
    response[
        "Cache-Control"
    ] = (
        "no-store, no-cache, "
        "must-revalidate, max-age=0"
    )

    response[
        "Pragma"
    ] = "no-cache"

    response[
        "Expires"
    ] = "0"

    return response


def _missing_user_response():
    return Response(
        {
            "detail": (
                "No se encontró el usuario autenticado."
            )
        },
        status=status.HTTP_404_NOT_FOUND,
    )


# ============================================================
# VISTA
# ============================================================

class UpdateAvatarView(APIView):
    """
    Actualiza o elimina el avatar del Usuario autenticado.

    Se admiten POST y PATCH para conservar compatibilidad con
    las llamadas existentes del frontend.
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

    # ========================================================
    # ACTUALIZAR
    # ========================================================

    def _update_avatar(
        self,
        request,
    ):
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
                status=(
                    status.HTTP_401_UNAUTHORIZED
                ),
            )

        uploaded_avatar = (
            _get_uploaded_avatar(
                request
            )
        )

        if uploaded_avatar is None:
            raise ValidationError(
                {
                    "avatar": (
                        "Seleccione una imagen para "
                        "actualizar el avatar."
                    )
                }
            )

        serializer = AvatarUpdateSerializer(
            data={
                "avatar": uploaded_avatar,
            },
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_avatar = (
            serializer.validated_data[
                "avatar"
            ]
        )

        locked_user = None
        previous_avatar_name = None
        new_avatar_name = None

        try:
            with transaction.atomic():
                locked_user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=user_id
                    )
                )

                current_avatar = getattr(
                    locked_user,
                    "avatar",
                    None,
                )

                previous_avatar_name = (
                    getattr(
                        current_avatar,
                        "name",
                        None,
                    )
                )

                           # FieldFile.save() almacena físicamente el archivo,
                # pero save=False impide ejecutar el save() completo
                # del modelo Usuario.
                locked_user.avatar.save(
                    getattr(
                        validated_avatar,
                        "name",
                        "avatar",
                    ),
                    validated_avatar,
                    save=False,
                )

                new_avatar_name = getattr(
                    locked_user.avatar,
                    "name",
                    None,
                )

                if not new_avatar_name:
                    raise ValidationError(
                        {
                            "avatar": (
                                "No fue posible almacenar "
                                "la imagen seleccionada."
                            )
                        }
                    )

                updated_rows = (
                    User.objects
                    .filter(
                        pk=locked_user.pk
                    )
                    .update(
                        avatar=new_avatar_name
                    )
                )

                if updated_rows != 1:
                    raise DatabaseError(
                        (
                            "No se pudo actualizar el campo "
                            "avatar del Usuario."
                        )
                    )

                if (
                    previous_avatar_name
                    and previous_avatar_name
                    != new_avatar_name
                ):
                    _schedule_storage_file_deletion(
                        previous_avatar_name
                    )

        except User.DoesNotExist:
            if new_avatar_name:
                _safe_delete_storage_file(
                    new_avatar_name
                )

            return _missing_user_response()

        except DjangoValidationError as exc:
            if (
                new_avatar_name
                and new_avatar_name
                != previous_avatar_name
            ):
                _safe_delete_storage_file(
                    new_avatar_name
                )

            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except ValidationError:
            if (
                new_avatar_name
                and new_avatar_name
                != previous_avatar_name
            ):
                _safe_delete_storage_file(
                    new_avatar_name
                )

            raise

        except (
            DatabaseError,
            OSError,
        ):
            if (
                new_avatar_name
                and new_avatar_name
                != previous_avatar_name
            ):
                _safe_delete_storage_file(
                    new_avatar_name
                )

            logger.exception(
                (
                    "No se pudo actualizar el avatar "
                    "del Usuario %s."
                ),
                user_id,
            )

            return Response(
                {
                    "detail": (
                        "No se pudo actualizar el avatar "
                        "debido a un error interno."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        refreshed_user = (
            _get_user_after_update(
                user_id
            )
        )

        if refreshed_user is None:
            return _missing_user_response()

        response = Response(
            {
                "detail": (
                    "El avatar se actualizó correctamente."
                ),
                "avatar_url": _get_avatar_url(
                    refreshed_user,
                    request=request,
                ),
            },
            status=status.HTTP_200_OK,
        )

        return _disable_response_cache(
            response
        )

    def patch(
        self,
        request,
    ):
        return self._update_avatar(
            request
        )

    def post(
        self,
        request,
    ):
        return self._update_avatar(
            request
        )

    # ========================================================
    # ELIMINAR
    # ========================================================

    def delete(
        self,
        request,
    ):
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
                status=(
                    status.HTTP_401_UNAUTHORIZED
                ),
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

                current_avatar = getattr(
                    locked_user,
                    "avatar",
                    None,
                )

                previous_avatar_name = (
                    getattr(
                        current_avatar,
                        "name",
                        None,
                    )
                )

                updated_rows = (
                    User.objects
                    .filter(
                        pk=locked_user.pk
                    )
                    .update(
                        avatar=None
                    )
                )

                if updated_rows != 1:
                    raise DatabaseError(
                        (
                            "No se pudo eliminar el campo "
                            "avatar del Usuario."
                        )
                    )

                if previous_avatar_name:
                    _schedule_storage_file_deletion(
                        previous_avatar_name
                    )

        except User.DoesNotExist:
            return _missing_user_response()

        except DatabaseError:
            logger.exception(
                (
                    "No se pudo eliminar el avatar "
                    "del Usuario %s."
                ),
                user_id,
            )

            return Response(
                {
                    "detail": (
                        "No se pudo eliminar el avatar "
                        "debido a un error interno."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        response = Response(
            {
                "detail": (
                    "El avatar se eliminó correctamente."
                ),
                "avatar_url": None,
            },
            status=status.HTTP_200_OK,
        )

        return _disable_response_cache(
            response
        )