"""
Views para recuperación de contraseña de usuarios externos locales.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth.serializers.auth_password_reset_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from core.models import PasswordResetToken

User = get_user_model()


def generic_ok():
    return Response(
        {
            "detail": (
                "Si el correo está registrado como usuario externo, "
                "recibirá instrucciones."
            )
        },
        status=status.HTTP_200_OK,
    )


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or ""


def throttle(key, limit, window_seconds):
    current = cache.get(key)

    if current is None:
        cache.set(key, 1, timeout=window_seconds)
        return True

    if int(current) >= limit:
        return False

    cache.incr(key)
    return True


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip().lower()
        ip = get_client_ip(request)

        if not throttle(f"pwreset:ip:{ip}", 5, 600):
            return generic_ok()

        if not throttle(f"pwreset:email:{email}", 3, 600):
            return generic_ok()

        user = User.objects.filter(email__iexact=email).first()

        if (
            not user
            or getattr(user, "auth_source", None) != "local"
            or getattr(user, "rol", None) != "autor_externo"
            or not getattr(user, "is_active", False)
        ):
            return generic_ok()

        raw_token = PasswordResetToken.create_for_user(user)

        frontend_url = getattr(
            settings,
            "FRONTEND_URL",
            "http://localhost:5173",
        ).rstrip("/")

        reset_link = f"{frontend_url}/reset-password?token={raw_token}"

        message = EmailMultiAlternatives(
            "Recuperación de contraseña — SGPC-FCVT",
            f"Enlace de recuperación:\n{reset_link}\n\nEste enlace expira en 1 hora.",
            getattr(settings, "DEFAULT_FROM_EMAIL", None),
            [email],
        )
        message.attach_alternative(
            render_to_string("emails/password_reset.html", {"reset_link": reset_link}),
            "text/html",
        )

        try:
            message.send(fail_silently=False)
        except Exception:
            return generic_ok()

        return generic_ok()


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_token = serializer.validated_data["token"].strip()
        new_password = serializer.validated_data["new_password"]

        reset = (
            PasswordResetToken.objects.select_related("user")
            .filter(token_hash=PasswordResetToken.hash_token(raw_token))
            .first()
        )

        if not reset:
            return Response(
                {"detail": "Token inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reset.is_used:
            return Response(
                {"detail": "Este token ya fue utilizado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reset.is_expired():
            return Response(
                {"detail": "El token ha expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = reset.user

        if (
            user.auth_source != "local"
            or user.rol != "autor_externo"
            or not user.is_active
        ):
            return Response(
                {"detail": "Operación no permitida."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            return Response(
                {"new_password": list(exc.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        reset.used_at = timezone.now()
        reset.save(update_fields=["used_at"])

        return Response(
            {"detail": "Contraseña actualizada correctamente."},
            status=status.HTTP_200_OK,
        )