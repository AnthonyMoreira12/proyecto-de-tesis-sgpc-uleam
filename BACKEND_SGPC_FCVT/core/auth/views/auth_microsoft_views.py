"""
Views para autenticación mediante Microsoft 365.

Flujo implementado:

1. MicrosoftLoginView
   - Genera un state criptográficamente seguro.
   - Lo registra temporalmente en caché.
   - Redirige al usuario hacia Microsoft.

2. MicrosoftCallbackView
   - Valida y consume el state.
   - Intercambia el código OAuth.
   - Consulta Microsoft Graph.
   - Resuelve y sincroniza el usuario institucional.
   - Genera un código temporal de intercambio.
   - Nunca incluye tokens JWT en la URL.

3. MicrosoftExchangeView
   - Consume el código temporal.
   - Recupera al usuario sincronizado.
   - Genera la sesión JWT.
   - Entrega los tokens al frontend.

Los códigos temporales son de un solo uso y se almacenan en
caché mediante claves hash para no exponer sus valores.
"""

import hashlib
import logging
import secrets
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import DatabaseError
from django.http import HttpResponseRedirect
from django.utils import timezone

from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth.services.auth_microsoft_services import (
    MicrosoftAuthServiceError,
    build_microsoft_auth_payload,
    build_microsoft_authorization_url,
    exchange_microsoft_authorization_code,
    fetch_graph_profile,
    is_allowed_institutional_email,
    resolve_microsoft_identity,
    sync_microsoft_user,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

DEFAULT_FRONTEND_URL = "http://localhost:5173"
DEFAULT_FRONTEND_LOGIN_PATH = "/login"

DEFAULT_STATE_TTL_SECONDS = 300
DEFAULT_EXCHANGE_CODE_TTL_SECONDS = 120

MIN_TEMPORARY_TTL_SECONDS = 30
MAX_TEMPORARY_TTL_SECONDS = 900

MAX_EXCHANGE_CODE_LENGTH = 512

MICROSOFT_AUTH_SOURCE = "microsoft"


# ============================================================
# SERIALIZER
# ============================================================

class MicrosoftExchangeSerializer(serializers.Serializer):
    """
    Valida el código temporal recibido por el frontend.

    Este código no es el código OAuth de Microsoft. Es un código
    interno de un solo uso generado por el backend después de
    completar correctamente el callback.
    """

    code = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        min_length=32,
        max_length=MAX_EXCHANGE_CODE_LENGTH,
        write_only=True,
        error_messages={
            "required": (
                "El código de intercambio es obligatorio."
            ),
            "blank": (
                "El código de intercambio es obligatorio."
            ),
            "min_length": (
                "El código de intercambio no es válido."
            ),
            "max_length": (
                "El código de intercambio no es válido."
            ),
        },
    )

    def validate_code(self, value):
        normalized_code = str(
            value or ""
        ).strip()

        if not normalized_code:
            raise serializers.ValidationError(
                "El código de intercambio es obligatorio."
            )

        allowed_characters = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789-_"
        )

        if any(
            character not in allowed_characters
            for character in normalized_code
        ):
            raise serializers.ValidationError(
                "El código de intercambio no es válido."
            )

        return normalized_code


