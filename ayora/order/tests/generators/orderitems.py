from django.db import transaction
from order.models import OrderItem
from typeguard import typechecked

from ..factories import OrderItemFactory


@transaction.atomic
@typechecked
def generate_order_items(amount: int = 1, create: bool = True, *args, **kwargs) -> list[OrderItem]:
    return OrderItemFactory.create_batch(amount, **kwargs) if create else OrderItemFactory.build_batch(amount, **kwargs)
