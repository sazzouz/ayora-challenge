from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..enums import OrderStatus
from ..models import Order
from .orderitems import OrderItemSerializer


class OrderItemRequestSerializer(serializers.Serializer):
    """Serializer for order item in requests."""

    item_id = serializers.CharField(help_text="Unique identifier of the item.")
    quantity = serializers.IntegerField(help_text="Number of items ordered.")


class OrderRequestSerializer(serializers.Serializer):
    """Serializer for creating an order."""

    menu_items = OrderItemRequestSerializer(many=True, required=True)
    payment_info_id = serializers.CharField(required=True)
    # NOTE: although in the schema as part of the payload, is redundant due to URL params
    # customer_id = serializers.CharField(required=True)

    default_error_messages = {
        "invalid_menu_items": "At least one menu item must be provided to place an order.",
        "invalid_quantity": "Quantity must be greater than 0 for all items.",
    }

    def validate(self, attrs):
        # Ensure that at least one menu item is provided
        menu_items = attrs.get("menu_items", [])
        if not menu_items:
            self.fail("invalid_menu_items")

        # Validate quantities
        for item in menu_items:
            if item["quantity"] <= 0:
                self.fail("invalid_quantity")

        return attrs


class AddItemRequestSerializer(serializers.Serializer):
    """Serializer for adding items to an existing order."""

    menu_items = OrderItemRequestSerializer(many=True, required=True)
    payment_info_id = serializers.CharField(required=True)

    default_error_messages = {
        "invalid_status": "Can only add items to an order in the `placed` state.",
        "invalid_customer_for_order": "The referenced customer is not linked to the order.",
    }

    def get_customer_id(self, **kwargs) -> str | None:
        return self.context.get("customerId")

    def get_order_id(self, **kwargs) -> str | None:
        return self.context.get("orderId")

    def validate(self, attrs):
        # get the url params
        customer_id, order_id = self.get_customer_id(), self.get_order_id()

        # get the order
        order = Order.objects.get(uid=order_id)

        # check if the customer is linked to the order
        if not customer_id == order.customer_id:
            self.fail("invalid_customer_for_order")

        # check if the order is in a state that can be updated
        if order.is_finalised:
            self.fail("invalid_status")

        return attrs


class AcceptRejectRequestSerializer(serializers.Serializer):
    """Serializer for accepting/rejecting an order."""

    action = serializers.ChoiceField(choices=["accept", "reject"], required=True)

    default_error_messages = {
        "invalid_already_finalised": "Can only apply action to an order that hasn't been finalised.",
    }

    def get_order_id(self, **kwargs) -> str | None:
        return self.context.get("orderId")

    def validate(self, attrs):
        # get the url params
        order_id = self.get_order_id()

        # get the order
        order = Order.objects.get(uid=order_id)

        # check if the order has already been finalised
        if order.is_finalised:
            self.fail("invalid_already_finalised")

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    """Read-only serializer for an order."""

    order_id = serializers.CharField(source="uid", help_text="Unique identifier for the order.")
    ordered_at = serializers.DateTimeField(source="created_at", help_text="Date and time the order was placed (UTC)")
    menu_items = OrderItemSerializer(
        source="orderitems",
        many=True,
        required=True,
        help_text="Order items linked to the order.",
    )
    status = serializers.SerializerMethodField(
        help_text="Status of the order.",
    )

    class Meta:
        model = Order
        fields = [
            "order_id",
            "customer_id",
            "ordered_at",
            "menu_items",
            "status",
        ]
        read_only_fields = fields

    @staticmethod
    @extend_schema_field(serializers.ChoiceField(choices=OrderStatus.choices, read_only=True))
    def get_status(obj: Order) -> str:
        return obj.status
