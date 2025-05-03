from core.mixins.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..managers import OrderPaymentQuerySet
from ..mixins import OrderFK


class OrderPayment(OrderFK, BaseModel):
    payment_info_id: models.CharField = models.CharField(
        max_length=255,
        verbose_name=_("Payment Info ID"),
        help_text=_("Unique identifier for the order payment."),
    )

    objects: OrderPaymentQuerySet = OrderPaymentQuerySet.as_manager()

    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["order", "payment_info_id"],
                name="order__orderpayment__unique_fields",
            )
        ]

    def __str__(self) -> str:
        return f"Payment for order ({self.order.pk}): {self.payment_info_id}"
