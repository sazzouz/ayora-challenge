from datetime import timedelta
from typing import TYPE_CHECKING

from core.mixins.managers import BaseQuerySet
from django.utils import timezone

from ..constants import ORDER__AUTO_REJECT_MINUTES
from ..enums import OrderStatus

if TYPE_CHECKING:
    from ..models import Order as OrderModelType  # noqa: F401


class OrderQuerySet(BaseQuerySet["OrderModelType"]):
    def actionable(self) -> "OrderQuerySet":
        """Return orders which can be actioned."""

        return self.exclude(status__in=[OrderStatus.ACCEPTED, OrderStatus.REJECTED])

    def accepted(self) -> "OrderQuerySet":
        """Return accepted orders."""

        return self.filter(accepted_at__isnull=False)

    def not__accepted(self) -> "OrderQuerySet":
        """Return orders that are not accepted."""

        return self.exclude(pk__in=self.accepted().values("pk"))

    def rejected(self) -> "OrderQuerySet":
        """Return rejected orders."""

        return self.filter(rejected_at__isnull=False)

    def not__rejected(self) -> "OrderQuerySet":
        """Return orders that are not rejected."""

        return self.exclude(pk__in=self.rejected().values("pk"))

    def stale(self) -> "OrderQuerySet":
        """Return stale orders (i.e. to be rejected)."""

        # determine the relative cutoff time
        cutoff_time = timezone.now() - timedelta(minutes=ORDER__AUTO_REJECT_MINUTES)

        return self.filter(status=OrderStatus.PLACED, created_at__lt=cutoff_time)
