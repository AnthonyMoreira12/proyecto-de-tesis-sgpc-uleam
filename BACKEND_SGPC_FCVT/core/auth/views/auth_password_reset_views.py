"""
Views para la recuperación de contraseña de usuarios externos.

Características:

- Mantiene respuestas genéricas para evitar enumerar usuarios.
- Aplica límites de frecuencia por correo e IP.
- Genera tokens de un solo uso.
- Elimina el token cuando el correo no puede enviarse.
- Confirma el cambio dentro de una transacción.
- Bloquea el token y el usuario durante la confirmación.
- Invalida otros tokens activos después del cambio.
- Impide recuperar contraseñas de cuentas Microsoft.
"""

import hashlib
import logging
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.cache import cache
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.core.mail import EmailMultiAlternatives
from django.db import DatabaseError, transaction
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth.serializers.auth_password_reset_serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)
from core.models import PasswordResetToken


User = get_user_model()

logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURACIÓN
# ============================================================

PASSWORD_RESET_IP_LIMIT = 5
PASSWORD_RESET_EMAIL_LIMIT = 3
PASSWORD_RESET_WINDOW_SECONDS = 600

PASSWORD_RESET_FRONTEND_PATH = "/reset-password"

LOCAL_AUTH_SOURCE = "local"
EXTERNAL_AUTHOR_ROLE = "autor_externo"


# ============================================================
# RESPUESTAS
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


def generic_ok():
    """
    Respuesta genérica para evitar revelar si el correo existe.
    """
    return _no_store_response(
        {
            "detail": (
                "Si el correo corresponde a una cuenta local "
                "habilitada, recibirá las instrucciones para "
                "restablecer su contraseña."
            )
        },
        status_code=status.HTTP_200_OK,
    )


def _invalid_token_response(message):
    """
    Respuesta controlada para tokens inválidos o vencidos.
    """
    return _no_store_response(
        {
            "detail": message,
        },
        status_code=status.HTTP_400_BAD_REQUEST,
    )


# ============================================================
# UTILIDADES DE RED Y CACHÉ
# ============================================================

def _normalize_text(value):
    return str(
        value or ""
    ).strip()


def _get_client_ip(request):
    """
    Obtiene la dirección IP.

    X-Forwarded-For solamente se utiliza cuando el proyecto
    habilita expresamente TRUST_X_FORWARDED_FOR.
    """
    trust_forwarded = bool(
        getattr(
            settings,
            "TRUST_X_FORWARDED_FOR",
            False,
        )
    )

    if trust_forwarded:
        forwarded_for = _normalize_text(
            request.META.get(
                "HTTP_X_FORWARDED_FOR"
            )
        )

        if forwarded_for:
            return (
                forwarded_for
                .split(",")[0]
                .strip()
            )

    return (
        _normalize_text(
            request.META.get(
                "REMOTE_ADDR"
            )
        )
        or "unknown"
    )


def _cache_identifier(value):
    """
    Evita almacenar correos o direcciones IP directamente
    dentro de las claves del sistema de caché.
    """
    normalized = _normalize_text(
        value
    ).lower()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def _rate_limit_allowed(
    *,
    namespace,
    identifier,
    limit,
    window_seconds,
):
    """
    Incrementa un contador de frecuencia.

    cache.add() e incr() son operaciones atómicas en los
    backends habituales como Redis y Memcached.
    """
    cache_key = (
        f"auth:password-reset:{namespace}:"
        f"{_cache_identifier(identifier)}"
    )

    if cache.add(
        cache_key,
        1,
        timeout=window_seconds,
    ):
        return True

    try:
        current = cache.incr(
            cache_key
        )

    except (
        ValueError,
        TypeError,
        NotImplementedError,
    ):
        current = int(
            cache.get(
                cache_key,
                0,
            )
            or 0
        ) + 1

        cache.set(
            cache_key,
            current,
            timeout=window_seconds,
        )

    return current <= limit


# ============================================================
# UTILIDADES DE CORREO
# ============================================================

