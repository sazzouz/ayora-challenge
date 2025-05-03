from rest_framework import serializers

from ..models import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Read-only details for an order item."""

    class Meta:
        model = OrderItem
        fields = ["quantity", "item_id"]
        read_only_fields = fields
