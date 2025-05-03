# ruff: noqa: F403, F405

from .base import *

DJANGO_ENV = "TEST"

DEBUG = False

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable persistent DB connections
# https://docs.djangoproject.com/en/5.1/ref/databases/#caveats
DATABASES["default"]["CONN_MAX_AGE"] = 0

# ==================================================|
# ============ 3rd party apps settings =============|
# ==================================================|


#  `celery` settings

CELERY_TASK_ALWAYS_EAGER = True

CELERY_TASK_EAGER_PROPAGATES = True
