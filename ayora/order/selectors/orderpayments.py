from typeguard import typechecked

from ..managers import OrderPaymentQuerySet
from ..models import OrderPayment


@typechecked
def order_payment__list(optimized: bool = True, *args, **kwargs) -> OrderPaymentQuerySet:
    """Return a queryset of order payment instances."""

    qs = OrderPayment.objects.filter(*args, **kwargs)

    # perform query optimizations
    if optimized:
        qs = qs.select_related("order")

    return qs
