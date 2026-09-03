"""
Configuración principal de Django para SGPC ULEAM.

Incluye:

- Seguridad general.
- PostgreSQL.
- Django REST Framework.
- JWT y revocación de refresh tokens.
- CORS y CSRF.
- Microsoft Entra ID.
- Redis o caché local.
- Correo SMTP.
- Recuperación de contraseña.
- Solicitudes de extensión del perfil.
- Logs estructurados.
"""

import os
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# ============================================================
# BASE Y VARIABLES DE ENTORNO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env"
)


def env_bool(
    name,
    default=False,
):
    """
    Convierte una variable de entorno en booleano.
    """
    value = os.getenv(
        name,
        str(default),
    )

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "si",
        "sí",
    }


def env_int(
    name,
    default,
    *,
    minimum=None,
    maximum=None,
):
    """
    Convierte una variable de entorno en entero seguro.
    """
    raw_value = os.getenv(
        name,
        str(default),
    )

    try:
        value = int(
            str(raw_value).strip()
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        value = int(default)

    if minimum is not None:
        value = max(
            int(minimum),
            value,
        )

    if maximum is not None:
        value = min(
            int(maximum),
            value,
        )

    return value


def env_list(
    name,
    default="",
    *,
    lowercase=False,
):
    """
    Convierte una variable separada por comas o punto y coma
    en una lista limpia y sin duplicados.
    """
    raw_value = os.getenv(
        name,
        default,
    )

    if raw_value is None:
        return []

    normalized_items = []

    for item in (
        str(raw_value)
        .replace(";", ",")
        .split(",")
    ):
        normalized = item.strip()

        if not normalized:
            continue

        if lowercase:
            normalized = normalized.lower()

        if normalized not in normalized_items:
            normalized_items.append(
                normalized
            )

    return normalized_items


# ============================================================
# SEGURIDAD GENERAL
# ============================================================

DEBUG = env_bool(
    "DJANGO_DEBUG",
    False,
)

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "",
).strip()

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = (
            "django-insecure-development-only-change-me"
        )
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY es obligatoria cuando "
            "DJANGO_DEBUG está desactivado."
        )

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)

APPEND_SLASH = True

X_FRAME_OPTIONS = "DENY"

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = (
    "strict-origin-when-cross-origin"
)

SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    False,
)

SESSION_COOKIE_SECURE = env_bool(
    "DJANGO_SESSION_COOKIE_SECURE",
    not DEBUG,
)

CSRF_COOKIE_SECURE = env_bool(
    "DJANGO_CSRF_COOKIE_SECURE",
    not DEBUG,
)

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"

SECURE_HSTS_SECONDS = env_int(
    "DJANGO_SECURE_HSTS_SECONDS",
    0,
    minimum=0,
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    False,
)

SECURE_HSTS_PRELOAD = env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD",
    False,
)


# ============================================================
# PROXY INVERSO
# ============================================================

TRUST_X_FORWARDED_FOR = env_bool(
    "TRUST_X_FORWARDED_FOR",
    False,
)

USE_X_FORWARDED_HOST = env_bool(
    "USE_X_FORWARDED_HOST",
    False,
)

TRUST_X_FORWARDED_PROTO = env_bool(
    "TRUST_X_FORWARDED_PROTO",
    False,
)

if TRUST_X_FORWARDED_PROTO:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


# ============================================================
# APLICACIONES INSTALADAS
# ============================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Proyecto
    "core.apps.CoreConfig",

    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
]


# ============================================================
# MODELO DE USUARIO
# ============================================================

AUTH_USER_MODEL = "core.Usuario"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.auditoria.middleware.AuditoriaRequestContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URLS Y WSGI
# ============================================================

ROOT_URLCONF = "BACKEND_SGPC_FCVT.urls"

WSGI_APPLICATION = (
    "BACKEND_SGPC_FCVT.wsgi.application"
)


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "debug"
                ),
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth.context_processors."
                    "auth"
                ),
                (
                    "django.contrib.messages.context_processors."
                    "messages"
                ),
            ],
        },
    },
]


# ============================================================
# BASE DE DATOS POSTGRESQL
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.postgresql"
        ),
        "NAME": os.getenv(
            "DB_NAME",
            "SGPC_FCVT_2",
        ).strip(),
        "USER": os.getenv(
            "DB_USER",
            "postgres",
        ).strip(),
        "PASSWORD": os.getenv(
            "DB_PASSWORD",
            "",
        ).strip(),
        "HOST": os.getenv(
            "DB_HOST",
            "127.0.0.1",
        ).strip(),
        "PORT": os.getenv(
            "DB_PORT",
            "5432",
        ).strip(),
        "CONN_MAX_AGE": env_int(
            "DB_CONN_MAX_AGE",
            60,
            minimum=0,
            maximum=3600,
        ),
    }
}

