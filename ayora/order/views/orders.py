from typing import TYPE_CHECKING, Any

from core.utils.responses import success_response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, generics, permissions, request, response, status

from ..constants import ORDER__AUTO_REJECT_MINUTES
from ..enums import OrderStatus
from ..filters import OrderFilter
from ..models import Order
from ..selectors import order__list, order_payment__list
from ..serializers import (
    AcceptRejectRequestSerializer,
    AddItemRequestSerializer,
    OrderRequestSerializer,
    OrderSerializer,
    RefundItemSerializer,
)
from ..services import order__create, order__create_items_for_order, order__create_payment_for_order
from ..tasks import RejectStaleOrdersTask

if TYPE_CHECKING:
    from ..models import Order as OrderModelType  # noqa: F401


class CustomerOrdersView(generics.CreateAPIView):
    """View for customers to place orders."""

    serializer_class = OrderRequestSerializer
    permission_classes = [permissions.AllowAny]

    # NOTE: Execute as a db transaction, only commit if all related objects are successfully created
    @transaction.atomic
    def post(self, request: request.Request, customerId: str, *args: Any, **kwargs: Any) -> response.Response:
        """Place a new order."""

        # Validate the request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create order with validated data
        order = order__create(customer_id=customerId)

        # Create order items
        _ = order__create_items_for_order(order=order, order_items_data=serializer.validated_data["menu_items"])

        # Create order payment
        _ = order__create_payment_for_order(order=order, payment_info_id=serializer.validated_data["payment_info_id"])

        # schedule the auto-rejection task
        # (although we have a regularly polling task, this will track the timing more closely per-order.)
        _ = RejectStaleOrdersTask.apply_async(
            countdown=ORDER__AUTO_REJECT_MINUTES * 60,
        )

        return response.Response(OrderSerializer(instance=order).data, status=status.HTTP_201_CREATED)


class CustomerOrderView(generics.UpdateAPIView):
    """View for customers to add items to their orders."""

    serializer_class = AddItemRequestSerializer
    permission_classes = [permissions.AllowAny]
    # NOTE: we could use `queryset = order__list().actionable()` as another layer if assurance, but would give 404
    # which is less informative to the client, could imply the order details are incorrect
    queryset = order__list()
    lookup_field = "uid"
    lookup_url_kwarg = "orderId"

    def get_queryset(self):
        """Override queryset to handle multi-param URLs."""
        queryset = super().get_queryset()
        customer_id = self.kwargs.get("customerId")
        return queryset.filter(customer_id=customer_id)

    def get_object(self):
        """Override object lookup to handle multi-param URLs."""
        queryset = self.get_queryset()  # Already filtered by customer ID
        order_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            obj = queryset.get(**{self.lookup_field: order_id})
            return obj
        except Order.DoesNotExist:
            raise exceptions.NotFound()

    @extend_schema(exclude=True)
    def put(
        self, request: request.Request, customerId: str, orderId: str, *args: Any, **kwargs: Any
    ) -> response.Response:
        """Override to ignore and disregard `PUT` update requests."""
        raise exceptions.MethodNotAllowed(method="PUT")

    # NOTE: Execute as a transaction, only commit if all related objects are successfully created
    @transaction.atomic
    def patch(
        self, request: request.Request, customerId: str, orderId: str, *args: Any, **kwargs: Any
    ) -> response.Response:
        """Add items to an existing order."""

        # Get the order object
        order: OrderModelType = self.get_object()

        # Validate the request
        serializer = self.get_serializer(data=request.data)
        serializer.context.update({"customerId": customerId, "orderId": orderId})
        serializer.is_valid(raise_exception=True)

        # Create order items
        _ = order__create_items_for_order(order=order, order_items_data=serializer.validated_data["menu_items"])

        # Create order payment
        _ = order__create_payment_for_order(order=order, payment_info_id=serializer.validated_data["payment_info_id"])

        return success_response()


class RestaurantOrdersView(generics.ListAPIView):
    """View for restaurants to list orders."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    queryset = order__list()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get(self, request: request.Request, *args: Any, **kwargs: Any) -> response.Response:
        """Retrieve a list of orders."""

        return self.list(request, *args, **kwargs)


class RestaurantOrderView(generics.UpdateAPIView):
    """View for restaurants to accept/reject orders."""

    serializer_class = AcceptRejectRequestSerializer
    permission_classes = [permissions.AllowAny]
    # NOTE: we could use `queryset = order__list().actionable()` as another layer if assurance, but would give 404
    # which is less informative to the client, could imply the order details are incorrect. Instead, we rely on the
    # finite-state machine logic at the model level.
    queryset = order__list()
    lookup_field = "uid"
    lookup_url_kwarg = "orderId"

    @extend_schema(exclude=True)
    def put(self, request: request.Request, orderId: str, *args: Any, **kwargs: Any) -> response.Response:
        """Override to ignore and disregard `PUT` update requests."""
        raise exceptions.MethodNotAllowed(method="PUT")

    def patch(self, request: request.Request, orderId: str, *args: Any, **kwargs: Any) -> response.Response:
        """Accept or reject an order."""

        # Get the order
        order: OrderModelType = self.get_object()

        # Validate the request
        serializer = self.get_serializer(data=request.data)
        serializer.context.update({"orderId": orderId})
        serializer.is_valid(raise_exception=True)

        # Map the action to the appropriate status
        action = serializer.validated_data["action"]
        status_map = {"accept": OrderStatus.ACCEPTED, "reject": OrderStatus.REJECTED}
        order_status = status_map[action]

        # Handle the desired action
        if order_status == OrderStatus.ACCEPTED:
            order.mark_as_accepted()
            order.save()
        else:
            order.mark_as_rejected()
            order.save()

        return success_response()


class RefundsView(generics.ListAPIView):
    """View for internal services to get refund items."""

    serializer_class = RefundItemSerializer
    permission_classes = [permissions.AllowAny]
    queryset = order_payment__list().rejected()

    def get(self, request: request.Request, *args: Any, **kwargs: Any) -> response.Response:
        """Retrieve a list of refunds (i.e. order payments linked to rejected orders)."""

        return self.list(request, *args, **kwargs)
