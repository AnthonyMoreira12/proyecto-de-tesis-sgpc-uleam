# Archivo de configuración principal de Django para SGPC-FCVT:
# define seguridad, apps, base de datos, JWT, CORS/CSRF,
# Microsoft Entra ID, cache y correo SMTP.

from datetime import timedelta
from pathlib import Path
import os

from corsheaders.defaults import default_headers
from dotenv import load_dotenv


# ======================================================
# BASE Y RUTAS
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga el archivo .env ubicado en la raíz del backend.
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    """
    Convierte una variable de entorno a booleano.
    """

    value = os.getenv(
        name,
        str(default),
    ).strip().lower()

    return value in (
        "1",
        "true",
        "yes",
        "on",
    )


def env_list(name, default=""):
    """
    Convierte una variable separada por comas o punto y coma
    en una lista limpia.
    """

    raw = os.getenv(
        name,
        default,
    ).replace(
        ";",
        ",",
    )

    return [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]


# ======================================================
# SEGURIDAD
# ======================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-me",
).strip()

DEBUG = env_bool(
    "DJANGO_DEBUG",
    False,
)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)


# ======================================================
# APPS INSTALADAS
# ======================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps propias
    "core",

    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
]


# ======================================================
# MODELO DE USUARIO PERSONALIZADO
# ======================================================

AUTH_USER_MODEL = "core.Usuario"


# ======================================================
# MIDDLEWARE
# ======================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "BACKEND_SGPC_FCVT.urls"


# ======================================================
# TEMPLATES
# ======================================================

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

WSGI_APPLICATION = "BACKEND_SGPC_FCVT.wsgi.application"


# ======================================================
# BASE DE DATOS
# ======================================================

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
    }
}


# ======================================================
# VALIDACIÓN DE CONTRASEÑAS
# ======================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


# ======================================================
# INTERNACIONALIZACIÓN
# ======================================================

LANGUAGE_CODE = "es-ec"

TIME_ZONE = "America/Guayaquil"

USE_I18N = True

USE_TZ = True


# ======================================================
# ARCHIVOS ESTÁTICOS
# ======================================================

STATIC_URL = "/static/"


# ======================================================
# ARCHIVOS DE MEDIA SUBIDOS POR USUARIOS
# ======================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ======================================================
# CONFIGURACIÓN DRF Y JWT
# ======================================================

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
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=30,
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        hours=8,
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),
}


# ======================================================
# CORS / CSRF
# ======================================================

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    ),
)

CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = list(
    default_headers
) + [
    "authorization",
    "content-type",
    "x-requested-with",
]

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    ),
)


# ======================================================
# LLAVE POR DEFECTO PARA MODELOS
# ======================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ======================================================
# MICROSOFT ENTRA ID / AZURE AD
# ======================================================

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

MICROSOFT_AUTHORITY = (
    "https://login.microsoftonline.com/"
    f"{MICROSOFT_TENANT_ID}"
)

MICROSOFT_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI",
    (
        "http://localhost:8000/"
        "api/auth/microsoft/callback/"
    ),
).strip()

MICROSOFT_SCOPES = [
    "User.Read",
]


# ======================================================
# FRONTEND URL
# ======================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
).strip()


# ======================================================
# CACHE
# Redis para producción/Docker y LocMem para desarrollo.
# ======================================================

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
            "OPTIONS": {
                "CLIENT_CLASS": (
                    "django_redis.client."
                    "DefaultClient"
                ),
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
            "LOCATION": (
                "sgpc-cache-local"
            ),
        }
    }


# ======================================================
# EMAIL / SMTP
# ======================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp."
    "EmailBackend"
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.office365.com",
).strip()

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_USE_TLS = env_bool(
    "EMAIL_USE_TLS",
    True,
)

EMAIL_TIMEOUT = int(
    os.getenv(
        "EMAIL_TIMEOUT",
        "30",
    )
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

SERVER_EMAIL = DEFAULT_FROM_EMAIL


# ======================================================
# SOLICITUDES DE EXTENSIÓN DEL PERFIL
# ======================================================

# Uno o varios correos separados por coma o punto y coma.
PROFILE_EXTENSION_ADMIN_EMAILS = env_list(
    "PROFILE_EXTENSION_ADMIN_EMAILS",
    DEFAULT_FROM_EMAIL,
)

# Evita que el usuario envíe repetidamente la misma solicitud.
# 600 segundos equivalen a 10 minutos.
PROFILE_EXTENSION_REQUEST_COOLDOWN_SECONDS = max(
    60,
    int(
        os.getenv(
            "PROFILE_EXTENSION_REQUEST_COOLDOWN_SECONDS",
            "600",
        )
    ),
)


# ======================================================
# TELEMETRÍA Y LOGS ESTRUCTURADOS
# ======================================================

ENABLE_TELEMETRY = env_bool(
    "ENABLE_TELEMETRY",
    False,
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
            "format": (
                "%(asctime)s "
                "%(levelname)s "
                "%(name)s "
                "%(message)s "
                "%(otelTraceID)s "
                "%(otelSpanID)s"
            ),
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
        "level": os.getenv(
            "DJANGO_LOG_LEVEL",
            "INFO",
        ),
    },
    "loggers": {
        "django": {
            "handlers": [
                "console",
            ],
            "level": os.getenv(
                "DJANGO_LOG_LEVEL",
                "INFO",
            ),
            "propagate": False,
        },
        "core": {
            "handlers": [
                "console",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}