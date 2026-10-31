from django.db.models.signals import pre_save
from wagtail.signals import page_published, page_unpublished

from .models import ContentPage
from .revalidation import (
    capture_previous_path,
    page_published_handler,
    page_unpublished_handler,
)

pre_save.connect(
    capture_previous_path, sender=ContentPage, dispatch_uid="cms_previous_path"
)
page_published.connect(
    page_published_handler, sender=ContentPage, dispatch_uid="cms_page_published"
)
page_unpublished.connect(
    page_unpublished_handler,
    sender=ContentPage,
    dispatch_uid="cms_page_unpublished",
)
