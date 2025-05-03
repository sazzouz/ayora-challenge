import pytest
from django.urls import reverse
from rest_framework import status

from order.enums import OrderStatus
from order.models import Order, OrderItem, OrderPayment


@pytest.mark.parametrize("menu_items_count", [1, 3])
def test__success__customer_orders__create(db, menu_items_count, api_client):
    """Test that a customer can successfully place an order."""
    # Prepare test data
    customer_id = "customer123"
    payment_info_id = "payment123"
    menu_items = [{"item_id": f"item{i}", "quantity": i + 1} for i in range(menu_items_count)]

    # Create request data
    request_data = {"menu_items": menu_items, "payment_info_id": payment_info_id}

    # Make the API request
    response = api_client.post(
        reverse("order:customer-orders", kwargs={"customerId": customer_id}),
        request_data,
    )

    # Assert response status
    assert response.status_code == status.HTTP_201_CREATED

    # Verify response data
    assert response.data["customer_id"] == customer_id
    assert response.data["status"] == OrderStatus.PLACED
    assert len(response.data["menu_items"]) == menu_items_count

    # Verify database objects were created
    order = Order.objects.get(customer_id=customer_id)
    order_items = OrderItem.objects.filter(order=order)
    order_payment = OrderPayment.objects.get(order=order)

    assert order.status == OrderStatus.PLACED
    assert order_items.count() == menu_items_count
    assert order_payment.payment_info_id == payment_info_id


def test__failure__customer_orders__create__empty_menu_items(db, api_client):
    """Test that order creation fails when no menu items are provided."""
    # Prepare request with empty menu items
    request_data = {"menu_items": [], "payment_info_id": "payment123"}

    # Make the API request
    response = api_client.post(
        reverse("order:customer-orders", kwargs={"customerId": "customer123"}),
        request_data,
    )

    # Assert the request fails with appropriate error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid_menu_items" in str(response.data)


def test__failure__customer_orders__create__missing_payment_info(db, api_client):
    """Test that order creation fails when payment info is missing."""
    # Prepare request with missing payment info
    request_data = {"menu_items": [{"item_id": "item1", "quantity": 1}]}

    # Make the API request
    response = api_client.post(
        reverse("order:customer-orders", kwargs={"customerId": "customer123"}),
        request_data,
    )

    # Assert the request fails with appropriate error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "payment_info_id" in str(response.data)
