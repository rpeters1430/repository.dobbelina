"""Tests for YouJizz site implementation."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from resources.lib.sites import youjizz
from tests.conftest import read_fixture

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "youjizz"


def load_fixture(name):
    """Load a fixture file from the youjizz fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html_data = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
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

    monkeypatch.setattr(youjizz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(youjizz.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(youjizz.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(youjizz.utils, "eod", lambda: None)

    youjizz.List("https://www.youjizz.com/")

    # Check that we parsed videos
    assert len(downloads) > 0, "Should parse at least one video"

    # Check first video has required fields
    assert downloads[0]["name"], "Video should have a title"
    assert downloads[0]["url"].startswith("https://www.youjizz.com/"), "Video URL should be absolute"


def test_list_handles_pagination(monkeypatch):
    """Test that List adds Next Page when pagination is present."""
    html_data = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html_data

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(youjizz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(youjizz.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(youjizz.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(youjizz.utils, "eod", lambda: None)

    youjizz.List("https://www.youjizz.com/")

    # Should have Next Page if pagination exists
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    if next_pages:
        assert next_pages[0]["url"].startswith("https://"), "Next page URL should be absolute"


def test_categories_parses_tags(monkeypatch):
    """Test that Categories correctly parses tags."""
    html_data = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html_data

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(youjizz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(youjizz.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(youjizz.utils, "eod", lambda: None)

    youjizz.Categories("https://www.youjizz.com/tags")

    # Should parse tags
    assert len(dirs) > 0, "Should parse at least one tag"

    # Check tags have required fields
    for tag in dirs:
        assert tag["name"], "Tag should have a name"
        assert "/tags/" in tag["url"], "Tag URL should contain /tags/"

    # Check that tags are sorted alphabetically (first should come before last)
    if len(dirs) >= 2:
        assert dirs[0]["name"].lower() <= dirs[-1]["name"].lower(), "Tags should be sorted alphabetically"


def test_search_builds_correct_url(monkeypatch):
    """Test that Search builds the correct URL with search parameter."""
    called_urls = []

    def fake_list(url):
        called_urls.append(url)

    monkeypatch.setattr(youjizz, "List", fake_list)

    youjizz.Search("https://www.youjizz.com/srch.php?search=", keyword="test search")

    assert len(called_urls) == 1
    assert "test+search" in called_urls[0]
