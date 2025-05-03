from typing import TYPE_CHECKING

import factory
from core.tests.conftest import CleanModelFactory

from .orderitems import OrderItemFactory
from .orderpayments import OrderPaymentFactory

if TYPE_CHECKING:
    from order.models import Order as OrderModelType


class OrderFactory(
    CleanModelFactory,
):
    customer_id = factory.Faker("uuid4")

    class Meta:
        model = "order.Order"

    class Params:
        items = factory.Trait(_with_items=True)
        payments = factory.Trait(_with_payments=True)
        accepted = factory.Trait(items=True, payments=True, _with_accepted=True)
        rejected = factory.Trait(items=True, payments=True, _with_rejected=True)

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> "OrderModelType":
        # extract flags
        with_items = kwargs.pop("_with_items", False)
        with_payments = kwargs.pop("_with_payments", False)
        with_accepted = kwargs.pop("_with_accepted", False)
        with_rejected = kwargs.pop("_with_rejected", False)

        # create the order
        obj: OrderModelType = super()._create(model_class, *args, **kwargs)

        # handle with items
        if with_items:
            # generate an order item
            _ = OrderItemFactory(order=obj)

        # handle with payments
        if with_payments:
            # generate an order payment
            _ = OrderPaymentFactory(order=obj)

        # handle with accepted
        if with_accepted:
            # mark as accepted
            obj.mark_as_accepted()
            obj.save()

        # handle with rejected
        if with_rejected:
            # mark as rejected
            obj.mark_as_rejected()
            obj.save()

        return obj
