# Archivo de configuración principal de Django para SGPC-FCVT:
# define seguridad, apps, base de datos, JWT, CORS/CSRF, Microsoft Entra ID, cache y correo SMTP.

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

load_dotenv()

# ======================================================
# BASE Y RUTAS
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.getenv(name, str(default)).strip().lower()
    return value in ("1", "true", "yes", "on")


def env_list(name, default=""):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# ======================================================
# SEGURIDAD
# ======================================================
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-me",
).strip()

# ✅ CORRECTO: Si falla el .env, el sistema se protege y apaga el debug
DEBUG = env_bool("DJANGO_DEBUG", False)

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

    # apps propias
    "core",

    # terceros
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
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
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
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "SGPC_FCVT_2").strip(),
        "USER": os.getenv("DB_USER", "postgres").strip(),
        "PASSWORD": os.getenv("DB_PASSWORD", "").strip(),
        "HOST": os.getenv("DB_HOST", "127.0.0.1").strip(),
        "PORT": os.getenv("DB_PORT", "5432").strip(),
    }
}


# ======================================================
# VALIDACIÓN DE CONTRASEÑAS
# ======================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# ======================================================
# INTERNACIONALIZACIÓN
# ======================================================
LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"

USE_I18N = True
USE_L10N = True
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
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=8),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ======================================================
# CORS / CSRF
# ======================================================
# Nunca uses "*" si el navegador detecta credentials.
# Define orígenes concretos.
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)


# ✅ CORRECTO: Bloqueamos el paso de cookies de terceros por seguridad
CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
    "x-requested-with",
]

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)


# ======================================================
# LLAVE POR DEFECTO PARA MODELOS
# ======================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ======================================================
# MICROSOFT ENTRA ID / AZURE AD
# ======================================================
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "").strip()
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "").strip()
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "").strip()

MICROSOFT_AUTHORITY = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}"

MICROSOFT_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI",
    "http://localhost:8000/api/auth/microsoft/callback/",
).strip()

MICROSOFT_SCOPES = ["User.Read"]


# ======================================================
# FRONTEND URL
# ======================================================
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
).strip()



# ======================================================
# CACHE (Híbrido: Redis para Prod/Docker, LocMem para Dev Local)
# ======================================================
REDIS_URL = os.getenv("REDIS_URL", "").strip()

if REDIS_URL:
    # Si detecta la variable (en Docker o Servidor), usa Redis
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    # Si no hay variable (tu PC local), usa la memoria de Windows
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sgpc-cache-local",
        }
    }

# ======================================================
# EMAIL / SMTP
# ======================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip()
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "").strip()

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER,
).strip()

# ==============================================================================
# TELEMETRÍA Y LOGS ESTRUCTURADOS (OPENTELEMETRY Y JSON)
# ==============================================================================
import os

# Determina si activamos la telemetría (se activará en producción mediante variables de entorno)
ENABLE_TELEMETRY = os.environ.get('ENABLE_TELEMETRY', 'False') == 'True'

# Configuración del formateador JSON para que guarde el "trace_id" y "span_id" de OpenTelemetry
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(otelTraceID)s %(otelSpanID)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}