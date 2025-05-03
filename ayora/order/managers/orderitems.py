from typing import TYPE_CHECKING

from core.mixins.managers import BaseQuerySet
from django.db.models import Subquery

if TYPE_CHECKING:
    from ..models import OrderItem as OrderItemModelType  # noqa: F401


class OrderItemQuerySet(BaseQuerySet["OrderItemModelType"]):
    def accepted(self) -> "OrderItemQuerySet":
        """Return accepted order items."""

        # avoid circular import
        from ..selectors import order__list

        return self.filter(
            order__in=Subquery(order__list().accepted().values("pk")),
        )

    def not__accepted(self) -> "OrderItemQuerySet":
        """Return order items that are not accepted."""

        return self.exclude(pk__in=self.accepted().values("pk"))

    def rejected(self) -> "OrderItemQuerySet":
        """Return rejected order items."""

        # avoid circular import
        from ..selectors import order__list

        return self.filter(
            order__in=Subquery(order__list().rejected().values("pk")),
        )

    def not__rejected(self) -> "OrderItemQuerySet":
        """Return order items that are not rejected."""

        return self.exclude(pk__in=self.rejected().values("pk"))
