"""
View de perfil del usuario autenticado.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth.serializers.auth_profile_read_serializers import ProfileSerializer
from core.auth.serializers.auth_profile_update_serializers import ProfileUpdateSerializer
from core.auth.services.auth_author_sync_services import asegurar_autor_para_usuario
from core.auth.services.auth_profile_services import (
    ProfileEditServiceError,
    ensure_profile_edit_allowed,
    register_failed_profile_attempt,
    finalize_profile_update,
)


def _django_validation_to_payload(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {"detail": exc.messages}

    return {"detail": str(exc)}


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(
            request.user,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user

        try:
            ensure_profile_edit_allowed(user)
        except ProfileEditServiceError as exc:
            return Response(exc.detail, status=exc.status_code)

        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            register_failed_profile_attempt(user)

            return Response(
                {
                    **serializer.errors,
                    "profile_edit_locked": getattr(user, "profile_edit_locked", False),
                    "attempts_left": getattr(user, "profile_edit_attempts_left", 0),
                    "profile_edit_until": getattr(user, "profile_edit_until", None),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()
            finalize_profile_update(user)
            asegurar_autor_para_usuario(user)
        except DjangoValidationError as exc:
            register_failed_profile_attempt(user)

            return Response(
                {
                    **_django_validation_to_payload(exc),
                    "profile_edit_locked": getattr(user, "profile_edit_locked", False),
                    "attempts_left": getattr(user, "profile_edit_attempts_left", 0),
                    "profile_edit_until": getattr(user, "profile_edit_until", None),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            register_failed_profile_attempt(user)

            return Response(
                {
                    "detail": "No se pudo actualizar el perfil por conflicto de unicidad.",
                    "profile_edit_locked": getattr(user, "profile_edit_locked", False),
                    "attempts_left": getattr(user, "profile_edit_attempts_left", 0),
                    "profile_edit_until": getattr(user, "profile_edit_until", None),
                },
                status=status.HTTP_409_CONFLICT,
            )

        user.refresh_from_db()

        response_serializer = ProfileSerializer(
            user,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)