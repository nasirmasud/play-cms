import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.models import Page
from wagtail_headless_preview.models import HeadlessMixin

from .blocks import BODY_BLOCKS, LinkBlock
from .serializers import ImageSerializer

MAX_IMAGE_BYTES = 5 * 1024 * 1024
HEX_COLOR = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Use a six-digit hex colour.")

RESERVED_SLUGS = {
    "admin",
    "api",
    "_next",
    "sitemap.xml",
    "robots.txt",
    "preview",
    "exit-preview",
    "cms-hooks",
}

FONT_CHOICES = [
    ("inter", "Inter"),
    ("poppins", "Poppins"),
    ("merriweather", "Merriweather"),
    ("source-sans", "Source Sans"),
]


class CustomImage(AbstractImage):
    alt = models.CharField(max_length=255, verbose_name="alt text")

    admin_form_fields = Image.admin_form_fields + ("alt",)

    api_fields = [
        APIField("alt"),
        APIField("focal_point_x"),
        APIField("focal_point_y"),
        APIField("focal_point_width"),
        APIField("focal_point_height"),
    ]

    class Meta:
        verbose_name = "image"
        verbose_name_plural = "images"

    def clean(self):
        super().clean()

        if self.file:
            if self.file.name.lower().endswith(".svg"):
                raise ValidationError({"file": "SVG uploads are not allowed."})
            if self.file.size > MAX_IMAGE_BYTES:
                raise ValidationError({"file": "Images must be 5 MB or smaller."})


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="renditions")

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class ContentPage(HeadlessMixin, Page):
    body = StreamField(BODY_BLOCKS, min_num=1)
    og_image = models.ForeignKey(
        "cms.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    parent_page_types = ["cms.ContentPage"]
    subpage_types = ["cms.ContentPage"]

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("og_image"),
    ]

    api_fields = [
        APIField("slug"),
        APIField("url_path"),
        APIField("body"),
        APIField("seo_title"),
        APIField("search_description"),
        APIField("og_image", serializer=ImageSerializer()),
    ]

    @classmethod
    def can_create_at(cls, parent):
        # Flat tree: pages may only be created directly under `home`
        # (depth 2). `home` itself is created by the seed command, which
        # bypasses this check.
        return parent.depth == 2 and super().can_create_at(parent)

    def clean(self):
        super().clean()

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", self.slug or ""):
            raise ValidationError(
                {"slug": "Use lowercase letters, numbers and single hyphens."}
            )

        if self.slug in RESERVED_SLUGS:
            raise ValidationError({"slug": "This slug is reserved."})

        if (
            self.slug == "home"
            and ContentPage.objects.filter(slug="home").exclude(pk=self.pk).exists()
        ):
            raise ValidationError({"slug": "Only one home page is allowed."})

        if self.pk:
            original_slug = (
                Page.objects.filter(pk=self.pk).values_list("slug", flat=True).first()
            )
            if original_slug == "home" and self.slug != "home":
                raise ValidationError({"slug": "The home page slug cannot change."})


class FooterColumnBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=80, required=False)
    links = blocks.ListBlock(LinkBlock(), min_num=1, max_num=8)


@register_setting
class HeaderSettings(BaseSiteSetting):
    logo = models.ForeignKey(
        "cms.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    nav_items = StreamField([("link", LinkBlock())], max_num=8, blank=True)

    panels = [
        FieldPanel("logo"),
        FieldPanel("nav_items"),
    ]


@register_setting
class FooterSettings(BaseSiteSetting):
    columns = StreamField([("column", FooterColumnBlock())], max_num=4, blank=True)
    socials = StreamField([("link", LinkBlock())], max_num=8, blank=True)
    copyright_text = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("columns"),
        FieldPanel("socials"),
        FieldPanel("copyright_text"),
    ]


@register_setting
class ThemeSettings(BaseSiteSetting):
    primary = models.CharField(max_length=7, default="#111111", validators=[HEX_COLOR])
    background = models.CharField(max_length=7, default="#ffffff", validators=[HEX_COLOR])
    foreground = models.CharField(max_length=7, default="#111111", validators=[HEX_COLOR])
    radius = models.CharField(
        max_length=8,
        choices=[("none", "None"), ("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
        default="md",
    )
    font_heading = models.CharField(max_length=32, choices=FONT_CHOICES, default="inter")
    font_body = models.CharField(max_length=32, choices=FONT_CHOICES, default="inter")

    panels = [
        FieldPanel("primary"),
        FieldPanel("background"),
        FieldPanel("foreground"),
        FieldPanel("radius"),
        FieldPanel("font_heading"),
        FieldPanel("font_body"),
    ]
