from django.http import JsonResponse
from wagtail.models import Site

from .models import FooterSettings, HeaderSettings, ThemeSettings
from .serializers import image_payload


def _stream_payload(stream):
    return [
        {
            "type": block.block_type,
            "value": block.block.get_api_representation(block.value),
            "id": block.id,
        }
        for block in stream
    ]


def _resolve_site(request):
    host = request.GET.get("site")
    if host:
        hostname, _, port = host.partition(":")
        site = Site.objects.filter(hostname=hostname).first()
        if site is not None:
            return site
    return Site.find_for_request(request)


def site_settings_view(request):
    site = _resolve_site(request)
    if site is None:
        return JsonResponse({"detail": "Site not found."}, status=404)

    header = HeaderSettings.for_site(site)
    footer = FooterSettings.for_site(site)
    theme = ThemeSettings.for_site(site)

    return JsonResponse(
        {
            "header": {
                "logo": image_payload(header.logo),
                "nav_items": _stream_payload(header.nav_items),
            },
            "footer": {
                "columns": _stream_payload(footer.columns),
                "socials": _stream_payload(footer.socials),
                "copyright_text": footer.copyright_text,
            },
            "theme": {
                "primary": theme.primary,
                "background": theme.background,
                "foreground": theme.foreground,
                "radius": theme.radius,
                "font_heading": theme.font_heading,
                "font_body": theme.font_body,
            },
        }
    )
