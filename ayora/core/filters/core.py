from django_filters import rest_framework as filters
from django_filters.filters import BaseInFilter


class CharInFilter(BaseInFilter, filters.CharFilter):
    """Filter for membership in a list of strings."""

    pass


class NumberInFilter(BaseInFilter, filters.NumberFilter):
    """Filter for membership in a list of numbers."""

    pass
