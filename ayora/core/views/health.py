from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from ..serializers import HealthCheckSerializer
from ..utils.responses import success_response__no_content


class HealthCheckView(GenericAPIView):
    """Returns a success response if the server is up and running."""

    serializer_class = HealthCheckSerializer

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return success_response__no_content()