DB_SSLMODE = os.getenv(
    "DB_SSLMODE",
    "",
).strip()

if DB_SSLMODE:
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": DB_SSLMODE,
    }


# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNACIONALIZACIÓN
# ============================================================

LANGUAGE_CODE = "es-ec"

TIME_ZONE = "America/Guayaquil"

USE_I18N = True

USE_TZ = True


# ============================================================
# ARCHIVOS ESTÁTICOS
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# ARCHIVOS MULTIMEDIA
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = (
    5 * 1024 * 1024
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    15 * 1024 * 1024
)


# ============================================================
# LLAVE PRIMARIA POR DEFECTO
# ============================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        (
            "rest_framework_simplejwt.authentication."
            "JWTAuthentication"
        ),
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        (
            "rest_framework.permissions."
            "IsAuthenticated"
        ),
    ),
    "DEFAULT_PARSER_CLASSES": (
        (
            "rest_framework.parsers."
            "JSONParser"
        ),
        (
            "rest_framework.parsers."
            "FormParser"
        ),
        (
            "rest_framework.parsers."
            "MultiPartParser"
        ),
    ),
}


# ============================================================
# SIMPLEJWT
# ============================================================

# ============================================================
# COOKIE HTTPONLY DEL REFRESH JWT
# ============================================================

AUTH_REFRESH_COOKIE_NAME = (
    os.getenv(
        "AUTH_REFRESH_COOKIE_NAME",
        "sgpc_refresh_token",
    ).strip()
    or "sgpc_refresh_token"
)

AUTH_REFRESH_COOKIE_PATH = (
    os.getenv(
        "AUTH_REFRESH_COOKIE_PATH",
        "/api/auth/",
    ).strip()
    or "/api/auth/"
)

AUTH_REFRESH_COOKIE_DOMAIN = (
    os.getenv(
        "AUTH_REFRESH_COOKIE_DOMAIN",
        "",
    ).strip()
    or None
)

AUTH_REFRESH_COOKIE_SECURE = env_bool(
    "AUTH_REFRESH_COOKIE_SECURE",
    not DEBUG,
)

AUTH_REFRESH_COOKIE_SAMESITE = (
    os.getenv(
        "AUTH_REFRESH_COOKIE_SAMESITE",
        "Lax",
    ).strip()
    or "Lax"
)

if (
    AUTH_REFRESH_COOKIE_SAMESITE.lower()
    not in {
        "lax",
        "strict",
        "none",
    }
):
    raise ImproperlyConfigured(
        "AUTH_REFRESH_COOKIE_SAMESITE debe ser "
        "Lax, Strict o None."
    )

if (
    AUTH_REFRESH_COOKIE_SAMESITE.lower()
    == "none"
    and not AUTH_REFRESH_COOKIE_SECURE
):
    raise ImproperlyConfigured(
        "AUTH_REFRESH_COOKIE_SECURE debe estar activo "
        "cuando AUTH_REFRESH_COOKIE_SAMESITE=None."
    )


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env_int(
            "JWT_ACCESS_MINUTES",
            30,
            minimum=1,
            maximum=1440,
        )
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(
        hours=env_int(
            "JWT_REFRESH_HOURS",
            8,
            minimum=1,
            maximum=720,
        )
    ),

    "ROTATE_REFRESH_TOKENS": env_bool(
        "JWT_ROTATE_REFRESH_TOKENS",
        True,
    ),

    "BLACKLIST_AFTER_ROTATION": env_bool(
        "JWT_BLACKLIST_AFTER_ROTATION",
        True,
    ),

    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",

    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),

    "AUTH_HEADER_NAME": (
        "HTTP_AUTHORIZATION"
    ),

    "USER_ID_FIELD": "id",

    "USER_ID_CLAIM": "user_id",

    "TOKEN_TYPE_CLAIM": "token_type",

    "JTI_CLAIM": "jti",
}


# ============================================================
# CORS
# ============================================================

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    ),
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(
    dict.fromkeys(
        list(default_headers)
        + [
            "authorization",
            "content-type",
            "x-requested-with",
        ]
    )
)

