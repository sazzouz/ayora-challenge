from core.mixins.filters import BaseFilter
from django_filters import rest_framework as filters

from ..models import Order


class OrderFilter(BaseFilter):
    status = filters.CharFilter(
        field_name="status",
        help_text="Order status.",
        lookup_expr="iexact",
    )

    class Meta:
        model = Order
        fields = ["status"]
