from typing import Any

from rest_framework.permissions import SAFE_METHODS


class ReadWriteSerializerMixin:
    """
    Ref: https://www.revsys.com/tidbits/using-different-read-and-write-serializers-django-rest-framework/

    A mixin that provides a way to specify different serializers
        for read and write operations.
    """

    read_serializer_class: Any = None
    write_serializer_class: Any = None

    def get_serializer_class(self) -> Any:
        if self.request.method in SAFE_METHODS:
            return self.get_read_serializer_class()
        return self.get_write_serializer_class()

    def get_read_serializer_class(self) -> Any:
        assert self.read_serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a "
            "`read_serializer_class` attribute, or override the "
            "`get_read_serializer_class()` method."
        )
        return self.read_serializer_class

    def get_write_serializer_class(self) -> Any:
        assert self.write_serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a "
            "`write_serializer_class` attribute, or override the "
            "`get_write_serializer_class()` method."
        )
        return self.write_serializer_class
