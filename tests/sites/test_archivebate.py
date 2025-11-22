"""Tests for archivebate.com site implementation."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from resources.lib.sites import archivebate
from tests.conftest import read_fixture


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "archivebate"


def load_fixture(name):
    """Load a fixture file from the archivebate fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_videos_parses_posts(monkeypatch):
    """Test that ListVideos correctly parses WordPress API JSON response."""
    json_data = load_fixture("posts_list.json")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
        return json_data

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "desc": desc,
            "duration": kwargs.get("duration", ""),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(archivebate.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(archivebate.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(archivebate.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.ListVideos("https://archivebate.com/wp-json/wp/v2/posts?per_page=30", page=1)

    assert len(downloads) == 2

    # Check first video
    assert downloads[0]["name"] == "Sample Video One - Hot Content"
    assert downloads[0]["url"] == "https://archivebate.com/2024/11/sample-video-one/"
    assert downloads[0]["icon"] == "https://archivebate.com/wp-content/uploads/thumb1.jpg"
    assert "first sample video" in downloads[0]["desc"]

    # Check second video
    assert downloads[1]["name"] == "Sample Video Two - Amazing Show"
    assert downloads[1]["url"] == "https://archivebate.com/2024/11/sample-video-two/"
    assert downloads[1]["icon"] == "https://archivebate.com/wp-content/uploads/thumb2.jpg"
    assert downloads[1]["duration"] == "25:45"

    # Check pagination - should have "Next Page" since we got POSTS_PER_PAGE items
    # Note: Our fixture only has 2 items, which is less than POSTS_PER_PAGE (30), so no next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 0  # No next page expected with only 2 items


def test_list_videos_handles_empty_response(monkeypatch):
    """Test that ListVideos handles empty results gracefully."""
    json_data = load_fixture("posts_empty.json")

    downloads = []
    notified = []

    def fake_get_html(url, referer=None):
        return json_data

    def fake_notify(msg):
        notified.append(msg)

    monkeypatch.setattr(archivebate.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(archivebate.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(archivebate.utils, "notify", fake_notify)
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.ListVideos("https://archivebate.com/wp-json/wp/v2/posts", page=1)

    assert len(downloads) == 0
    assert "Nothing found" in notified


def test_categories_parses_api_response(monkeypatch):
    """Test that Categories correctly parses category JSON."""
    json_data = load_fixture("categories_list.json")

    dirs = []

    def fake_get_html(url, referer=None):
        return json_data

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(archivebate.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(archivebate.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.Categories("https://archivebate.com/wp-json/wp/v2/categories")

    assert len(dirs) == 3

    # Check categories are parsed correctly
    assert "Teen" in dirs[0]["name"]
    assert "(156)" in dirs[0]["name"]
    assert "categories=101" in dirs[0]["url"]

    assert "MILF" in dirs[1]["name"]
    assert "(89)" in dirs[1]["name"]
    assert "categories=102" in dirs[1]["url"]

    assert "Latina" in dirs[2]["name"]
    assert "(45)" in dirs[2]["name"]


def test_search_builds_correct_url(monkeypatch):
    """Test that Search builds the correct API URL with search parameter."""
    called_urls = []

    def fake_list_videos(url, page=1):
        called_urls.append(url)

    monkeypatch.setattr(archivebate, "ListVideos", fake_list_videos)

    archivebate.Search("https://archivebate.com/wp-json/wp/v2/posts", keyword="test query")

    assert len(called_urls) == 1
    assert "search=test+query" in called_urls[0]
    assert "page=1" in called_urls[0]
