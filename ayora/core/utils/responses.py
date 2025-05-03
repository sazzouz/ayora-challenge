from rest_framework import status
from rest_framework.response import Response
from typeguard import typechecked


@typechecked
def success_response() -> Response:
    """Provides a standard success response."""
    return Response(status=status.HTTP_200_OK)


@typechecked
def success_response__no_content() -> Response:
    """Provides a standard success response (no content)."""
    return Response(status=status.HTTP_204_NO_CONTENT)


@typechecked
def created_response(headers: dict) -> Response:
    """Provides a standard created response."""
    return Response(status=status.HTTP_201_CREATED, headers=headers)


@typechecked
def server_error_response() -> Response:
    """Provides a standard server error response."""
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@typechecked
def client_error_response() -> Response:
    """Provides a standard client error response."""
    return Response(status=status.HTTP_400_BAD_REQUEST)


@typechecked
def unauthorized_error_response() -> Response:
    """Provides a standard unauthorized error response."""
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@typechecked
def conflict_error_response() -> Response:
    """Provides a standard conflict error response."""
    return Response(status=status.HTTP_409_CONFLICT)
