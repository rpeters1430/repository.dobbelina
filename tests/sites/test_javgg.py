"""Tests for javgg.co site implementation."""
from pathlib import Path

from resources.lib.sites import javgg


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "javgg"


def load_fixture(name):
    """Load a fixture file from the javgg fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(javgg.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javgg.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(javgg.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javgg.utils, "eod", lambda: None)

    javgg.List("https://javgg.co/new-post/page/1/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video
    assert downloads[0]["name"] == "JAVGG Video Title 1"
    assert downloads[0]["url"] == "/javgg-video-12345/"
    assert downloads[0]["icon"] == "https://javgg.co/thumb1.jpg"

    # Check second video (data-src)
    assert downloads[1]["name"] == "JAVGG Video Title 2"
    assert downloads[1]["url"] == "/javgg-video-67890/"
    assert downloads[1]["icon"] == "https://javgg.co/thumb2.jpg"

    # Check third video
    assert downloads[2]["name"] == "JAVGG Video Title 3"
    assert downloads[2]["url"] == "/javgg-video-abc123/"


def test_list_pagination(monkeypatch):
    """Test that List correctly adds pagination."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(javgg.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javgg.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(javgg.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javgg.utils, "eod", lambda: None)

    javgg.List("https://javgg.co/new-post/page/1/")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert next_pages[0]["url"] == "/new-post/page/2/"
    assert "Page 1 of 5" in next_pages[0]["name"]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(javgg.site, "search_dir", fake_search_dir)

    javgg.Search("https://javgg.co/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded search."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(javgg, "List", fake_list)

    javgg.Search("https://javgg.co/?s=", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
