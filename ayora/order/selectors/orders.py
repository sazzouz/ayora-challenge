from typeguard import typechecked

from ..managers import OrderQuerySet
from ..models import Order


@typechecked
def order__list(optimized: bool = True, *args, **kwargs) -> OrderQuerySet:
    """Return a queryset of order instances."""

    qs = Order.objects.filter(*args, **kwargs)

    # perform query optimizations
    if optimized:
        qs = qs.prefetch_related("orderitems", "orderpayments")

    return qs
