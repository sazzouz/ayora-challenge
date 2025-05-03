from core.mixins.models import (
    BaseModel,
)
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..managers import OrderQuerySet
from ..mixins import (
    OrderFSM,
)


class Order(
    OrderFSM,
    BaseModel,
):
    customer_id: models.CharField = models.CharField(
        max_length=255,
        verbose_name=_("Customer ID"),
        help_text=_("Unique identifier for the customer who placed the order."),
    )

    objects: OrderQuerySet = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"({self.status}) Order for customer: {self.customer_id}"

    @cached_property
    def is_finalised(self) -> bool:
        """Return if the order has recieved an action from the restaurant."""
        return any([self.accepted_at, self.rejected_at])
