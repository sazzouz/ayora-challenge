from django.db import transaction
from typeguard import typechecked

from order.models import OrderPayment

from ..factories import OrderPaymentFactory


@transaction.atomic
@typechecked
def generate_order_payments(amount: int = 1, create: bool = True, *args, **kwargs) -> list[OrderPayment]:
    return (
        OrderPaymentFactory.create_batch(amount, **kwargs)
        if create
        else OrderPaymentFactory.build_batch(amount, **kwargs)
    )
