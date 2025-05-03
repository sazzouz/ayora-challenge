# ruff: noqa: F403, F405


from .base import *

DJANGO_ENV = "DEV"


# Disable persistent DB connections
# https://docs.djangoproject.com/en/5.1/ref/databases/#caveats
DATABASES["default"]["CONN_MAX_AGE"] = 0

# Domains (using HTTP by default)

SERVER_DOMAIN = env("DJANGO_PROJECT_DOMAIN", default="localhost:8000")

SERVER_URL = f"http://{SERVER_DOMAIN}"

CLIENT_DOMAIN = env("DJANGO_CLIENT_DOMAIN", default="localhost:3000")

CLIENT_URL = f"http://{CLIENT_DOMAIN}"

ALLOWED_HOSTS = [
    SERVER_DOMAIN,
    "localhost",
]

# ==================================================|
# ============ 3rd party apps settings =============|
# ==================================================|


# ==================================================|
# ============= Ayora apps settings ==============|
# ==================================================|
