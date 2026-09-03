"""
Utilidades para administrar el refresh token JWT mediante cookie HttpOnly.

Reglas de seguridad:

- El refresh token no se expone al JavaScript del frontend.
- La cookie se limita a las rutas de autenticación del API.
- La duración de la cookie sigue REFRESH_TOKEN_LIFETIME de SimpleJWT.
- La configuración Secure/SameSite puede adaptarse mediante settings.
- El access token continúa enviándose en el cuerpo de la respuesta.
"""

from django.conf import settings

from rest_framework_simplejwt.settings import api_settings


DEFAULT_REFRESH_COOKIE_NAME = "sgpc_refresh_token"
DEFAULT_REFRESH_COOKIE_PATH = "/api/auth/"
DEFAULT_REFRESH_COOKIE_SAMESITE = "Lax"


def _normalize_text(value):
    return str(value or "").strip()


def get_refresh_cookie_name():
    return (
        _normalize_text(
            getattr(
                settings,
                "AUTH_REFRESH_COOKIE_NAME",
                DEFAULT_REFRESH_COOKIE_NAME,
            )
        )
        or DEFAULT_REFRESH_COOKIE_NAME
    )


def get_refresh_cookie_path():
    return (
        _normalize_text(
            getattr(
                settings,
                "AUTH_REFRESH_COOKIE_PATH",
                DEFAULT_REFRESH_COOKIE_PATH,
            )
        )
        or DEFAULT_REFRESH_COOKIE_PATH
    )


def get_refresh_cookie_domain():
    value = _normalize_text(
        getattr(
            settings,
            "AUTH_REFRESH_COOKIE_DOMAIN",
            "",
        )
    )

    return value or None


def get_refresh_cookie_samesite():
    value = _normalize_text(
        getattr(
            settings,
            "AUTH_REFRESH_COOKIE_SAMESITE",
            DEFAULT_REFRESH_COOKIE_SAMESITE,
        )
    )

    if not value:
        return DEFAULT_REFRESH_COOKIE_SAMESITE

    normalized = value.lower()

    mapping = {
        "lax": "Lax",
        "strict": "Strict",
        "none": "None",
    }

    return mapping.get(
        normalized,
        DEFAULT_REFRESH_COOKIE_SAMESITE,
    )


def get_refresh_cookie_secure():
    return bool(
        getattr(
            settings,
            "AUTH_REFRESH_COOKIE_SECURE",
            not bool(
                getattr(
                    settings,
                    "DEBUG",
                    False,
                )
            ),
        )
    )


def get_refresh_cookie_max_age():
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME

    try:
        total_seconds = int(
            lifetime.total_seconds()
        )
    except (
        AttributeError,
        TypeError,
        ValueError,
        OverflowError,
    ):
        total_seconds = 0

    return max(
        1,
        total_seconds,
    )


def get_refresh_token_from_request(request):
    """
    Recupera el refresh token únicamente desde la cookie HttpOnly.

    JavaScript no necesita ni debe tener acceso al valor real.
    """
    if request is None:
        return ""

    cookies = getattr(
        request,
        "COOKIES",
        {},
    ) or {}

    return _normalize_text(
        cookies.get(
            get_refresh_cookie_name(),
            "",
        )
    )


def set_refresh_cookie(
    response,
    refresh_token,
):
    """
    Guarda el refresh token en una cookie HttpOnly.
    """
    token = _normalize_text(
        refresh_token
    )

    if response is None or not token:
        return response

    response.set_cookie(
        key=get_refresh_cookie_name(),
        value=token,
        max_age=get_refresh_cookie_max_age(),
        path=get_refresh_cookie_path(),
        domain=get_refresh_cookie_domain(),
        secure=get_refresh_cookie_secure(),
        httponly=True,
        samesite=get_refresh_cookie_samesite(),
    )

    return response


def delete_refresh_cookie(response):
    """
    Elimina del navegador la cookie del refresh token.
    """
    if response is None:
        return response

    response.delete_cookie(
        key=get_refresh_cookie_name(),
        path=get_refresh_cookie_path(),
        domain=get_refresh_cookie_domain(),
        samesite=get_refresh_cookie_samesite(),
    )

    return response
