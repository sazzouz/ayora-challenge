from django.urls import path

from .views.orders import (
    CustomerOrdersView,
    CustomerOrderView,
    RefundsView,
    RestaurantOrdersView,
    RestaurantOrderView,
)

app_name = "order"

urlpatterns = [
    # Customer
    path("customers/<str:customerId>/orders", CustomerOrdersView.as_view(), name="customer-orders"),
    path("customers/<str:customerId>/orders/<str:orderId>", CustomerOrderView.as_view(), name="customer-order"),
    # Restaurant
    path("restaurant/orders", RestaurantOrdersView.as_view(), name="restaurant-orders"),
    path("restaurant/orders/<str:orderId>", RestaurantOrderView.as_view(), name="restaurant-order"),
    # Internal
    path("internal/refunds", RefundsView.as_view(), name="internal-refunds"),
]
