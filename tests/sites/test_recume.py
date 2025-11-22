"""Tests for recu.me site implementation."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from resources.lib.sites import recume
from tests.conftest import read_fixture


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "recume"


def load_fixture(name):
    """Load a fixture file from the recume fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_posts_with_metadata(monkeypatch):
    """Test that List correctly parses WordPress API posts with metadata extraction."""
    json_data = load_fixture("posts_list.json")

    downloads = []
    dirs = []

    def fake_get_html(url, headers=None):
        return json_data

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "desc": desc,
            "duration": kwargs.get("duration", ""),
            "quality": kwargs.get("quality", ""),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(recume.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(recume.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(recume.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(recume.utils, "eod", lambda: None)

    recume.List("https://recu.me/wp-json/wp/v2/posts?page=1&per_page=36")

    assert len(downloads) == 2

    # Check first video with all metadata
    assert downloads[0]["name"] == "Hot Video Performance"
    assert downloads[0]["url"] == "https://recu.me/hot-video-performance/"
    assert downloads[0]["icon"] == "https://recu.me/wp-content/uploads/2024/11/thumb1.jpg"
    assert downloads[0]["duration"] == "18:45"
    assert downloads[0]["quality"] == "1080P"
    assert "Published: 2024-11-15" in downloads[0]["desc"]
    assert "Amazing performance" in downloads[0]["desc"]

    # Check second video
    assert downloads[1]["name"] == "Amazing Show Recording"
    assert downloads[1]["url"] == "https://recu.me/amazing-show-recording/"
    assert downloads[1]["icon"] == "https://recu.me/wp-content/uploads/2024/11/thumb2.jpg"
    assert downloads[1]["duration"] == "25:12"
    assert downloads[1]["quality"] == "720P"


def test_list_handles_pagination(monkeypatch):
    """Test that List adds Next Page when appropriate."""
    # Create a fixture with exactly API_PAGE_SIZE items to trigger pagination
    posts = []
    for i in range(recume.API_PAGE_SIZE):
        posts.append({
            "id": 1000 + i,
            "link": f"https://recu.me/video-{i}/",
            "title": {"rendered": f"Video {i}"},
            "content": {"rendered": ""},
            "date": "2024-11-01T00:00:00"
        })

    import json
    json_data = json.dumps(posts)

    dirs = []

    def fake_get_html(url, headers=None):
        return json_data

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(recume.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(recume.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(recume.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(recume.utils, "eod", lambda: None)

    recume.List("https://recu.me/wp-json/wp/v2/posts?page=1&per_page=36")

    # Should have Next Page since we got exactly per_page items
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "page=2" in next_pages[0]["url"]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles empty results gracefully."""
    json_data = load_fixture("posts_empty.json")

    downloads = []

    def fake_get_html(url, headers=None):
        return json_data

    monkeypatch.setattr(recume.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(recume.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(recume.utils, "eod", lambda: None)

    recume.List("https://recu.me/wp-json/wp/v2/posts")

    assert len(downloads) == 0


def test_categories_parses_and_sorts(monkeypatch):
    """Test that Categories correctly parses and sorts categories."""
    json_data = load_fixture("categories_list.json")

    dirs = []
    fetch_count = [0]

    def fake_get_html(url, headers=None):
        fetch_count[0] += 1
        # Return empty on second call to stop pagination
        if fetch_count[0] > 1:
            return "[]"
        return json_data

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(recume.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(recume.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(recume.utils, "eod", lambda: None)

    recume.Categories("https://recu.me/wp-json/wp/v2/categories?per_page=100")

    assert len(dirs) == 3

    # Check that categories are sorted alphabetically
    assert "Asian" in dirs[0]["name"]
    assert "Blonde" in dirs[1]["name"]
    assert "Brunette" in dirs[2]["name"]

    # Check counts are displayed
    assert "(95)" in dirs[0]["name"]
    assert "(234)" in dirs[1]["name"]
    assert "(187)" in dirs[2]["name"]

    # Check URLs contain category IDs
    assert "categories=12" in dirs[0]["url"]
    assert "categories=5" in dirs[1]["url"]
    assert "categories=8" in dirs[2]["url"]


def test_search_builds_correct_url(monkeypatch):
    """Test that Search builds the correct API URL with search parameter."""
    called_urls = []

    def fake_list(url):
        called_urls.append(url)

    monkeypatch.setattr(recume, "List", fake_list)

    recume.Search("https://recu.me/", keyword="test search")

    assert len(called_urls) == 1
    assert "search=test+search" in called_urls[0]
    assert "page=1" in called_urls[0]


def test_extract_duration_patterns():
    """Test the _extract_duration helper with various formats."""
    # HH:MM:SS format
    assert recume._extract_duration("Duration: 01:23:45") == "01:23:45"

    # MM:SS format
    assert recume._extract_duration("Length: 15:30") == "15:30"

    # XhYm format
    assert recume._extract_duration("Runtime: 1h25m30s") == "1H25M30S"

    # No duration
    assert recume._extract_duration("No duration here") == ""
    assert recume._extract_duration("") == ""


def test_extract_quality_patterns():
    """Test the _extract_quality helper."""
    assert recume._extract_quality("Video in 1080p quality") == "1080P"
    assert recume._extract_quality("Available in 720p") == "720P"
    assert recume._extract_quality("360p resolution") == "360P"
    assert recume._extract_quality("HD video") == ""
    assert recume._extract_quality("") == ""
