from django.core.signing import BadSignature, SignatureExpired
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.contrib.redirects.api import RedirectsAPIViewSet

from .models import ContentPage
from .serializers import image_payload

api_router = WagtailAPIRouter("wagtailapi")


class ContentPageAPIViewSet(PagesAPIViewSet):
    model = ContentPage


api_router.register_endpoint("pages", ContentPageAPIViewSet)
api_router.register_endpoint("redirects", RedirectsAPIViewSet)


def block_payload(block):
    return {
        "type": block.block_type,
        "value": block.block.get_api_representation(block.value),
        "id": block.id,
    }


def content_page_payload(page):
    return {
        "id": page.id,
        "title": page.title,
        "slug": page.slug,
        "url_path": page.url_path,
        "seo_title": page.seo_title or "",
        "search_description": page.search_description or "",
        "og_image": image_payload(page.og_image),
        "body": [block_payload(block) for block in page.body],
    }


class PagePreviewAPIView(APIView):
    """Draft preview payload validated by the package's signed token.

    ``wagtail-headless-preview`` 0.9 ships the token model and helpers but not
    an API viewset, so the project provides this endpoint.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, pk=None):
        content_type = request.query_params.get("content_type", "").lower()
        token = request.query_params.get("token", "")

        if content_type != ContentPage.get_content_type_str() or not token:
            return JsonResponse({"detail": "Invalid preview request."}, status=400)

        try:
            page = ContentPage.get_page_from_preview_token(token)
        except (BadSignature, SignatureExpired):
            return JsonResponse({"detail": "Invalid preview token."}, status=403)

        if page is None:
            return JsonResponse({"detail": "Preview not found."}, status=404)

        return JsonResponse(content_page_payload(page))
