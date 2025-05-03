from django.db import transaction
from typeguard import typechecked

from order.models import Order

from ..factories import OrderFactory


@transaction.atomic
@typechecked
def generate_orders(amount: int = 1, create: bool = True, *args, **kwargs) -> list[Order]:
    return OrderFactory.create_batch(amount, **kwargs) if create else OrderFactory.build_batch(amount, **kwargs)
