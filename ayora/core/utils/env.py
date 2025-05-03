from enum import Enum

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from typeguard import typechecked


def env_to_enum(enum_cls: Enum, value: str) -> Enum:
    """Convert an environment variable to an Enum value."""

    for x in enum_cls:
        if x.value == value:
            return x

    raise ImproperlyConfigured(f"Env value {repr(value)} could not be found in {repr(enum_cls)}")


@typechecked
def is_prod() -> bool:
    """Check if the environment is production."""

    return settings.DJANGO_ENV == "PROD"