# ============================================================
# UTILIDADES GENERALES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _safe_ttl(
    setting_name,
    default,
):
    """
    Obtiene un tiempo de vida temporal dentro de límites
    seguros.
    """
    configured = getattr(
        settings,
        setting_name,
        default,
    )

    try:
        ttl = int(
            configured
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        ttl = int(
            default
        )

    return max(
        MIN_TEMPORARY_TTL_SECONDS,
        min(
            ttl,
            MAX_TEMPORARY_TTL_SECONDS,
        ),
    )


def _state_ttl():
    return _safe_ttl(
        "MICROSOFT_STATE_TTL_SECONDS",
        DEFAULT_STATE_TTL_SECONDS,
    )


def _exchange_code_ttl():
    return _safe_ttl(
        "MICROSOFT_EXCHANGE_CODE_TTL_SECONDS",
        DEFAULT_EXCHANGE_CODE_TTL_SECONDS,
    )


def _cache_key(
    namespace,
    raw_value,
):
    """
    Construye una clave de caché sin almacenar directamente el
    state o código temporal.

    Esto evita que secretos temporales aparezcan en herramientas
    de administración o monitoreo del backend de caché.
    """
    normalized_value = _normalize_text(
        raw_value
    )

    digest = hashlib.sha256(
        normalized_value.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        f"auth:microsoft:{namespace}:"
        f"{digest}"
    )


def _store_temporary_value(
    *,
    namespace,
    raw_key,
    value,
    ttl,
):
    """
    Registra un valor temporal evitando sobrescribir una clave
    existente.

    Retorna True cuando se almacenó correctamente.
    """
    key = _cache_key(
        namespace,
        raw_key,
    )

    return bool(
        cache.add(
            key,
            value,
            timeout=ttl,
        )
    )


def _consume_temporary_value(
    *,
    namespace,
    raw_key,
    ttl,
):
    """
    Consume un valor temporal una sola vez.

    Se utiliza una marca atómica adicional para impedir que dos
    solicitudes concurrentes utilicen el mismo state o código.
    """
    key = _cache_key(
        namespace,
        raw_key,
    )

    value = cache.get(
        key
    )

    if value is None:
        return None

    consumed_key = (
        f"{key}:consumed"
    )

    first_consumer = cache.add(
        consumed_key,
        True,
        timeout=ttl,
    )

    if not first_consumer:
        return None

    cache.delete(
        key
    )

    return value


def _generate_temporary_secret(
    *,
    namespace,
    payload,
    ttl,
):
    """
    Genera un secreto temporal único y lo registra en caché.
    """
    for _attempt in range(5):
        raw_secret = secrets.token_urlsafe(
            48
        )

        stored = _store_temporary_value(
            namespace=namespace,
            raw_key=raw_secret,
            value=payload,
            ttl=ttl,
        )

        if stored:
            return raw_secret

    raise MicrosoftAuthServiceError(
        {
            "detail": (
                "No fue posible generar un código temporal "
                "de autenticación."
            )
        },
        status_code=(
            status.HTTP_503_SERVICE_UNAVAILABLE
        ),
    )


# ============================================================
# URL DEL FRONTEND
# ============================================================

def _frontend_base_url():
    """
    Obtiene y valida la URL base del frontend.
    """
    frontend_url = _normalize_text(
        getattr(
            settings,
            "FRONTEND_URL",
            DEFAULT_FRONTEND_URL,
        )
    ).rstrip("/")

    parsed = urlsplit(
        frontend_url
    )

    if (
        parsed.scheme not in {
            "http",
            "https",
        }
        or not parsed.netloc
    ):
        logger.error(
            "FRONTEND_URL no contiene una URL válida."
        )

        return DEFAULT_FRONTEND_URL

    return frontend_url


def _frontend_login_path():
    """
    Obtiene la ruta de inicio de sesión del frontend.
    """
    login_path = _normalize_text(
        getattr(
            settings,
            "MICROSOFT_FRONTEND_LOGIN_PATH",
            DEFAULT_FRONTEND_LOGIN_PATH,
        )
    )

    if not login_path:
        login_path = DEFAULT_FRONTEND_LOGIN_PATH

    if not login_path.startswith("/"):
        login_path = (
            f"/{login_path}"
        )

    return login_path


def _frontend_login_url(
    **query_params,
):
    """
    Construye la URL de retorno codificando correctamente los
    parámetros.
    """
    base_url = (
        f"{_frontend_base_url()}"
        f"{_frontend_login_path()}"
    )

    clean_params = {
        key: value
        for key, value in query_params.items()
        if value not in (
            None,
            "",
        )
    }

    if not clean_params:
        return base_url

    return (
        f"{base_url}?"
        f"{urlencode(clean_params)}"
    )


def _redirect_to_frontend(
    **query_params,
):
    """
    Crea una redirección que no debe almacenarse en caché.
    """
    response = HttpResponseRedirect(
        _frontend_login_url(
            **query_params
        )
    )

    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate"
    )
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


def _redirect_with_error(
    *,
    error_code,
    message,
):
    """
    Redirige al login del frontend con un error controlado.

    Nunca envía mensajes internos de Microsoft, Django o
    PostgreSQL.
    """
    return _redirect_to_frontend(
        ms_error=message,
        ms_error_code=error_code,
    )


# ============================================================
# RESPUESTAS DE API
# ============================================================

