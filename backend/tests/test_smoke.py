import pytest
from django.apps import apps

from cms.models import CustomImage


def test_custom_image_has_required_alt():
    assert apps.get_model("cms.CustomImage") is CustomImage
    assert CustomImage._meta.get_field("alt").null is False


@pytest.mark.django_db
def test_pages_api_responds(client):
    response = client.get("/api/v2/pages/")

    assert response.status_code == 200
    assert "items" in response.json()
