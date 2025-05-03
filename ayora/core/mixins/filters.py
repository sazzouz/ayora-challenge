from django_filters import rest_framework as filters


class BaseFilter(filters.FilterSet):
    """Base filter with utilities for all subsequent filters."""

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Return all fields of the filter."""

        return list(cls.base_filters.keys())