def _no_store_response(
    payload,
    *,
    status_code,
):
    """
    Construye una respuesta JSON que no puede almacenarse en
    caché.
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


# ============================================================
# CONSULTA DEL USUARIO
# ============================================================

def _get_microsoft_user(user_id):
    """
    Recupera al usuario Microsoft con su relación académica.
    """
    if not user_id:
        return None

    return (
        User.objects
        .select_related(
            "carrera",
            "carrera__facultad",
        )
        .filter(
            pk=user_id,
            auth_source=MICROSOFT_AUTH_SOURCE,
        )
        .first()
    )


# ============================================================
# LOGIN MICROSOFT
# ============================================================

class MicrosoftLoginView(APIView):
    """
    Inicia el flujo OAuth con Microsoft.

    El endpoint es público porque todavía no existe una sesión
    local autenticada.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request):
        state_ttl = _state_ttl()

        try:
            state = _generate_temporary_secret(
                namespace="state",
                payload={
                    "created_at": (
                        timezone.now().isoformat()
                    ),
                },
                ttl=state_ttl,
            )

            authorization_url = (
                build_microsoft_authorization_url(
                    state=state
                )
            )

        except MicrosoftAuthServiceError as exc:
            logger.error(
                (
                    "No se pudo iniciar la autenticación "
                    "Microsoft: %s"
                ),
                exc.detail,
            )

            return _redirect_with_error(
                error_code="configuration_error",
                message=(
                    "No fue posible iniciar sesión con "
                    "Microsoft en este momento."
                ),
            )

        response = HttpResponseRedirect(
            authorization_url
        )

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate"
        )
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response


# ============================================================
# CALLBACK MICROSOFT
# ============================================================

