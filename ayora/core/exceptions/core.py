from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from ..mixins.exceptions import BaseException


class CoreException(BaseException):
    """Core exception."""

    pass


class ValidationError(DjangoValidationError):
    """Custom exception that extends Django's ValidationError to ensure an error code
    is passed in all cases (i.e. admin, API, etc.).

    NOTE: this is considered a suboptimal solution and should be normalized to the
    standard framework exception if the desired behaviour is eventually supported.
    """

    def __init__(self, message: str, code: str = "invalid", params: dict = {}) -> None:
        super().__init__(message, code=code, params=params)

        self.message = message
        self.code = code
        self.params = params


class DuplicateError(BaseException):
    """Duplicate error exception."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "duplicate_error"
    default_detail = _("Object is a duplicate of existing data.")


class StrategyException(ValidationError):
    """Strategy exception."""

    default_code = "strategy_error"
    default_detail = _("Strategy failed.")

    def __init__(self, message: str = default_detail, code: str = default_code, params: dict = {}) -> None:
        super().__init__(message, code=code, params=params)


class DefaultStoreNotImplementedError(CoreException):
    """Default store not implemented error."""

    default_code = "default_store_not_implemented_error"
    default_detail = _("Default store not implemented.")
