import os
from pathlib import Path

import dj_database_url
import rest_framework.exceptions as drf_exceptions
import structlog
from django.utils.translation import gettext_lazy as _

# Initialise environment variables
from ..env import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def rel(*path: str) -> str:
    """
    Used to get the relative path for any file, combines with the BASEDIR
    @param path: the relative path for the file
    @return: absolute path to the file
    """
    return os.path.join(BASE_DIR, *path)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django_supersecret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Domains

SERVER_DOMAIN = env("DJANGO_PROJECT_DOMAIN", default="localhost:8000")

SERVER_URL = f"https://{SERVER_DOMAIN}" if not DEBUG else f"http://{SERVER_DOMAIN}"

CLIENT_DOMAIN = env("DJANGO_CLIENT_DOMAIN", default="localhost:3000")

CLIENT_URL = f"https://{CLIENT_DOMAIN}"

ALLOWED_HOSTS = [
    SERVER_DOMAIN,
    # NOTE: Also needed in production to perform healthcheck
    "localhost",
]

SITE_URL = SERVER_URL

# CSRF

CSRF_TRUSTED_ORIGINS = [SERVER_URL]

CORS_ALLOWED_ORIGINS = [CLIENT_URL]

AYORA_APPS = [
    "core.apps.CoreConfig",
    "order.apps.OrderConfig",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_celery_beat",
    "django_extensions",
    "django_filters",
    "django_structlog",
    "drf_spectacular",
    "drf_standardized_errors",
    "rest_framework",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.humanize",
    "django.contrib.admindocs",
    *THIRD_PARTY_APPS,
    *AYORA_APPS,
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "config.urls"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# NOTE: also used for email verification link
PASSWORD_RESET_TIMEOUT = 259200  # 3 days, in seconds (default)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        env="DB_URL",
        conn_max_age=int(os.getenv("POSTGRES_CONN_MAX_AGE", 600)),
        conn_health_checks=True,
    )
}

# Cache

# https://docs.djangoproject.com/en/dev/ref/settings/#cache
CACHES = {"default": env.cache("REDIS_URL")}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
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

# Email

EMAIL_BACKEND = "core.utils.emails.ConsoleEmailBackend"

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
        "verbose": {"format": ("%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s")},
        "simple": {"format": "%(levelname)s %(message)s"},
        "sql": {
            "()": "core.utils.loggers.SQLFormatter",
            "format": "%(duration).3f %(statement)s",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
        "sql": {
            "class": "logging.StreamHandler",
            "formatter": "sql",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django": {
            "handlers": ["console"],
            "propagate": True,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console", "sql"],
            "level": "INFO",
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-gb"

LOCALE_PATHS: list[str] = []

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Sessions

"""
Do read:
    1. https://docs.djangoproject.com/en/3.1/ref/settings/#sessions
    2. https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
"""
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=1209600)  # Default - 2 weeks in seconds

SESSION_COOKIE_HTTPONLY = env.bool("SESSION_COOKIE_HTTPONLY", default=True)

SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME", default="sessionid")

SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", default="Lax")

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)

CSRF_USE_SESSIONS = env.bool("CSRF_USE_SESSIONS", default=True)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# This setting tells Django at which URL static files are going to be served.
# Here, they well be accessible at your-domain.onrender.com/static/...
STATIC_URL = "/static/"

STATIC_ROOT = rel(env("DJANGO_STATIC_ROOT", default="static"))

STATICFILES_DIR = rel("static")

# Media files i.e. user uploaded files

MEDIA_URL = "/media/"

MEDIA_ROOT = rel(env("DJANGO_MEDIA_ROOT", default="media"))

DEFAULT_CONTENT_TYPE = "application/octet-stream"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Max file size for uploads
# https://docs.djangoproject.com/en/dev/ref/settings/#data-upload-max-memory-size
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB

# ==================================================|
# ============ 3rd party apps settings =============|
# ==================================================|


# `structlog` settings

STRUCTLOG_PROCESSORS = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.filter_by_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

STRUCTLOG_SETTINGS = {
    "processors": STRUCTLOG_PROCESSORS,
    "logger_factory": structlog.stdlib.LoggerFactory(),
    "wrapper_class": structlog.stdlib.BoundLogger,
    "cache_logger_on_first_use": True,
}

