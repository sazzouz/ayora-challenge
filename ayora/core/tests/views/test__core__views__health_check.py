from django.urls import reverse


def test__core__view__health_check(api_client):
    """Test that the health status endpoint returns a success response."""

    response = api_client.get(reverse("health"))
    assert response.status_code == 204
