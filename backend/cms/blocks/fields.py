import re
from urllib.parse import urlparse

import nh3
from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.rich_text import expand_db_html

from cms.serializers import image_payload


def page_path(page):
    """Public path for a Wagtail page: no host, no trailing slash."""
    url = page.url
    if not url:
        return ""
    path = urlparse(url).path or "/"
    return path if path == "/" else path.rstrip("/")


class LinkBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=80, required=False)
    page = blocks.PageChooserBlock(required=False)
    url = blocks.CharBlock(max_length=500, required=False)
    new_tab = blocks.BooleanBlock(required=False, default=False)

    class Meta:
        icon = "link"
        label = "Link"

    def clean(self, value):
        label = (value.get("label") or "").strip()
        page = value.get("page")
        url = (value.get("url") or "").strip()

        if not (label or page or url):
            if getattr(self.meta, "required", True):
                raise blocks.StructBlockValidationError(
                    block_errors={"label": ValidationError("This field is required.")}
                )
            return value

        result = super().clean(value)

        if not label:
            raise blocks.StructBlockValidationError(
                block_errors={"label": ValidationError("This field is required.")}
            )

        if bool(page) == bool(url):
            raise blocks.StructBlockValidationError(
                block_errors={"page": ValidationError("Choose exactly one of page or URL.")}
            )

        if url:
            if url.startswith("//"):
                raise blocks.StructBlockValidationError(
                    block_errors={
                        "url": ValidationError("Protocol-relative URLs are not allowed.")
                    }
                )
            parsed = urlparse(url)
            if parsed.scheme and parsed.scheme not in {"http", "https", "mailto", "tel"}:
                raise blocks.StructBlockValidationError(
                    block_errors={"url": ValidationError("Use http, https, mailto or tel.")}
                )

        return result

    def get_api_representation(self, value, context=None):
        if not value:
            return None

        page = value.get("page")
        url = page_path(page) if page else (value.get("url") or "").strip()

        if not url:
            return None

        return {
            "label": value.get("label", ""),
            "url": url,
            "new_tab": bool(value.get("new_tab")),
        }


class ApiImageChooserBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        return image_payload(value)


RICH_TEXT_FEATURES = ["h2", "h3", "bold", "italic", "ol", "ul", "link"]


class SanitizedRichTextBlock(blocks.RichTextBlock):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("features", RICH_TEXT_FEATURES)
        super().__init__(*args, **kwargs)

    def get_api_representation(self, value, context=None):
        html = expand_db_html(value.source) if value else ""
        return nh3.clean(
            html,
            tags={"p", "h2", "h3", "strong", "em", "b", "i", "ul", "ol", "li", "a", "br"},
            attributes={"a": {"href", "title"}},
            url_schemes={"http", "https", "mailto", "tel"},
        )


def safe_text(value):
    return re.sub(r"\s+", " ", value or "").strip()
