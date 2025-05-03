from itertools import chain

from django.db import models
from rest_framework import serializers
from typeguard import typechecked

from core.types.models import DjangoModelType


@typechecked
def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


@typechecked
def inline_serializer(*, fields, data=None, **kwargs):
    """Create an inline serializer.

    NOTE: Important note if you are using `drf-spectacular`
    Please refer to the following issue:
    https://github.com/HackSoftware/Django-Styleguide/issues/105#issuecomment-1669468898
    Since you might need to use unique names (uuids) for each inline serializer
    """

    serializer_class = create_serializer_class(name="", fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


@typechecked
def model_to_dict(
    obj: "DjangoModelType",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict:
    """
    Custom `model_to_dict` implementation that includes all fields by default.
    Inspired by `django.forms.models.model_to_dict`
    """
    opts = obj._meta
    data = {}

    # Get all field types
    for field in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        # Skip if field should be excluded
        if exclude and field.name in exclude:
            continue
        # Skip if using include and field is not in include list
        if include and field.name not in include:
            continue

        # Get the field value, handling special cases
        value = field.value_from_object(obj)

        # Convert UUID fields to string for serialization
        if isinstance(field, models.UUIDField):
            value = str(value)

        data[field.name] = value

    return data
