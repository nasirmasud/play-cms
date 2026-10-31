import json
import urllib.request

from django.conf import settings

from cms.models import ContentPage


def _public_path(url_path):
    path = url_path or "/"
    if path.startswith("/home/"):
        path = path[len("/home") :]
    elif path == "/home/":
        path = "/"
    return path if path == "/" else path.rstrip("/")


def public_path(page):
    """Strip the site root (``/home``) and any trailing slash."""
    return _public_path(page.url_path)


def capture_previous_path(sender, instance, **kwargs):
    if not instance.pk:
        return
    previous = sender.objects.filter(pk=instance.pk).values_list("url_path", flat=True).first()
    if previous:
        instance._previous_url_path = previous


def revalidation_payload(page):
    new_path = public_path(page)
    previous_path = getattr(page, "_previous_url_path", None)
    old_path = _public_path(previous_path) if previous_path else None

    paths = {path for path in (new_path, old_path) if path and path != "/"}
    if "/" in (new_path, old_path):
        paths.add("/")

    return {
        "paths": sorted(paths),
        "tags": ["pages", f"pages_{page.slug}"],
        "old_path": old_path,
        "new_path": new_path,
    }


def send_revalidation(payload):
    url = getattr(settings, "REVALIDATION_URL", "")
    if not url:
        return None

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Revalidate-Secret": getattr(settings, "REVALIDATE_SECRET", ""),
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status


def page_published_handler(sender, instance, **kwargs):
    if not getattr(settings, "REVALIDATION_ENABLED", False):
        return
    send_revalidation(revalidation_payload(instance))


def page_unpublished_handler(sender, instance, **kwargs):
    if not getattr(settings, "REVALIDATION_ENABLED", False):
        return
    path = public_path(instance)
    send_revalidation({"paths": [path], "tags": ["pages", f"pages_{instance.slug}"]})


def is_content_page(sender):
    return issubclass(sender, ContentPage)
