import structlog
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_standardized_errors.formatter import (
    ExceptionFormatter as DrfseExceptionFormatter,
)
from drf_standardized_errors.handler import ExceptionHandler as DrfseExceptionHandler
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DrfValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from typeguard import typechecked

from core.exceptions.core import StrategyException, ValidationError
from core.utils.core import instance_but_not_subclass

logger = structlog.get_logger(__name__)


class ExceptionFormatter(DrfseExceptionFormatter):
    pass


@typechecked
class ExceptionHandler(DrfseExceptionHandler):
    def convert_known_exceptions(self, exc: Exception) -> Exception:
        # handle Django validation errors
        if instance_but_not_subclass(object=exc, klass=DjangoValidationError):
            detail = getattr(exc, "message_dict", DrfValidationError.default_detail)
            code = DrfValidationError.default_code
            return DrfValidationError(
                detail=detail,
                code=code,
            )

        # handle core validation errors
        elif any(
            [
                instance_but_not_subclass(object=exc, klass=ValidationError),
                instance_but_not_subclass(object=exc, klass=StrategyException),
            ]
        ):
            detail = getattr(exc, "message", DrfValidationError.default_detail)
            code = getattr(exc, "code", DrfValidationError.default_code)
            return DrfValidationError(
                detail=detail,
                code=code,
            )

        else:
            return super().convert_known_exceptions(exc)

    def report_exception(self, exc: Exception, response: Response):
        if not isinstance(exc, APIException):
            try:
                request: Request = self.context["request"]._request
            except AttributeError:
                request = None
            logger.exception(exc, path=request.path)
            return super().report_exception(exc, response)
        return None
