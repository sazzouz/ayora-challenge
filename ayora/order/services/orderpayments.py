from core.services.models import model__update
from typeguard import typechecked

from ..managers import OrderPaymentQuerySet
from ..models import OrderPayment


@typechecked
def order_payment__build(*args, **kwargs) -> OrderPayment:
    """Build an order payment instance."""

    instance = OrderPayment(*args, **kwargs)
    return instance


@typechecked
def order_payment__create(*args, **kwargs) -> OrderPayment:
    """Create an order payment instance."""

    instance = OrderPayment.objects.create(*args, **kwargs)
    return instance


@typechecked
def order_payment__bulk_create(*, instances: list[OrderPayment]) -> list[OrderPayment]:
    """Bulk create order payment instances."""

    instances = OrderPayment.objects.bulk_create(instances)
    return instances


@typechecked
def order_payment__get_or_create(*args, **kwargs) -> tuple[OrderPayment, bool]:
    """Get or create a order payment instance."""

    # initialize the created flag
    has_created = False

    try:
        # get the order payment instance
        instance = OrderPayment.objects.get(*args, **kwargs)

        return instance, has_created

    except OrderPayment.DoesNotExist:
        # create the order payment instance
        instance = order_payment__create(*args, **kwargs)

        # update the created flag
        has_created = True

        return instance, has_created


@typechecked
def order_payment__update(*, instance: OrderPayment, updates: dict) -> tuple[OrderPayment, bool]:
    """Update an order payment instance."""

    instance, has_updated = model__update(instance=instance, fields=updates.keys(), data=updates)
    return instance, has_updated


@typechecked
def order_payment__bulk_update(*, queryset: OrderPaymentQuerySet, updated_fields: list) -> int:
    """Bulk update order payment instances."""

    count = OrderPayment.objects.bulk_update(queryset, updated_fields)
    return count
