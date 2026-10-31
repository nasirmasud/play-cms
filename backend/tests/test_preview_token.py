import datetime

import pytest
from django.core.management import call_command
from wagtail.models import Page
from wagtail_headless_preview.models import PagePreview

from cms.models import ContentPage


def _make_page(slug="preview-page", title="Preview Page"):
    root = Page.get_first_root_node()
    page = ContentPage(
        title=title,
        slug=slug,
        body=[
            (
                "hero",
                {
                    "heading": "Preview",
                    "align": "center",
                    "size": "lg",
                    "background": "none",
                    "spacing": "md",
                },
            )
        ],
    )
    root.add_child(instance=page)
    page.save_revision().publish()
    return page


@pytest.mark.django_db
def test_preview_token_valid(client):
    page = _make_page()
    preview = page.create_page_preview()
    url = "/api/v2/page_preview/0/?content_type=cms.contentpage&token=" + preview.token
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "preview-page"
    assert data["title"] == "Preview Page"
    assert len(data["body"]) == 1
    assert data["body"][0]["type"] == "hero"


@pytest.mark.django_db
def test_preview_token_tampered(client):
    page = _make_page()
    preview = page.create_page_preview()
    url = "/api/v2/page_preview/0/?content_type=cms.contentpage&token=" + preview.token + "tampered"
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_preview_token_missing_token(client):
    url = "/api/v2/page_preview/0/?content_type=cms.contentpage"
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_preview_token_missing_content_type(client):
    page = _make_page()
    preview = page.create_page_preview()
    url = "/api/v2/page_preview/0/?token=" + preview.token
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_preview_token_wrong_content_type(client):
    page = _make_page()
    preview = page.create_page_preview()
    url = "/api/v2/page_preview/0/?content_type=cms.otherpage&token=" + preview.token
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_preview_token_expired(client):
    page = _make_page()
    preview = page.create_page_preview()
    preview.created_at = datetime.date.today() - datetime.timedelta(days=2)
    preview.save()
    PagePreview.garbage_collect()

    url = "/api/v2/page_preview/0/?content_type=cms.contentpage&token=" + preview.token
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_cleanup_previews_deletes_stale_only():
    page = _make_page()
    fresh = page.create_page_preview()

    stale_page = _make_page(slug="stale-page", title="Stale Page")
    stale = stale_page.create_page_preview()
    stale.created_at = datetime.date.today() - datetime.timedelta(days=2)
    stale.save()

    # dry-run: nothing deleted
    call_command("cleanup_previews", "--dry-run")
    assert PagePreview.objects.filter(pk=fresh.pk).exists()
    assert PagePreview.objects.filter(pk=stale.pk).exists()

    # real run: only stale deleted
    call_command("cleanup_previews")
    assert PagePreview.objects.filter(pk=fresh.pk).exists()
    assert not PagePreview.objects.filter(pk=stale.pk).exists()
