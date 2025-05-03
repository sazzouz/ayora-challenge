import pytest
from django.urls import reverse
from rest_framework import status

from order.enums import OrderStatus


@pytest.mark.parametrize("order_count", [3, 5])
def test__success__restaurant_orders__list(order_count, api_client, generate_orders):
    """Test that restaurant can view all orders."""

    # Generate orders
    _ = generate_orders(amount=order_count)

    # Make the API request
    response = api_client.get(reverse("order:restaurant-orders"))

    # Assert response status and data
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == order_count

    # Verify first result contains expected fields
    first_result = response.data["results"][0]
    assert "order_id" in first_result
    assert "customer_id" in first_result
    assert "ordered_at" in first_result
    assert "menu_items" in first_result
    assert "status" in first_result


@pytest.mark.parametrize("filter_status", [OrderStatus.PLACED, OrderStatus.ACCEPTED, OrderStatus.REJECTED])
def test__success__restaurant_orders__filter_by_status(api_client, filter_status, generate_orders):
    """Test that orders can be filtered by status."""

    # Generate orders with different statuses
    for order_status in OrderStatus.values:
        generate_orders(amount=2, status=order_status)

    # Make the API request with status filter
    response = api_client.get(reverse("order:restaurant-orders") + f"?status={filter_status}")

    # Assert response status
    assert response.status_code == status.HTTP_200_OK

    # Verify filtered results
    assert response.data["count"] == 2

    # All returned orders should have the requested status
    for order in response.data["results"]:
        assert order["status"] == filter_status
