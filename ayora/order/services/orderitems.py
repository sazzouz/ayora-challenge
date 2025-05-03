from core.services.models import model__update
from typeguard import typechecked

from ..managers import OrderItemQuerySet
from ..models import OrderItem


@typechecked
def order_item__build(*args, **kwargs) -> OrderItem:
    """Build an order item instance."""

    instance = OrderItem(*args, **kwargs)
    return instance


@typechecked
def order_item__create(*args, **kwargs) -> OrderItem:
    """Create an order item instance."""

    instance = OrderItem.objects.create(*args, **kwargs)
    return instance


@typechecked
def order_item__bulk_create(*, instances: list[OrderItem]) -> list[OrderItem]:
    """Bulk create order item instances."""

    instances = OrderItem.objects.bulk_create(instances)
    return instances


@typechecked
def order_item__get_or_create(*args, **kwargs) -> tuple[OrderItem, bool]:
    """Get or create a order item instance."""

    # initialize the created flag
    has_created = False

    try:
        # get the order item instance
        instance = OrderItem.objects.get(*args, **kwargs)

        return instance, has_created

    except OrderItem.DoesNotExist:
        # create the order item instance
        instance = order_item__create(*args, **kwargs)

        # update the created flag
        has_created = True

        return instance, has_created


@typechecked
def order_item__update(*, instance: OrderItem, updates: dict) -> tuple[OrderItem, bool]:
    """Update an order item instance."""

    instance, has_updated = model__update(instance=instance, fields=updates.keys(), data=updates)
    return instance, has_updated


@typechecked
def order_item__bulk_update(*, queryset: OrderItemQuerySet, updated_fields: list) -> int:
    """Bulk update order item instances."""

    count = OrderItem.objects.bulk_update(queryset, updated_fields)
    return count
