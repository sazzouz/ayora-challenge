from typing import Union

from core.mixins.enums import BaseTextChoices
from django.utils.translation import gettext_lazy as _
from typeguard import typechecked


class OrderStatus(BaseTextChoices):
    PLACED = "placed", _("Placed")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")

    @classmethod
    @typechecked
    def valid_actions(cls, as_enum: bool = False) -> list[Union[str, "OrderStatus"]]:
        """Return statuses linked to an order action."""
        members = [member for member in cls if member != cls.PLACED]
        return members if as_enum else [member.value for member in members]