CORS_EXPOSE_HEADERS = [
    "Content-Disposition",
    "Content-Length",
]


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    ),
)


# ============================================================
# MICROSOFT ENTRA ID
# ============================================================

MICROSOFT_TENANT_ID = os.getenv(
    "MICROSOFT_TENANT_ID",
    "",
).strip()

MICROSOFT_CLIENT_ID = os.getenv(
    "MICROSOFT_CLIENT_ID",
    "",
).strip()

MICROSOFT_CLIENT_SECRET = os.getenv(
    "MICROSOFT_CLIENT_SECRET",
    "",
).strip()

MICROSOFT_AUTHORITY = os.getenv(
    "MICROSOFT_AUTHORITY",
    (
        f"https://login.microsoftonline.com/"
        f"{MICROSOFT_TENANT_ID}"
        if MICROSOFT_TENANT_ID
        else ""
    ),
).strip()

MICROSOFT_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI",
    (
        "http://localhost:8000/"
        "api/auth/microsoft/callback/"
    ),
).strip()

MICROSOFT_SCOPES = env_list(
    "MICROSOFT_SCOPES",
    "User.Read",
)

MICROSOFT_APP_SCOPES = env_list(
    "MICROSOFT_APP_SCOPES",
    "https://graph.microsoft.com/.default",
)

MICROSOFT_ALLOWED_DOMAINS = env_list(
    "MICROSOFT_ALLOWED_DOMAINS",
    "uleam.edu.ec",
    lowercase=True,
)

MICROSOFT_ALLOWED_EMAILS = env_list(
    "MICROSOFT_ALLOWED_EMAILS",
    "",
    lowercase=True,
)

MICROSOFT_ADMIN_EMAILS = env_list(
    "MICROSOFT_ADMIN_EMAILS",
    "",
    lowercase=True,
)

MICROSOFT_ALLOW_LOCAL_ACCOUNT_LINKING = env_bool(
    "MICROSOFT_ALLOW_LOCAL_ACCOUNT_LINKING",
    True,
)

MICROSOFT_SYNC_NAMES = env_bool(
    "MICROSOFT_SYNC_NAMES",
    True,
)

MICROSOFT_STORE_RAW_CLAIMS = env_bool(
    "MICROSOFT_STORE_RAW_CLAIMS",
    DEBUG,
)

MICROSOFT_STORE_RAW_GRAPH = env_bool(
    "MICROSOFT_STORE_RAW_GRAPH",
    DEBUG,
)

MICROSOFT_GRAPH_TIMEOUT_SECONDS = env_int(
    "MICROSOFT_GRAPH_TIMEOUT_SECONDS",
    15,
    minimum=1,
    maximum=60,
)

MICROSOFT_STATE_TTL_SECONDS = env_int(
    "MICROSOFT_STATE_TTL_SECONDS",
    300,
    minimum=30,
    maximum=900,
)

MICROSOFT_EXCHANGE_CODE_TTL_SECONDS = env_int(
    "MICROSOFT_EXCHANGE_CODE_TTL_SECONDS",
    120,
    minimum=30,
    maximum=900,
)

MICROSOFT_FRONTEND_LOGIN_PATH = os.getenv(
    "MICROSOFT_FRONTEND_LOGIN_PATH",
    "/login",
).strip()


# ============================================================
# FRONTEND
# ============================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
).strip()


# ============================================================
# RECUPERACIÓN DE CONTRASEÑA
# ============================================================

PASSWORD_RESET_IP_LIMIT = env_int(
    "PASSWORD_RESET_IP_LIMIT",
    5,
    minimum=1,
    maximum=100,
)

PASSWORD_RESET_EMAIL_LIMIT = env_int(
    "PASSWORD_RESET_EMAIL_LIMIT",
    3,
    minimum=1,
    maximum=50,
)

PASSWORD_RESET_WINDOW_SECONDS = env_int(
    "PASSWORD_RESET_WINDOW_SECONDS",
    600,
    minimum=60,
    maximum=86_400,
)

PASSWORD_RESET_FRONTEND_PATH = os.getenv(
    "PASSWORD_RESET_FRONTEND_PATH",
    "/restablecer-contrasena",
).strip()


# ============================================================
# CACHÉ
# ============================================================

REDIS_URL = os.getenv(
    "REDIS_URL",
    "",
).strip()

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": (
                "django_redis.cache."
                "RedisCache"
            ),
            "LOCATION": REDIS_URL,
            "TIMEOUT": 300,
            "KEY_PREFIX": "sgpc",
            "OPTIONS": {
                "CLIENT_CLASS": (
                    "django_redis.client."
                    "DefaultClient"
                ),
                "IGNORE_EXCEPTIONS": False,
            },
        }
    }

