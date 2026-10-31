from django.conf import settings
from rest_framework import serializers

RENDITIONS = {
    "thumbnail": "fill-160x160",
    "card": "fill-640x480",
    "tablet": "width-768",
    "full": "width-1600",
}


def _absolute(url):
    if not url:
        return url
    if url.startswith(("http://", "https://")):
        return url
    base = (getattr(settings, "WAGTAILAPI_BASE_URL", "") or "").rstrip("/")
    return f"{base}{url}" if base else url


def _focal_point(image):
    if image.has_focal_point() and image.width and image.height:
        return {
            "x": round(image.focal_point_x / image.width, 4),
            "y": round(image.focal_point_y / image.height, 4),
        }
    return {"x": 0.5, "y": 0.5}


def image_payload(image):
    if not image:
        return None

    renditions = {
        name: _absolute(image.get_rendition(spec).url)
        for name, spec in RENDITIONS.items()
    }

    return {
        "id": image.id,
        "alt": image.alt,
        "width": image.width,
        "height": image.height,
        "focal_point": _focal_point(image),
        "renditions": renditions,
    }


class ImageSerializer(serializers.Field):
    def to_representation(self, value):
        return image_payload(value)