def _build_reset_link(raw_token):
    """
    Construye el enlace del frontend.

    La ruta puede sobrescribirse mediante:

    PASSWORD_RESET_FRONTEND_PATH
    """
    frontend_url = _normalize_text(
        getattr(
            settings,
            "FRONTEND_URL",
            "http://localhost:5173",
        )
    ).rstrip("/")

    reset_path = _normalize_text(
        getattr(
            settings,
            "PASSWORD_RESET_FRONTEND_PATH",
            PASSWORD_RESET_FRONTEND_PATH,
        )
    )

    if not reset_path.startswith("/"):
        reset_path = f"/{reset_path}"

    encoded_token = quote(
        raw_token,
        safe="",
    )

    return (
        f"{frontend_url}{reset_path}"
        f"?token={encoded_token}"
    )


def _build_reset_html(reset_link):
    """
    Renderiza la plantilla HTML cuando existe.

    El correo de texto plano continúa funcionando aunque la
    plantilla no esté instalada.
    """
    try:
        return render_to_string(
            "emails/password_reset.html",
            {
                "reset_link": reset_link,
            },
        )

    except TemplateDoesNotExist:
        logger.warning(
            (
                "No se encontró la plantilla "
                "emails/password_reset.html. "
                "Se enviará únicamente texto plano."
            )
        )

        return None


def _send_reset_email(
    *,
    recipient,
    reset_link,
):
    """
    Envía el correo y retorna la cantidad aceptada por el
    backend configurado.
    """
    from_email = (
        _normalize_text(
            getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                None,
            )
        )
        or _normalize_text(
            getattr(
                settings,
                "EMAIL_HOST_USER",
                None,
            )
        )
        or None
    )

    subject = (
        "Recuperación de contraseña — SGPC ULEAM"
    )

    text_body = (
        "Se solicitó el restablecimiento de la contraseña "
        "de su cuenta en SGPC ULEAM.\n\n"
        f"Utilice el siguiente enlace:\n{reset_link}\n\n"
        "El enlace expira en una hora y solo puede "
        "utilizarse una vez.\n\n"
        "Si usted no realizó esta solicitud, ignore "
        "este mensaje."
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[recipient],
    )

    html_body = _build_reset_html(
        reset_link
    )

    if html_body:
        message.attach_alternative(
            html_body,
            "text/html",
        )

    return message.send(
        fail_silently=False
    )


# ============================================================
# SOLICITUD DE RECUPERACIÓN
# ============================================================