else:
    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends."
                "locmem.LocMemCache"
            ),
            "LOCATION": "sgpc-cache-local",
            "TIMEOUT": 300,
            "KEY_PREFIX": "sgpc",
        }
    }


# ============================================================
# CORREO SMTP
# ============================================================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    (
        "django.core.mail.backends.smtp."
        "EmailBackend"
    ),
).strip()

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.office365.com",
).strip()

EMAIL_PORT = env_int(
    "EMAIL_PORT",
    587,
    minimum=1,
    maximum=65535,
)

EMAIL_USE_TLS = env_bool(
    "EMAIL_USE_TLS",
    True,
)

EMAIL_USE_SSL = env_bool(
    "EMAIL_USE_SSL",
    False,
)

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured(
        "EMAIL_USE_TLS y EMAIL_USE_SSL no pueden "
        "estar activos simultáneamente."
    )

EMAIL_TIMEOUT = env_int(
    "EMAIL_TIMEOUT",
    30,
    minimum=1,
    maximum=300,
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
).strip()

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
).strip()

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER,
).strip()

SERVER_EMAIL = os.getenv(
    "SERVER_EMAIL",
    DEFAULT_FROM_EMAIL,
).strip()


# ============================================================
# ADMINISTRADORES DE DJANGO
# ============================================================

DJANGO_ADMIN_EMAILS = env_list(
    "DJANGO_ADMIN_EMAILS",
    "",
    lowercase=True,
)

ADMINS = [
    (
        f"Administrador SGPC {index}",
        email,
    )
    for index, email in enumerate(
        DJANGO_ADMIN_EMAILS,
        start=1,
    )
]

MANAGERS = ADMINS


# ============================================================
# SOLICITUDES DE EXTENSIÓN DEL PERFIL
# ============================================================

PROFILE_EXTENSION_ADMIN_EMAILS = env_list(
    "PROFILE_EXTENSION_ADMIN_EMAILS",
    ",".join(
        DJANGO_ADMIN_EMAILS
    ),
    lowercase=True,
)

PROFILE_EXTENSION_ADMIN_EMAIL = os.getenv(
    "PROFILE_EXTENSION_ADMIN_EMAIL",
    "",
).strip().lower()

PROFILE_EXTENSION_FROM_NAME = os.getenv(
    "PROFILE_EXTENSION_FROM_NAME",
    "SGPC ULEAM",
).strip()

PROFILE_EXTENSION_REQUEST_COOLDOWN_SECONDS = (
    env_int(
        "PROFILE_EXTENSION_REQUEST_COOLDOWN_SECONDS",
        600,
        minimum=60,
        maximum=86_400,
    )
)


# ============================================================
# TELEMETRÍA
# ============================================================

ENABLE_TELEMETRY = env_bool(
    "ENABLE_TELEMETRY",
    False,
)


# ============================================================
# LOGS ESTRUCTURADOS
# ============================================================

DJANGO_LOG_LEVEL = os.getenv(
    "DJANGO_LOG_LEVEL",
    "INFO",
).strip().upper()

CORE_LOG_LEVEL = os.getenv(
    "CORE_LOG_LEVEL",
    "INFO",
).strip().upper()

LOG_FORMAT = (
    "%(asctime)s "
    "%(levelname)s "
    "%(name)s "
    "%(message)s"
)

if ENABLE_TELEMETRY:
    LOG_FORMAT += (
        " %(otelTraceID)s"
        " %(otelSpanID)s"
    )

LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            "()": (
                "pythonjsonlogger.jsonlogger."
                "JsonFormatter"
            ),
            "format": LOG_FORMAT,
        },
    },

    "handlers": {
        "console": {
            "class": (
                "logging.StreamHandler"
            ),
            "formatter": "json",
        },
    },

    "root": {
        "handlers": [
            "console",
        ],
        "level": DJANGO_LOG_LEVEL,
    },

    "loggers": {
        "django": {
            "handlers": [
                "console",
            ],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },

        "django.request": {
            "handlers": [
                "console",
            ],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },

        "django.server": {
            "handlers": [
                "console",
            ],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },

        "core": {
            "handlers": [
                "console",
            ],
            "level": CORE_LOG_LEVEL,
            "propagate": False,
        },
    },
}