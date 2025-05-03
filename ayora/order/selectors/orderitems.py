from typeguard import typechecked

from ..managers import OrderItemQuerySet
from ..models import OrderItem


@typechecked
def order_item__list(optimized: bool = True, *args, **kwargs) -> OrderItemQuerySet:
    """Return a queryset of order item instances."""

    qs = OrderItem.objects.filter(*args, **kwargs)

    # perform query optimizations
    if optimized:
        qs = qs.select_related("order")

    return qs
