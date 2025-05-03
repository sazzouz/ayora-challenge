import json
import uuid
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from typeguard import typechecked

from core.utils.encoders import LazyJsonEncoder
from core.utils.serializers import model_to_dict


class BaseModel(models.Model):
    """Abstract base model mixin."""

    uid: models.UUIDField = models.UUIDField(
        editable=False,
        default=uuid.uuid4,
        unique=True,
        verbose_name=_("UID"),
        help_text=_("Unique identifier for this object."),
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Object created at."),
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Object updated at."),
    )

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        update_fields = kwargs.get("update_fields", None)
        if update_fields:
            # ensure `updated_at` is also updated
            kwargs["update_fields"] = set(update_fields).union({"updated_at"})
        super().save(*args, **kwargs)

    @typechecked
    def dump(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        properties: list[str] | None = None,
    ) -> dict:
        """Serialize model instance as a dict."""

        if include is not None and exclude is not None:
            raise ValueError("Both 'fields' and 'exclude' lists cannot be provided simultaneously.")

        data = model_to_dict(self)

        # handle inclusions and exclusions
        if include:
            data = {field: data[field] for field in include if field in data}
        elif exclude:
            data = {field: data[field] for field in data if field not in exclude}

        # handle properties
        if properties:
            for property in properties:
                data[property] = getattr(self, property)

        return data

    @typechecked
    def dump_json(self, include: list[str] | None = None, exclude: list[str] | None = None) -> str:
        """Serialize model instance as a json string."""

        if include is not None and exclude is not None:
            raise ValueError("Both 'fields' and 'exclude' lists cannot be provided simultaneously.")

        encoder = LazyJsonEncoder()
        data = encoder.encode(self.dump())

        if include:
            data = {field: data[field] for field in include}
        elif exclude:
            data = {field: data[field] for field in data if field not in exclude}

        return data

    @typechecked
    def dump_json_dict(self, include: list[str] | None = None, exclude: list[str] | None = None) -> dict:
        """Serialize model instance as a json-compatible dict."""

        if include is not None and exclude is not None:
            raise ValueError("Both 'fields' and 'exclude' lists cannot be provided simultaneously.")

        encoder = LazyJsonEncoder()
        data = encoder.encode(self.dump())

        if include:
            data = {field: data[field] for field in include}
        elif exclude:
            data = {field: data[field] for field in data if field not in exclude}

        return json.loads(data)