class MicrosoftCallbackView(APIView):
    """
    Procesa el callback enviado por Microsoft.

    Los tokens JWT nunca se colocan en la URL. La redirección al
    frontend contiene únicamente un código interno de un solo
    uso.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request):
        microsoft_error = _normalize_text(
            request.GET.get(
                "error"
            )
        )

        if microsoft_error:
            logger.warning(
                (
                    "Microsoft canceló o rechazó el flujo "
                    "OAuth con error %s."
                ),
                microsoft_error,
            )

            return _redirect_with_error(
                error_code="microsoft_rejected",
                message=(
                    "Microsoft canceló o rechazó "
                    "el inicio de sesión."
                ),
            )

        authorization_code = _normalize_text(
            request.GET.get(
                "code"
            )
        )

        state = _normalize_text(
            request.GET.get(
                "state"
            )
        )

        if not authorization_code or not state:
            return _redirect_with_error(
                error_code="missing_parameters",
                message=(
                    "La respuesta de Microsoft está "
                    "incompleta."
                ),
            )

        stored_state = (
            _consume_temporary_value(
                namespace="state",
                raw_key=state,
                ttl=_state_ttl(),
            )
        )

        if stored_state is None:
            return _redirect_with_error(
                error_code="invalid_state",
                message=(
                    "La solicitud de autenticación expiró "
                    "o ya fue utilizada."
                ),
            )

        try:
            token_result = (
                exchange_microsoft_authorization_code(
                    code=authorization_code
                )
            )

        except MicrosoftAuthServiceError:
            logger.exception(
                (
                    "No se pudo intercambiar el código "
                    "OAuth de Microsoft."
                )
            )

            return _redirect_with_error(
                error_code="token_exchange_failed",
                message=(
                    "Microsoft no pudo completar "
                    "la autenticación."
                ),
            )

        if (
            not isinstance(
                token_result,
                dict,
            )
            or token_result.get(
                "error"
            )
        ):
            error_code = (
                token_result.get(
                    "error",
                    "unknown_error",
                )
                if isinstance(
                    token_result,
                    dict,
                )
                else "invalid_response"
            )

            correlation_id = (
                token_result.get(
                    "correlation_id"
                )
                if isinstance(
                    token_result,
                    dict,
                )
                else None
            )

            logger.warning(
                (
                    "Microsoft rechazó el intercambio OAuth. "
                    "Error=%s CorrelationId=%s"
                ),
                error_code,
                correlation_id,
            )

            return _redirect_with_error(
                error_code="token_exchange_failed",
                message=(
                    "Microsoft no pudo completar "
                    "la autenticación."
                ),
            )

        claims = token_result.get(
            "id_token_claims"
        ) or {}

        access_token = token_result.get(
            "access_token"
        )

        graph_profile = (
            fetch_graph_profile(
                access_token
            )
            if access_token
            else {
                "_error": (
                    "missing_access_token"
                )
            }
        )

        identity = resolve_microsoft_identity(
            claims=claims,
            graph=graph_profile,
        )

        if identity is None:
            return _redirect_with_error(
                error_code="invalid_identity",
                message=(
                    "Microsoft no proporcionó una "
                    "identidad válida."
                ),
            )

        if not is_allowed_institutional_email(
            identity["email"]
        ):
            logger.warning(
                (
                    "Se rechazó un correo Microsoft no "
                    "autorizado."
                )
            )

            return _redirect_with_error(
                error_code="institutional_email_required",
                message=(
                    "Debe utilizar una cuenta institucional "
                    "autorizada."
                ),
            )

        try:
            user = sync_microsoft_user(
                User,
                identity=identity,
                claims=claims,
                graph=graph_profile,
            )

        except MicrosoftAuthServiceError as exc:
            logger.warning(
                (
                    "No fue posible sincronizar la cuenta "
                    "Microsoft. Estado=%s Detalle=%s"
                ),
                exc.status_code,
                exc.detail,
            )

            if (
                exc.status_code
                == status.HTTP_409_CONFLICT
            ):
                return _redirect_with_error(
                    error_code="account_conflict",
                    message=(
                        "La cuenta Microsoft entra en "
                        "conflicto con un usuario existente. "
                        "Solicite una revisión al administrador."
                    ),
                )

            if (
                exc.status_code
                == status.HTTP_403_FORBIDDEN
            ):
                return _redirect_with_error(
                    error_code="access_denied",
                    message=(
                        "La cuenta Microsoft no está "
                        "autorizada para acceder."
                    ),
                )

            return _redirect_with_error(
                error_code="account_sync_failed",
                message=(
                    "No fue posible sincronizar su cuenta "
                    "institucional."
                ),
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al sincronizar "
                    "una cuenta Microsoft."
                )
            )

            return _redirect_with_error(
                error_code="database_unavailable",
                message=(
                    "El sistema no pudo completar el inicio "
                    "de sesión por un error temporal."
                ),
            )

        if user is None or not getattr(
            user,
            "pk",
            None,
        ):
            return _redirect_with_error(
                error_code="user_not_created",
                message=(
                    "No fue posible crear o recuperar "
                    "el usuario institucional."
                ),
            )

        if not bool(
            getattr(
                user,
                "is_active",
                False,
            )
        ):
            return _redirect_with_error(
                error_code="inactive_account",
                message=(
                    "La cuenta institucional se encuentra "
                    "inactiva."
                ),
            )

        try:
            one_time_code = (
                _generate_temporary_secret(
                    namespace="exchange",
                    payload={
                        "user_id": user.pk,
                        "created_at": (
                            timezone.now().isoformat()
                        ),
                    },
                    ttl=_exchange_code_ttl(),
                )
            )

        except MicrosoftAuthServiceError:
            logger.exception(
                (
                    "No se pudo generar el código de "
                    "intercambio Microsoft."
                )
            )

            return _redirect_with_error(
                error_code="exchange_code_failed",
                message=(
                    "La autenticación se completó, pero no "
                    "fue posible crear la sesión."
                ),
            )

        return _redirect_to_frontend(
            ms_code=one_time_code
        )


# ============================================================
# INTERCAMBIO POR JWT
# ============================================================

class MicrosoftExchangeView(APIView):
    """
    Intercambia el código interno de un solo uso por la sesión
    JWT del usuario Microsoft.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = MicrosoftExchangeSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        if not serializer.is_valid():
            return _no_store_response(
                serializer.errors,
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        one_time_code = (
            serializer.validated_data[
                "code"
            ]
        )

        exchange_data = (
            _consume_temporary_value(
                namespace="exchange",
                raw_key=one_time_code,
                ttl=_exchange_code_ttl(),
            )
        )

        if not isinstance(
            exchange_data,
            dict,
        ):
            return _no_store_response(
                {
                    "detail": (
                        "El código de autenticación es "
                        "inválido, expiró o ya fue utilizado."
                    )
                },
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
            )

        user_id = exchange_data.get(
            "user_id"
        )

        user = _get_microsoft_user(
            user_id
        )

        if user is None:
            return _no_store_response(
                {
                    "detail": (
                        "La cuenta Microsoft asociada ya "
                        "no está disponible."
                    )
                },
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
            )

        if not bool(
            getattr(
                user,
                "is_active",
                False,
            )
        ):
            return _no_store_response(
                {
                    "detail": (
                        "La cuenta institucional se "
                        "encuentra inactiva."
                    )
                },
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        try:
            payload = build_microsoft_auth_payload(
                user,
                request=request,
            )

        except MicrosoftAuthServiceError as exc:
            return _no_store_response(
                exc.detail
                if isinstance(
                    exc.detail,
                    dict,
                )
                else {
                    "detail": exc.detail,
                },
                status_code=exc.status_code,
            )

        return _no_store_response(
            payload,
            status_code=status.HTTP_200_OK,
        )