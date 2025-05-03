import base64
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from pydantic_core import Url
from typeguard import typechecked


class LazyJsonEncoder(DjangoJSONEncoder):
    """
    Custom JSON encoder to handle custom types which are not serializable by default.

    see: https://docs.djangoproject.com/en/4.2/topics/serialization/#serialization-formats-json
    """

    def default(self, obj):
        # avoid circular imports
        from core.mixins.models import BaseModel

        # ...handle custom types if unable to serialize in a JSON field.

        # handle decimal objects
        if isinstance(obj, Decimal):
            return str(obj)

        # handle URLs
        if isinstance(obj, Url):
            return str(obj)

        # handle models with UIDs
        if isinstance(obj, BaseModel):
            return obj.uid

        # handle other models
        if isinstance(obj, models.Model):
            return obj.pk

        return super().default(obj)


@typechecked
def encode_base64(data: str) -> str:
    """Encode original string to base64 string."""

    # convert to bytes
    bytes = data.encode("utf-8")

    # encode bytes
    return base64.b64encode(bytes).decode("utf-8")


@typechecked
def decode_base64(data: str) -> str:
    """Decode base64 string to original string."""

    # convert to bytes
    bytes = data.encode("utf-8")

    # decode bytes
    return base64.b64decode(bytes).decode("utf-8")
