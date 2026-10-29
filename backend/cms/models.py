from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CustomImage(AbstractImage):
    alt = models.CharField(max_length=255, verbose_name="alt text")

    admin_form_fields = Image.admin_form_fields + ("alt",)

    class Meta:
        verbose_name = "image"
        verbose_name_plural = "images"


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="renditions")

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
