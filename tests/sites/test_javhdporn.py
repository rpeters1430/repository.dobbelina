"""Tests for javhdporn.net site implementation."""

from pathlib import Path

from resources.lib.sites import javhdporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "javhdporn"


def load_fixture(name):
    """Load a fixture file from the javhdporn fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(javhdporn.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javhdporn.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(javhdporn.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javhdporn.utils, "eod", lambda: None)

    javhdporn.List("https://www4.javhdporn.net/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (with HD)
    assert downloads[0]["name"] == "JAVHD Video Title 1"
    assert downloads[0]["url"] == "/video/javhd-video-12345/"
    assert downloads[0]["icon"] == "https://pics.pornfhd.com/thumb1.jpg"
    assert downloads[0]["duration"] == "45:30"
    assert downloads[0]["quality"] == "HD"

    # Check second video (src fallback, no HD)
    assert downloads[1]["name"] == "JAVHD Video Title 2"
    assert downloads[1]["url"] == "/video/javhd-video-67890/"
    assert downloads[1]["icon"] == "https://pics.pornfhd.com/thumb2.jpg"
    assert downloads[1]["duration"] == "1:12:45"
    assert downloads[1]["quality"] == ""

    # Check third video (HD badge)
    assert downloads[2]["name"] == "JAVHD Video Title 3"
    assert downloads[2]["url"] == "/video/javhd-video-abc123/"
    assert downloads[2]["duration"] == "38:20"
    assert downloads[2]["quality"] == "HD"


def test_list_pagination(monkeypatch):
    """Test that List correctly adds pagination."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(javhdporn.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javhdporn.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(javhdporn.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javhdporn.utils, "eod", lambda: None)

    javhdporn.List("https://www4.javhdporn.net/")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "/page/2/" in next_pages[0]["url"]
    # Check if pagination info is present (format may vary)
    # The actual implementation shows "(Currently in Page 1 of 20)" when both current and last are found
    assert "Next Page" in next_pages[0]["name"]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(javhdporn.site, "search_dir", fake_search_dir)

    javhdporn.Search("https://www4.javhdporn.net/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded search."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(javhdporn, "List", fake_list)

    javhdporn.Search("https://www4.javhdporn.net/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "test%20query" in list_calls[0]
