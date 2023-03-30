"""
Default django settings for collectivo_app.

Will not be used if custom settings are defined through
the COLLECTIVO_SETTINGS environment variable (see manage.py).
"""
import logging
import os
from pathlib import Path

from corsheaders.defaults import default_headers

from collectivo.version import __version__

from .utils import get_env_bool, string_to_list

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = get_env_bool("DEBUG", False)
DEVELOPMENT = get_env_bool("DEVELOPMENT", False)

if os.environ.get("ALLOWED_HOSTS") is not None:
    ALLOWED_HOSTS = string_to_list(os.environ.get("ALLOWED_HOSTS"))
elif DEVELOPMENT:
    ALLOWED_HOSTS = [
        "*",
        "0.0.0.0",
        "127.0.0.1",
        "localhost",
        "collectivo.local",
    ]
else:
    logger.warning(
        "You must set the environment variable "
        "ALLOWED_HOSTS if DEVELOPMENT is False."
    )

# Choose built-in collectivo extensions from environment
_built_in_extensions = [
    "profiles",
    "memberships",
    "memberships.payments",
    "emails",
    "emails.tags",
    "tags",
    "payments",
    "shifts",
    "direktkredit",
]
_chosen_extensions = string_to_list(os.environ.get("COLLECTIVO_EXTENSIONS"))
for ext in _chosen_extensions:
    if ext not in _built_in_extensions:
        _chosen_extensions.remove(ext)
        logger.warning(
            f"Environment variable '{ext}' in 'COLLECTIVO_EXTENSIONS' has "
            f"been ignored. Available extensions are: {_built_in_extensions}."
        )

INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "corsheaders",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "simple_history",
    # Collectivo core apps
    "collectivo",
    "collectivo.core",
    "collectivo.auth.keycloak",
    "collectivo.menus",
    "collectivo.extensions",
    "collectivo.dashboard",
    # Collectivo custom extensions
    *[f"collectivo.{ext}" for ext in _chosen_extensions],
    # TODO: Move this to MILA Repository
    "mila.registration",
    "mila.direktkredit",
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

if DEVELOPMENT:
    INSTALLED_APPS += ["django_extensions"]

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


# CORS Settings
# https://pypi.org/project/django-cors-headers/

if os.environ.get("CORS_ALLOWED_ORIGINS"):
    CORS_ALLOWED_ORIGINS = string_to_list(
        os.environ.get("CORS_ALLOWED_ORIGINS")
    )
elif DEVELOPMENT:
    CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-Request-ID",
]

CORS_EXPOSE_HEADERS = [
    "X-Request-ID",
]


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


# Celery settings
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
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
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
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
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
    "DESCRIPTION": "A modular framework to build participative community platforms.",
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
            "format": "\n\x1b[33;20m[%(levelname)s %(asctime)s %(pathname)s@%(lineno)s]:\x1b[0m %(message)s"
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
        "collectivo": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


# Email settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 465)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = get_env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = get_env_bool("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_FROM")


# Settings for collectivo
COLLECTIVO = {
    "dev.create_test_data": DEVELOPMENT,
    "keycloak.synchronize": True,
    "keycloak.server_url": os.environ.get("KEYCLOAK_SERVER_URL"),
    "keycloak.realm_name": os.environ.get("KEYCLOAK_REALM_NAME", "collectivo"),
    "keycloak.client_id": os.environ.get("KEYCLOAK_CLIENT_ID", "collectivo"),
    "keycloak.client_secret_key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
}
