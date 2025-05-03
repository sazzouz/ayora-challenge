# ruff: noqa: F403, F405


from .base import *

DJANGO_ENV = "PROD"

DEBUG = False


# Following settings only make sense on production and may break development environments.
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # the same as Caddy has
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [
        # Needed to perform healthcheck
        "^health/",
    ]

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # ==================================================|
    # ============ 3rd party apps settings =============|
    # ==================================================|

    # `structlog`

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

    # `drf_spectacular` app settings

    SPECTACULAR_SETTINGS["SERVERS"] = [{"url": f"{SERVER_URL}"}]

    # ==================================================|
    # ============= Ayora apps settings ==============|
    # ==================================================|
