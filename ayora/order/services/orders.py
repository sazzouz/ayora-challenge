from core.services.models import model__update
from typeguard import typechecked

from ..managers import OrderItemQuerySet, OrderQuerySet
from ..models import Order, OrderPayment
from ..selectors import order_item__list
from .orderitems import order_item__build, order_item__bulk_create, order_item__bulk_update
from .orderpayments import order_payment__create


@typechecked
def order__build(*args, **kwargs) -> Order:
    """Build an order instance."""

    instance = Order(*args, **kwargs)
    return instance


@typechecked
def order__create(*args, **kwargs) -> Order:
    """Create an order instance."""

    instance = Order.objects.create(*args, **kwargs)
    return instance


@typechecked
def order__bulk_create(*, instances: list[Order]) -> list[Order]:
    """Bulk create order instances."""

    instances = Order.objects.bulk_create(instances)
    return instances


@typechecked
def order__get_or_create(*args, **kwargs) -> tuple[Order, bool]:
    """Get or create a order instance."""

    # initialize the created flag
    has_created = False

    try:
        # get the order instance
        instance = Order.objects.get(*args, **kwargs)

        return instance, has_created

    except Order.DoesNotExist:
        # create the order instance
        instance = order__create(*args, **kwargs)

        # update the created flag
        has_created = True

        return instance, has_created


@typechecked
def order__update(*, instance: Order, updates: dict) -> tuple[Order, bool]:
    """Update an order."""

    instance, has_updated = model__update(instance=instance, fields=updates.keys(), data=updates)
    return instance, has_updated


@typechecked
def order__bulk_update(*, queryset: OrderQuerySet, updated_fields: list) -> int:
    """Bulk update order instances."""

    count = Order.objects.bulk_update(queryset, updated_fields)
    return count


@typechecked
def order__create_items_for_order(*, order: Order, order_items_data: list[dict]) -> OrderItemQuerySet:
    """Create or update order items for an order."""

    # Get existing items as a dict for simpler lookup
    existing_items__qs = order_item__list(order=order)
    existing_items = {item.item_id: item for item in existing_items__qs}

    # Process items
    new_items = []
    items_to_update = {}  # Dictionary to track item_id -> quantity to add
    for item_data in order_items_data:
        item_id = item_data["item_id"]
        quantity = item_data["quantity"]

        if item_id in existing_items:
            # Track the quantity to add for this item
            if item_id not in items_to_update:
                items_to_update[item_id] = quantity
            else:
                items_to_update[item_id] += quantity
        else:
            # Create new item
            new_items.append(order_item__build(order=order, **item_data))

    # Update existing items with accumulated quantities
    if items_to_update:
        items_to_update_qs = existing_items__qs.filter(item_id__in=items_to_update.keys())
        for item in items_to_update_qs:
            item.quantity += items_to_update[item.item_id]
        _ = order_item__bulk_update(queryset=items_to_update_qs, updated_fields=["quantity"])

    # Create new order items
    _ = order_item__bulk_create(instances=new_items)

    # Return latest items for the order
    return order_item__list(order=order)


@typechecked
def order__create_payment_for_order(*, order: Order, payment_info_id: str) -> OrderPayment:
    """Create and payment for an order."""

    return order_payment__create(order=order, payment_info_id=payment_info_id)


@typechecked
def order__handle__stale_orders() -> int:
    """Handle orders that have become stale (i.e. exceeded the auto-rejection time window)"""

    # avoid circular import
    from ..selectors import order__list

    # get stale orders
    stale_orders = order__list().stale()

    if stale_orders.exists():
        # reject stale orders
        for order in stale_orders:
            order.mark_as_rejected()
            order.save()

    return stale_orders.count()
