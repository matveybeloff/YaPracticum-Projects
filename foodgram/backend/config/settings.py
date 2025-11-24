import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .constants import DEFAULT_PAGE_SIZE

try:
    _base = Path(__file__).resolve().parent.parent
    _env_path = _base.parent / ".env"
    load_dotenv(_env_path) if _env_path.exists() else load_dotenv()
except Exception:
    pass


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-u8*t^bg38k4w5n*c!q4k9_e49ix&n#i=z*0*fmf^#hljs6yt8i",
)


def _to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


DEBUG = _to_bool(os.getenv("DEBUG"), default=True)

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,food.sytes.net"
).split(",")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CSRF_TRUSTED_ORIGINS_ENV = os.getenv("CSRF_TRUSTED_ORIGINS")
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [
        s.strip() for s in CSRF_TRUSTED_ORIGINS_ENV.split(",") if s.strip()
    ]
else:
    CSRF_TRUSTED_ORIGINS = [
        f"https://{h.strip()}"
        for h in ALLOWED_HOSTS
        if h.strip() and h.strip() not in {
            "localhost", "127.0.0.1", "0.0.0.0"
        }
    ]
    CSRF_TRUSTED_ORIGINS += [
        "http://localhost",
        "http://127.0.0.1",
    ]

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "rest_framework.authtoken",
    "djoser",
    "django_filters",
    "users",
    "recipes",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            (BASE_DIR.parent / "frontend" / "build"),
            (BASE_DIR.parent / "docs"),
        ],
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


WSGI_APPLICATION = "config.wsgi.application"


if os.getenv("POSTGRES_DB") or os.getenv("DB_ENGINE") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv(
                "POSTGRES_DB", os.getenv("DB_NAME", "postgres")
            ),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_USER_MODEL = "users.User"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "api.pagination.LimitPageNumberPagination"
    ),
    "PAGE_SIZE": DEFAULT_PAGE_SIZE,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
}


DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": False,
    "SERIALIZERS": {
        "user": "api.users.serializers.UserSerializer",
        "current_user": "api.users.serializers.UserSerializer",
    },
    "PERMISSIONS": {
        "user": ["rest_framework.permissions.AllowAny"],
        "user_list": ["rest_framework.permissions.AllowAny"],
        "current_user": ["rest_framework.permissions.IsAuthenticated"],
    },
}


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


LANGUAGE_CODE = "ru"


_STATIC_ROOT = os.getenv("STATIC_ROOT")
STATIC_ROOT = (
    Path(_STATIC_ROOT) if _STATIC_ROOT else (BASE_DIR / "staticfiles")
)


TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


MEDIA_URL = "/media/"
_MEDIA_ROOT = os.getenv("MEDIA_ROOT")
MEDIA_ROOT = Path(_MEDIA_ROOT) if _MEDIA_ROOT else (BASE_DIR / "media")


STATIC_URL = "static/"
STATICFILES_DIRS = [
    (BASE_DIR.parent / "frontend" / "build" / "static"),
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
