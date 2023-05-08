"""Django settings for collectivo."""
import logging
import os
from pathlib import Path

from corsheaders.defaults import default_headers

from collectivo.version import __version__

from .utils import get_env_bool, load_collectivo_settings

logger = logging.getLogger(__name__)

# Collectivo
COLLECTIVO = {
    "development": False,
    "example_data": False,
    "api_docs": False,
    "extensions": [],
    **load_collectivo_settings(),
}

# Django
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = COLLECTIVO["development"]  # Enable debug mode in development
ALLOWED_HOSTS = COLLECTIVO["allowed_hosts"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "simple_history",
    "collectivo",
    "collectivo.core",
    *COLLECTIVO["extensions"],
]


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "collectivo.core.middleware.AddRequestId",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "collectivo.core.middleware.RequestLogMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]


ROOT_URLCONF = "collectivo_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "collectivo_app.wsgi.application"


# CORS
# https://pypi.org/project/django-cors-headers/

CORS_ALLOWED_ORIGINS = COLLECTIVO["allowed_origins"]
CORS_ORIGIN_ALLOW_ALL = COLLECTIVO["development"]
CORS_ALLOW_HEADERS = list(default_headers) + ["X-Request-ID"]
CORS_EXPOSE_HEADERS = ["X-Request-ID"]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASS"),
    }
}


# Celery

CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_EVENT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_TASK_ACCEPT_CONTENT = ["pickle"]
CELERY_RESULT_ACCEPT_CONTENT = ["pickle"]
CELERY_EVENT_ACCEPT_CONTENT = ["pickle"]
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_BACKEND", "redis://127.0.0.1:6379/0"
)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.environ.get("TIME_ZONE", "CET")
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_DIR = os.path.realpath(os.path.join(BASE_DIR, "static"))
STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django Rest Framework (DRF)
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.LimitOffsetPagination"
    ),
    "DEFAULT_VERSIONING_CLASS": (
        "rest_framework.versioning.AcceptHeaderVersioning"
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "collectivo.auth.keycloak.authentication.KeycloakAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}


# DRF Spectacular (OpenAPI)
# https://drf-spectacular.readthedocs.io/

_schema_versions = ["0.1.0"]
_swagger_urls = ""
for version in _schema_versions:
    _swagger_urls += (
        f'{{url: "/api/dev/schema/?version={version}", '
        f'name: "API Version {version}"}}, '
    )

SPECTACULAR_SETTINGS = {
    "TITLE": "collectivo",
    "DESCRIPTION": (
        "A modular framework to build participative community platforms."
    ),
    "LICENSE": {
        "name": "GNU Affero General Public License v3.0",
        "url": "https://github.com/MILA-Wien/collectivo/blob/main/LICENSE",
    },
    "VERSION": "",
    "SERVERS": [],
    "TAGS": [],
    "EXTERNAL_DOCS": {"url": "https://github.com/MILA-Wien/collectivo"},
    # Allow for authentication via token in the SwaggerUI interface
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            }
        }
    },
    "SECURITY": [
        {
            "ApiKeyAuth": [],
        }
    ],
    # Define SWAGGER UI with top bar for version switching
    "SWAGGER_UI_SETTINGS": f"""{{
        deepLinking: true,
        urls: [{_swagger_urls}],
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        layout: "StandaloneLayout",
        persistAuthorization: true,
        filter: true
    }}""",
}


# Logging
# https://docs.djangoproject.com/en/4.1/ref/logging/

LOGGING_LEVEL = "DEBUG"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": (
                "\n\x1b[33;20m[%(levelname)s %(asctime)s"
                " %(pathname)s@%(lineno)s]:\x1b[0m %(message)s"
            )
        },
        "simple": {"format": "[%(levelname)s %(asctime)s]: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        name: {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        }
        for name in INSTALLED_APPS
    },
}


# Emails
# TODO: Move to extension settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 465)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = get_env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = get_env_bool("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_FROM")
