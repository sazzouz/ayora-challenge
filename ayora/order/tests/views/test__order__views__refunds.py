import pytest
from django.urls import reverse
from rest_framework import status

from order.enums import OrderStatus
from order.models import Order


@pytest.mark.parametrize(
    "placed_amount, accepted_amount, rejected_amount, expected_rejected_count",
    [
        (3, 2, 4, 4),
        (5, 0, 3, 3),
        (0, 0, 0, 0),
    ],
)
def test__success__refunds_view__list(
    api_client, generate_orders, placed_amount, accepted_amount, rejected_amount, expected_rejected_count
):
    """Test that the refunds endpoint returns only payments for rejected orders."""

    # Generate different orders in different states
    _ = generate_orders(amount=placed_amount)
    _ = generate_orders(amount=accepted_amount, accepted=True)
    _ = generate_orders(amount=rejected_amount, rejected=True)

    # Make the API request
    response = api_client.get(reverse("order:internal-refunds"))

    # Assert response status
    assert response.status_code == status.HTTP_200_OK

    # Verify only rejected orders are included
    assert len(response.data["results"]) == expected_rejected_count

    # Verify payment info structure
    for refund_item in response.data["results"]:
        assert "order_id" in refund_item
        assert "payment_info_id" in refund_item

        # Extract order ID and verify it belongs to a rejected order
        order_id = refund_item["order_id"]
        order = Order.objects.get(uid=order_id)
        assert order.status == OrderStatus.REJECTED
