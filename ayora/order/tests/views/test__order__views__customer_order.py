import uuid

from django.urls import reverse
from rest_framework import status

from order.models import OrderItem, OrderPayment


def test__success__customer_order__add_items(db, api_client, generate_orders, generate_order_payments):
    """Test that a customer can successfully add items to their placed order."""

    customer_id = str(uuid.uuid4())
    orders = generate_orders(customer_id=customer_id)
    _ = [generate_order_payments(order=order) for order in orders]
    order = orders[0]

    # Prepare additional items
    new_items = [{"item_id": str(uuid.uuid4()), "quantity": 2}, {"item_id": str(uuid.uuid4()), "quantity": 3}]
    new_payment_info_id = str(uuid.uuid4())

    # Create request data
    request_data = {"menu_items": new_items, "payment_info_id": new_payment_info_id}

    # Make the API request
    response = api_client.patch(
        reverse("order:customer-order", kwargs={"customerId": customer_id, "orderId": order.uid}),
        request_data,
    )

    # Assert response status
    assert response.status_code == status.HTTP_200_OK

    # Verify database changes
    order_items = OrderItem.objects.filter(order=order)
    order_payments = OrderPayment.objects.filter(order=order)

    # Verify the items were added
    assert order_items.count() > 1
    assert order_payments.count() > 1
    assert OrderPayment.objects.filter(order=order, payment_info_id=new_payment_info_id).exists()


def test__failure__customer_order__add_items__order_accepted(db, api_client, generate_orders):
    """Test that items cannot be added to an accepted order."""
    # Create an accepted order

    orders = generate_orders(accepted=True)
    order = orders[0]

    # Prepare request data
    request_data = {"menu_items": [{"item_id": "item2", "quantity": 2}], "payment_info_id": "payment456"}

    # Make the API request
    response = api_client.patch(
        reverse("order:customer-order", kwargs={"customerId": order.customer_id, "orderId": order.uid}),
        request_data,
    )

    # Assert the request fails with appropriate error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid_status" in str(response.data)


def test__failure__customer_order__add_items__wrong_customer(db, api_client, generate_orders):
    """Test that items cannot be added to an order by a different customer."""
    # Create test order for one customer
    original_customer_id = "customer123"
    orders = generate_orders(customer_id=original_customer_id)
    order = orders[0]

    # Attempt to add items using a different customer ID
    different_customer_id = "customer456"

    request_data = {"menu_items": [{"item_id": "item2", "quantity": 2}], "payment_info_id": "payment456"}

    # Make the API request with different customer ID
    response = api_client.patch(
        reverse("order:customer-order", kwargs={"customerId": different_customer_id, "orderId": order.uid}),
        request_data,
    )

    # Should return 404 since the order isn't found for that customer
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test__failure__customer_order__put_method_not_allowed(api_client, generate_orders):
    """Test that PUT method is not allowed for customer order endpoint."""
    # Create test order
    customer_id = "customer123"
    orders = generate_orders(customer_id=customer_id)
    order = orders[0]

    # Attempt to use PUT method
    response = api_client.put(
        reverse("order:customer-order", kwargs={"customerId": customer_id, "orderId": order.uid}),
        {"menu_items": [{"item_id": "item2", "quantity": 2}], "payment_info_id": "payment456"},
    )

    # Assert method not allowed
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
