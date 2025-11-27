"""Tests for Motherless site implementation."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from resources.lib.sites import motherless
from tests.conftest import read_fixture

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "motherless"


def load_fixture(name):
    """Load a fixture file from the motherless fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html_data = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
        return html_data

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "duration": kwargs.get("duration", ""),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(motherless.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(motherless.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(motherless.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(motherless.utils, "eod", lambda: None)

    motherless.List("https://motherless.com/videos/recent")

    # Check that we parsed videos
    assert len(downloads) > 0, "Should parse at least one video"

    # Check first video has required fields
    assert downloads[0]["name"], "Video should have a title"
    assert "motherless.com" in downloads[0]["url"], "Video URL should be for motherless.com"


def test_list_handles_pagination(monkeypatch):
    """Test that List adds Next Page when pagination is present."""
    html_data = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html_data

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(motherless.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(motherless.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(motherless.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(motherless.utils, "eod", lambda: None)

    motherless.List("https://motherless.com/videos/recent")

    # Should have Next Page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) > 0, "Should have next page"
    assert "page=" in next_pages[0]["url"], "Next page URL should contain page parameter"


def test_categories_parses_and_sorts(monkeypatch):
    """Test that Categories correctly parses categories."""
    html_data = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html_data

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(motherless.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(motherless.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(motherless.utils, "eod", lambda: None)

    motherless.Categories("https://motherless.com/categories")

    # Should parse categories
    assert len(dirs) > 0, "Should parse at least one category"

    # Check categories have required fields
    for cat in dirs:
        assert cat["name"], "Category should have a name"
        assert "/porn/" in cat["url"], "Category URL should contain /porn/"

    # Check that categories are sorted alphabetically
    if len(dirs) >= 2:
        assert dirs[0]["name"].lower() <= dirs[-1]["name"].lower(), "Categories should be sorted alphabetically"


def test_search_builds_correct_url(monkeypatch):
    """Test that Search builds the correct URL with search parameter."""
    called_urls = []

    def fake_list(url):
        called_urls.append(url)

    monkeypatch.setattr(motherless, "List", fake_list)

    motherless.Search("https://motherless.com/search/videos?term=", keyword="test search")

    assert len(called_urls) == 1
    assert "test+search" in called_urls[0]
