from rest_framework import serializers

from ..models import OrderPayment


class RefundItemSerializer(serializers.ModelSerializer):
    """Read-only details for an order payment requiring a refund."""

    order_id = serializers.SerializerMethodField(help_text="Unique identifier for the order.")

    class Meta:
        model = OrderPayment
        fields = [
            "order_id",
            "payment_info_id",
        ]
        read_only_fields = fields

    def get_order_id(self, obj) -> str:
        return obj.order.uid
