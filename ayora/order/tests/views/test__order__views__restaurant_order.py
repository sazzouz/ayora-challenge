import pytest
from django.urls import reverse
from rest_framework import status

from order.enums import OrderStatus


@pytest.mark.parametrize("action,expected_status", [("accept", OrderStatus.ACCEPTED), ("reject", OrderStatus.REJECTED)])
def test__success__restaurant_order__action(action, expected_status, api_client, generate_orders):
    """Test that restaurant can accept take action on an order (i.e. accept or reject)."""

    # Generate an order
    orders = generate_orders()
    order = orders[0]

    # Prepare request data
    request_data = {"action": action}

    # Make the API request
    response = api_client.patch(
        reverse("order:restaurant-order", kwargs={"orderId": order.uid}),
        request_data,
    )

    # Assert response status
    assert response.status_code == status.HTTP_200_OK

    # Verify order status was updated
    order.refresh_from_db()
    assert order.status == expected_status

    # Check additional fields based on action
    if action == "accept":
        assert order.accepted_at is not None
        assert order.rejected_at is None
    else:  # reject
        assert order.rejected_at is not None
        assert order.accepted_at is None


def test__failure__restaurant_order__invalid_action(api_client, generate_orders):
    """Test that invalid actions are rejected."""
    # Generate an order
    orders = generate_orders()
    order = orders[0]

    # Prepare request with invalid action
    request_data = {"action": "invalid_action"}

    # Make the API request
    response = api_client.patch(
        reverse("order:restaurant-order", kwargs={"orderId": order.uid}),
        request_data,
    )

    # Assert bad request response
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test__failure__restaurant_order__already_accepted(api_client, generate_orders):
    """Test that an already accepted order cannot be modified."""
    # Create a test order with ACCEPTED status
    orders = generate_orders(accepted=True)
    order = orders[0]

    # Try to reject the already accepted order
    request_data = {"action": "reject"}

    # Make the API request
    response = api_client.patch(
        reverse("order:restaurant-order", kwargs={"orderId": order.uid}),
        request_data,
    )

    # Assert bad request response
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test__failure__restaurant_order__already_rejected(api_client, generate_orders):
    """Test that an already rejected order cannot be modified."""
    # Create a test order with REJECTED status
    orders = generate_orders(rejected=True)
    order = orders[0]

    # Try to accept the already rejected order
    request_data = {"action": "accept"}

    # Make the API request
    response = api_client.patch(
        reverse("order:restaurant-order", kwargs={"orderId": order.uid}),
        request_data,
    )

    # Assert bad request response
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test__failure__restaurant_order__order_not_found(api_client):
    """Test that a 404 is returned for non-existent orders."""
    # Generate a non-existent order ID
    non_existent_order_id = "non-existent-order-id"

    # Make the API request with non-existent order ID
    response = api_client.patch(
        reverse("order:restaurant-order", kwargs={"orderId": non_existent_order_id}),
        {"action": "accept"},
    )

    # Assert not found response
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test__failure__restaurant_order__put_method_not_allowed(api_client, generate_orders):
    """Test that PUT method is not allowed for restaurant order endpoint."""
    # Generate an order
    orders = generate_orders()
    order = orders[0]

    # Attempt to use PUT method
    response = api_client.put(
        reverse("order:restaurant-order", kwargs={"orderId": order.uid}),
        {"action": "accept"},
    )

    # Assert method not allowed
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
