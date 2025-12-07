"""Tests for longvideos.xxx site implementation."""
from pathlib import Path

from resources.lib.sites import longvideos


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "longvideos"


def load_fixture(name):
    """Load a fixture file from the longvideos fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "duration": kwargs.get("duration", ""),
            "quality": kwargs.get("quality", ""),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(longvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(longvideos.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(longvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(longvideos.utils, "eod", lambda: None)
    monkeypatch.setattr(longvideos.utils, "notify", lambda **k: None)

    longvideos.List("https://www.longvideos.xxx/latest-updates/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (FHD quality, clean duration)
    assert downloads[0]["name"] == "Stepmom Seduction"
    assert "12345" in downloads[0]["url"]
    assert "12345.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "10:30"
    assert downloads[0]["quality"] == "FHD"

    # Check second video (no quality, duration with text)
    assert downloads[1]["name"] == "college-party"  # From URL
    assert "67890" in downloads[1]["url"]
    assert downloads[1]["duration"] == "15:45"  # Cleaned from "min 15:45 sec"
    assert downloads[1]["quality"] == ""

    # Check third video (k4/FHD quality)
    assert downloads[2]["name"] == "Passionate Night"
    assert "11223" in downloads[2]["url"]
    assert downloads[2]["duration"] == "08:20"
    assert downloads[2]["quality"] == "FHD"

    # Should have pagination with context menu
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "(2)" in dirs[0]["name"]
    assert "/latest-updates/2/" in dirs[0]["url"]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses category links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(longvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(longvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(longvideos.utils, "eod", lambda: None)

    longvideos.Categories("https://www.longvideos.xxx/categories/")

    # Should have 3 categories
    assert len(dirs) == 3

    # Check categories
    assert dirs[0]["name"] == "MILF"
    assert "categories/milf" in dirs[0]["url"]

    assert dirs[1]["name"] == "Teen"
    assert "categories/teen" in dirs[1]["url"]

    assert dirs[2]["name"] == "Anal"
    assert "categories/anal" in dirs[2]["url"]


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(longvideos.site, "search_dir", fake_search_dir)

    longvideos.Search("https://www.longvideos.xxx/search/{}/relevance/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(longvideos, "List", fake_list)

    longvideos.Search("https://www.longvideos.xxx/search/{}/relevance/", keyword="test query")

    assert len(list_calls) == 1
    assert "test-query" in list_calls[0]


def test_list_handles_no_data(monkeypatch):
    """Test that List handles 'There is no data in this list.' message."""
    html = "<html><body>There is no data in this list.</body></html>"

    downloads = []
    notified = []

    def fake_get_html(url):
        return html

    def fake_notify(**kwargs):
        notified.append(kwargs)

    monkeypatch.setattr(longvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(longvideos.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(longvideos.utils, "notify", fake_notify)

    longvideos.List("https://www.longvideos.xxx/latest-updates/")

    # Should have no videos and notification shown
    assert len(downloads) == 0
    assert len(notified) == 1
    assert "No videos found" in notified[0]["msg"]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no video items."""
    html = "<html><body></body></html>"

    downloads = []

    def fake_get_html(url):
        return html

    monkeypatch.setattr(longvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(longvideos.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(longvideos.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(longvideos.utils, "eod", lambda: None)
    monkeypatch.setattr(longvideos.utils, "notify", lambda **k: None)

    longvideos.List("https://www.longvideos.xxx/latest-updates/")

    # Should have no videos
    assert len(downloads) == 0
