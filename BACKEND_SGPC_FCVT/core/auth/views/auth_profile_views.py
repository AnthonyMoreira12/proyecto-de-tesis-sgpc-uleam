"""
Views del perfil del usuario autenticado.

Gestiona:

- Consulta del perfil.
- Actualización controlada del perfil.
- Intentos fallidos de edición.
- Sincronización del autor relacionado.
- Solicitudes de ampliación del periodo de edición.

Las operaciones de actualización se ejecutan de forma
transaccional para evitar estados parciales.
"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction

from rest_framework import status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.auth.serializers.auth_profile_extension_serializers import (
    ProfileEditExtensionRequestSerializer,
)
from core.auth.serializers.auth_profile_read_serializers import (
    ProfileSerializer,
)
from core.auth.serializers.auth_profile_update_serializers import (
    ProfileUpdateSerializer,
)
from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.auth.services.auth_profile_extension_services import (
    ProfileExtensionRequestError,
    send_profile_edit_extension_request,
)
from core.auth.services.auth_profile_services import (
    ProfileEditServiceError,
    ensure_profile_edit_allowed,
    finalize_profile_update,
    get_profile_edit_status,
    register_failed_profile_attempt,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# UTILIDADES
# ============================================================

def _profile_queryset():
    """
    Queryset optimizado para consultar el perfil y su relación
    académica.
    """
    return (
        User.objects
        .select_related(
            "carrera",
            "carrera__facultad",
        )
    )


def _get_current_user(user):
    """
    Obtiene una instancia actualizada del usuario autenticado.
    """
    user_id = getattr(
        user,
        "pk",
        None,
    )

    if not user_id:
        return None

    return (
        _profile_queryset()
        .filter(
            pk=user_id
        )
        .first()
    )


def _django_validation_to_payload(exc):
    """
    Convierte ValidationError de Django en una respuesta
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