structlog.configure(**STRUCTLOG_SETTINGS)

# `django-structlog` settings

DJANGO_STRUCTLOG_CELERY_ENABLED = True


# `rest_framework` settings


class AuthenticationFailed(drf_exceptions.AuthenticationFailed):
    pass


class InvalidToken(AuthenticationFailed):
    default_detail = _("Token is invalid or expired")
    default_code = "token_not_valid"


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_standardized_errors.openapi.AutoSchema",
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ],
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "UPLOADED_FILES_USE_URL": True,
    "ORDERING_PARAM": "sort_by",
    "SEARCH_PARAM": "search",
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "core.utils.paginators.PageNumberPaginator",
    "PAGE_SIZE": 20,
}

# `drf-standardized-errors` settings

DRF_STANDARDIZED_ERRORS = {
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True,
    "EXCEPTION_HANDLER_CLASS": "core.utils.exceptions.ExceptionHandler",
    "EXCEPTION_FORMATTER_CLASS": "core.utils.exceptions.ExceptionFormatter",
    "ALLOWED_ERROR_STATUS_CODES": [
        "400",
        "404",
    ],
}

# `drf_spectacular` settings


SPECTACULAR_SETTINGS = {
    "TITLE": "Ayora API",
    "DESCRIPTION": "Ayora API documentation.",
    "VERSION": "1.0.0",
    "SERVERS": [{"url": f"{SERVER_URL}"}],
    "SERVE_PERMISSIONS": [],
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_PATCH": True,
    "PREPROCESSING_HOOKS": [
        "drf_spectacular.hooks.preprocess_exclude_path_format",
        "config.docs.custom_preprocessing_hook",
    ],
    "POSTPROCESSING_HOOKS": [
        "drf_standardized_errors.openapi_hooks.postprocess_schema_enums",
        "config.docs.custom_postprocessing_hook",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_standardized_errors.openapi_serializers.ValidationErrorEnum.choices",
        "ClientErrorEnum": "drf_standardized_errors.openapi_serializers.ClientErrorEnum.choices",
        "ServerErrorEnum": "drf_standardized_errors.openapi_serializers.ServerErrorEnum.choices",
        "ErrorCode401Enum": "drf_standardized_errors.openapi_serializers.ErrorCode401Enum.choices",
        "ErrorCode403Enum": "drf_standardized_errors.openapi_serializers.ErrorCode403Enum.choices",
        "ErrorCode404Enum": "drf_standardized_errors.openapi_serializers.ErrorCode404Enum.choices",
        "ErrorCode405Enum": "drf_standardized_errors.openapi_serializers.ErrorCode405Enum.choices",
        "ErrorCode406Enum": "drf_standardized_errors.openapi_serializers.ErrorCode406Enum.choices",
        "ErrorCode415Enum": "drf_standardized_errors.openapi_serializers.ErrorCode415Enum.choices",
        "ErrorCode429Enum": "drf_standardized_errors.openapi_serializers.ErrorCode429Enum.choices",
        "ErrorCode500Enum": "drf_standardized_errors.openapi_serializers.ErrorCode500Enum.choices",
    },
    "SORT_OPERATION_PARAMETERS": True,
}

# `corsheaders` settings

CORS_ALLOW_CREDENTIALS = True

# `celery` settings

CELERY_BROKER_URL = env("REDIS_URL")

CELERY_RESULT_BACKEND = env("REDIS_URL")

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = 60 * 40  # 40 minutes

CELERY_BROKER_URL = env("REDIS_URL")

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_ACCEPT_CONTENT = ["json"]

CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_BACKEND = env("REDIS_URL")

CELERY_CACHE_BACKEND = "default"

CELERY_WORKER_MAX_TASKS_PER_CHILD = 100

# ==================================================|
# ============= Ayora apps settings ==============|
# ==================================================|


CORE__DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

CORE__STATIC_MEDIA_MAX_BYTES = DATA_UPLOAD_MAX_MEMORY_SIZE  # 50 MB

CORE__REPR_OUTPUT_SIZE = 5