class PasswordResetRequestView(APIView):
    """
    Solicita un enlace de recuperación.

    La respuesta es deliberadamente idéntica cuando:

    - El correo no existe.
    - La cuenta pertenece a Microsoft.
    - El usuario no es externo.
    - La cuenta está inactiva.
    - Se supera el límite de frecuencia.
    - El servidor de correo falla.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = (
            PasswordResetRequestSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data[
            "email"
        ]

        client_ip = _get_client_ip(
            request
        )

        ip_allowed = _rate_limit_allowed(
            namespace="ip",
            identifier=client_ip,
            limit=int(
                getattr(
                    settings,
                    "PASSWORD_RESET_IP_LIMIT",
                    PASSWORD_RESET_IP_LIMIT,
                )
            ),
            window_seconds=int(
                getattr(
                    settings,
                    "PASSWORD_RESET_WINDOW_SECONDS",
                    PASSWORD_RESET_WINDOW_SECONDS,
                )
            ),
        )

        email_allowed = _rate_limit_allowed(
            namespace="email",
            identifier=email,
            limit=int(
                getattr(
                    settings,
                    "PASSWORD_RESET_EMAIL_LIMIT",
                    PASSWORD_RESET_EMAIL_LIMIT,
                )
            ),
            window_seconds=int(
                getattr(
                    settings,
                    "PASSWORD_RESET_WINDOW_SECONDS",
                    PASSWORD_RESET_WINDOW_SECONDS,
                )
            ),
        )

        if not ip_allowed or not email_allowed:
            return generic_ok()

        user = (
            User.objects
            .filter(
                email__iexact=email
            )
            .first()
        )

        if user is None:
            return generic_ok()

        auth_source = _normalize_text(
            getattr(
                user,
                "auth_source",
                "",
            )
        ).lower()

        role = _normalize_text(
            getattr(
                user,
                "rol",
                "",
            )
        ).lower()

        is_eligible = bool(
            auth_source == LOCAL_AUTH_SOURCE
            and role == EXTERNAL_AUTHOR_ROLE
            and getattr(
                user,
                "is_active",
                False,
            )
        )

        if not is_eligible:
            return generic_ok()

        raw_token = (
            PasswordResetToken.create_for_user(
                user
            )
        )

        token_hash = (
            PasswordResetToken.hash_token(
                raw_token
            )
        )

        reset_link = _build_reset_link(
            raw_token
        )

        try:
            sent_count = _send_reset_email(
                recipient=email,
                reset_link=reset_link,
            )

            if sent_count < 1:
                raise RuntimeError(
                    (
                        "El backend de correo no confirmó "
                        "el envío."
                    )
                )

        except Exception:
            logger.exception(
                (
                    "No se pudo enviar el correo de "
                    "recuperación al Usuario %s."
                ),
                user.pk,
            )

            # El token no debe permanecer activo si el correo
            # nunca llegó a enviarse.
            PasswordResetToken.objects.filter(
                token_hash=token_hash,
                used_at__isnull=True,
            ).delete()

            return generic_ok()

        return generic_ok()


# ============================================================
# CONFIRMACIÓN DE RECUPERACIÓN
# ============================================================

class PasswordResetConfirmView(APIView):
    """
    Confirma el cambio de contraseña mediante un token válido.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = (
            PasswordResetConfirmSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        raw_token = serializer.validated_data[
            "token"
        ]

        new_password = serializer.validated_data[
            "new_password"
        ]

        token_hash = (
            PasswordResetToken.hash_token(
                raw_token
            )
        )

        try:
            with transaction.atomic():
                reset_token = (
                    PasswordResetToken.objects
                    .select_for_update()
                    .select_related("user")
                    .filter(
                        token_hash=token_hash
                    )
                    .first()
                )

                if reset_token is None:
                    return _invalid_token_response(
                        (
                            "El enlace de recuperación "
                            "no es válido."
                        )
                    )

                if reset_token.is_used:
                    return _invalid_token_response(
                        (
                            "Este enlace de recuperación "
                            "ya fue utilizado."
                        )
                    )

                if reset_token.is_expired():
                    return _invalid_token_response(
                        (
                            "El enlace de recuperación "
                            "ha expirado."
                        )
                    )

                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=reset_token.user_id
                    )
                )

                auth_source = _normalize_text(
                    getattr(
                        user,
                        "auth_source",
                        "",
                    )
                ).lower()

                role = _normalize_text(
                    getattr(
                        user,
                        "rol",
                        "",
                    )
                ).lower()

                if (
                    auth_source != LOCAL_AUTH_SOURCE
                    or role != EXTERNAL_AUTHOR_ROLE
                    or not getattr(
                        user,
                        "is_active",
                        False,
                    )
                ):
                    return _no_store_response(
                        {
                            "detail": (
                                "La recuperación de contraseña "
                                "no está disponible para esta "
                                "cuenta."
                            )
                        },
                        status_code=(
                            status.HTTP_403_FORBIDDEN
                        ),
                    )

                try:
                    validate_password(
                        new_password,
                        user=user,
                    )

                except DjangoValidationError as exc:
                    return _no_store_response(
                        {
                            "new_password": list(
                                exc.messages
                            )
                        },
                        status_code=(
                            status.HTTP_400_BAD_REQUEST
                        ),
                    )

                user.set_password(
                    new_password
                )

                user.save(
                    update_fields=[
                        "password",
                    ]
                )

                current_time = timezone.now()

                reset_token.used_at = current_time

                reset_token.save(
                    update_fields=[
                        "used_at",
                    ]
                )

                # Se invalidan otras solicitudes activas del
                # mismo usuario.
                (
                    PasswordResetToken.objects
                    .filter(
                        user_id=user.pk,
                        used_at__isnull=True,
                    )
                    .exclude(
                        pk=reset_token.pk
                    )
                    .update(
                        used_at=current_time
                    )
                )

        except User.DoesNotExist:
            return _invalid_token_response(
                (
                    "El usuario asociado al enlace "
                    "ya no existe."
                )
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al confirmar "
                    "una recuperación de contraseña."
                )
            )

            return _no_store_response(
                {
                    "detail": (
                        "No fue posible actualizar la "
                        "contraseña debido a un error temporal."
                    )
                },
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return _no_store_response(
            {
                "detail": (
                    "La contraseña fue actualizada "
                    "correctamente."
                )
            },
            status_code=status.HTTP_200_OK,
        )