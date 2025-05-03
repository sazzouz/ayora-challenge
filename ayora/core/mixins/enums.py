from enum import Enum

from core.exceptions.core import ValidationError
from django.db.models import IntegerChoices, TextChoices


class BaseEnum(Enum):
    """Base class for enums."""

    @classmethod
    def get_members(cls) -> list[Enum]:
        """Members of the enum."""

        return [member for member in cls]

    @classmethod
    def get_values(cls) -> list[str]:
        """Return values of the enum."""

        return [member.value for member in cls]


class BaseTextChoices(TextChoices):
    """Base class for text choices."""

    @classmethod
    def get_label(cls, value: str, as_enum: bool = False) -> str:
        for choice in cls:
            if choice.value == value:
                return cls[choice.label] if as_enum else choice.label
        raise ValidationError(f"Invalid value '{value}' for {cls.__name__}")


class BaseIntegerChoices(IntegerChoices):
    """Base class for integer choices."""

    @classmethod
    def get_label(cls, value: int, as_enum: bool = False) -> str:
        for choice in cls:
            if choice.value == value:
                return cls[choice.label] if as_enum else choice.label
        raise ValidationError(f"Invalid value '{value}' for {cls.__name__}")
