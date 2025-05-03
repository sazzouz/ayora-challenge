from typing import TYPE_CHECKING

from core.mixins.managers import BaseQuerySet
from django.db.models import Subquery

if TYPE_CHECKING:
    from ..models import OrderPayment as OrderPaymentModelType  # noqa: F401


class OrderPaymentQuerySet(BaseQuerySet["OrderPaymentModelType"]):
    def rejected(self) -> "OrderPaymentQuerySet":
        """Return order payments for rejected order."""

        # avoid circular import
        from ..selectors import order__list

        return self.filter(
            order__in=Subquery(order__list().rejected().values("pk")),
        )

    def not__rejected(self) -> "OrderPaymentQuerySet":
        """Return order payments not linked to rejected orders."""

        return self.exclude(pk__in=self.rejected().values("pk"))
