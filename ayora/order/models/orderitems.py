from typing import Any

from core.mixins.models import (
    BaseModel,
)
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..managers import OrderItemQuerySet
from ..mixins import (
    OrderFK,
)


class OrderItem(
    OrderFK,
    BaseModel,
):
    item_id: models.CharField = models.CharField(
        max_length=255,
        verbose_name=_("Item ID"),
        help_text=_("Unique identifier of the item."),
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity"),
        help_text=_("Number of items ordered."),
    )

    objects: OrderItemQuerySet = OrderItemQuerySet.as_manager()

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "item_id"],
                name="order__orderitem__unique_fields",
            )
        ]

    def __str__(self) -> str:
        return f"Item for order ({self.order.pk}): {self.quantity} x {self.item_id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # validate the instance
        self.full_clean()

        # save the instance
        super().save(*args, **kwargs)