def _edit_status_payload(edit_status):
    """
    Convierte el estado interno de edición en los nombres de
    campos consumidos por el frontend.
    """
    edit_status = edit_status or {}

    return {
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

        "attempts_left": int(
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

        "profile_edit_expired": bool(
            edit_status.get(
                "expired",
                False,
            )
        ),

        "profile_edit_available": bool(
            edit_status.get(
                "available",
                False,
            )
        ),
    }


def _build_validation_error_response(
    *,
    user,
    errors,
    decrement_attempt=True,
):
    """
    Construye una respuesta de validación y, cuando corresponde,
    descuenta un intento de edición de forma transaccional.
    """
    if decrement_attempt:
        try:
            edit_status = (
                register_failed_profile_attempt(
                    user
                )
            )

        except ProfileEditServiceError as exc:
            payload = dict(
                errors
            )

            if isinstance(
                exc.detail,
                dict,
            ):
                payload.update(
                    exc.detail
                )

            else:
                payload["detail"] = (
                    exc.detail
                )

            return Response(
                payload,
                status=exc.status_code,
            )

    else:
        edit_status = (
            get_profile_edit_status(
                user
            )
        )

    payload = dict(
        errors
    )

    payload.update(
        _edit_status_payload(
            edit_status
        )
    )

    return Response(
        payload,
        status=status.HTTP_400_BAD_REQUEST,
    )


def _serialize_profile(
    *,
    user,
    request,
):
    """
    Serializa el perfil con el contexto necesario para construir
    la URL absoluta del avatar.
    """
    return ProfileSerializer(
        user,
        context={
            "request": request,
        },
    ).data


# ============================================================
# PERFIL
# ============================================================

class ProfileView(APIView):
    """
    Consulta y actualización del perfil autenticado.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    # ========================================================
    # CONSULTA
    # ========================================================

    def get(self, request):
        user = _get_current_user(
            request.user
        )

        if user is None:
            return Response(
                {
                    "detail": (
                        "No se encontró el usuario "
                        "autenticado."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            _serialize_profile(
                user=user,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def patch(self, request):
        """
        Actualiza el perfil dentro de una única transacción.

        Orden de ejecución:

        1. Bloquea la fila del usuario.
        2. Verifica el permiso de edición.
        3. Valida la información.
        4. Guarda el perfil.
        5. Recalcula la completitud.
        6. Sincroniza el autor relacionado.
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
                status=(
                    status.HTTP_401_UNAUTHORIZED
                ),
            )

        try:
            with transaction.atomic():
                locked_user = (
                    _profile_queryset()
                    .select_for_update()
                    .get(
                        pk=user_id
                    )
                )

                try:
                    ensure_profile_edit_allowed(
                        locked_user
                    )

                except ProfileEditServiceError as exc:
                    return Response(
                        exc.detail,
                        status=exc.status_code,
                    )

                serializer = (
                    ProfileUpdateSerializer(
                        locked_user,
                        data=request.data,
                        partial=True,
                        context={
                            "request": request,
                        },
                    )
                )

                if not serializer.is_valid():
                    return (
                        _build_validation_error_response(
                            user=locked_user,
                            errors=dict(
                                serializer.errors
                            ),
                            decrement_attempt=True,
                        )
                    )

                updated_user = serializer.save()

                updated_user = (
                    finalize_profile_update(
                        updated_user
                    )
                )

                asegurar_autor_para_usuario(
                    updated_user
                )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario autenticado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        except DjangoValidationError as exc:
            return _build_validation_error_response(
                user=request.user,
                errors=(
                    _django_validation_to_payload(
                        exc
                    )
                ),
                decrement_attempt=True,
            )

        except DRFValidationError as exc:
            error_payload = (
                exc.detail
                if isinstance(
                    exc.detail,
                    dict,
                )
                else {
                    "detail": exc.detail,
                }
            )

            return _build_validation_error_response(
                user=request.user,
                errors=error_payload,
                decrement_attempt=True,
            )

        except IntegrityError:
            logger.exception(
                (
                    "Conflicto de integridad al actualizar "
                    "el perfil del usuario %s."
                ),
                user_id,
            )

            current_user = (
                _get_current_user(
                    request.user
                )
                or request.user
            )

            edit_status = (
                get_profile_edit_status(
                    current_user
                )
            )

            payload = {
                "detail": (
                    "No se pudo actualizar el perfil "
                    "porque los datos entran en conflicto "
                    "con otro registro existente."
                )
            }

            payload.update(
                _edit_status_payload(
                    edit_status
                )
            )

            return Response(
                payload,
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        refreshed_user = (
            _get_current_user(
                request.user
            )
        )

        if refreshed_user is None:
            return Response(
                {
                    "detail": (
                        "El perfil se actualizó, pero no "
                        "fue posible volver a consultarlo."
                    )
                },
                status=(
                    status.HTTP_200_OK
                ),
            )

        return Response(
            _serialize_profile(
                user=refreshed_user,
                request=request,
            ),
            status=status.HTTP_200_OK,
        )


# ============================================================
# SOLICITUD DE EXTENSIÓN
# ============================================================

class ProfileEditExtensionRequestView(APIView):
    """
    Envía por correo una solicitud de extensión del periodo de
    edición.

    Esta vista no ejecuta ensure_profile_edit_allowed porque se
    utiliza precisamente cuando el plazo ha vencido o el perfil
    se encuentra bloqueado.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = (
            ProfileEditExtensionRequestSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = _get_current_user(
            request.user
        )

        if user is None:
            return Response(
                {
                    "detail": (
                        "No se encontró el usuario "
                        "autenticado."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        try:
            result = (
                send_profile_edit_extension_request(
                    user=user,
                    motivo=(
                        serializer.validated_data[
                            "motivo"
                        ]
                    ),
                    horas_solicitadas=(
                        serializer.validated_data[
                            "horas_solicitadas"
                        ]
                    ),
                    request=request,
                )
            )

        except ProfileExtensionRequestError as exc:
            return Response(
                exc.detail,
                status=exc.status_code,
            )

        return Response(
            {
                "detail": (
                    "La solicitud de extensión fue "
                    "enviada correctamente al "
                    "administrador."
                ),

                "email_sent": True,

                "sent_count": result.get(
                    "sent_count",
                    0,
                ),

                "requested_hours": result[
                    "requested_hours"
                ],

                "recipient_count": result[
                    "recipient_count"
                ],
            },
            status=status.HTTP_200_OK,
        )