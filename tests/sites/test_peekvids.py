"""Tests for peekvids.com site implementation."""
from pathlib import Path

from resources.lib.sites import peekvids


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "peekvids"


def load_fixture(name):
    """Load a fixture file from the peekvids fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
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

    monkeypatch.setattr(peekvids.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(peekvids.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(peekvids.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(peekvids.utils, "eod", lambda: None)

    peekvids.List("https://www.peekvids.com/videos")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (data-src, HD quality)
    assert downloads[0]["name"] == "Hot Video Title"
    assert "123456" in downloads[0]["url"]
    assert "123456.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "12:34"
    assert downloads[0]["quality"] == "HD"

    # Check second video (data-original fallback, no quality)
    assert downloads[1]["name"] == "Amazing Scene"
    assert "789012" in downloads[1]["url"]
    assert "789012.jpg" in downloads[1]["icon"]
    assert downloads[1]["duration"] == "8:45"
    assert downloads[1]["quality"] == ""

    # Check third video (src fallback, HD)
    assert downloads[2]["name"] == "Full Scene"
    assert "345678" in downloads[2]["url"]
    assert "345678.jpg" in downloads[2]["icon"]
    assert downloads[2]["duration"] == "15:20"
    assert downloads[2]["quality"] == "HD"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "/videos/page/2" in dirs[0]["url"]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses category links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(peekvids.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(peekvids.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(peekvids.utils, "eod", lambda: None)

    peekvids.Cat("https://www.peekvids.com/categories")

    # Should have 3 categories
    assert len(dirs) == 3

    # Check categories
    assert dirs[0]["name"] == "MILF [COLOR hotpink]2,345 Videos[/COLOR]"
    assert "categories/milf" in dirs[0]["url"]

    assert dirs[1]["name"] == "Teen [COLOR hotpink]1,890 Videos[/COLOR]"
    assert "categories/teen" in dirs[1]["url"]

    assert dirs[2]["name"] == "Anal [COLOR hotpink]1,567 Videos[/COLOR]"
    assert "categories/anal" in dirs[2]["url"]


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(peekvids.site, "search_dir", fake_search_dir)

    peekvids.Search("https://www.peekvids.com/videos?q=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(peekvids, "List", fake_list)

    peekvids.Search("https://www.peekvids.com/videos?q=", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos."""
    html = "<html><body></body></html>"

    downloads = []

    def fake_get_html(url, referer=None):
        return html

    monkeypatch.setattr(peekvids.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(peekvids.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(peekvids.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(peekvids.utils, "eod", lambda: None)

    peekvids.List("https://www.peekvids.com/videos")

    # Should have no videos
    assert len(downloads) == 0
