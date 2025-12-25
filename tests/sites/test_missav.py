"""Tests for missav.ws site implementation."""

from pathlib import Path

from resources.lib.sites import missav


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "missav"


def load_fixture(name):
    """Load a fixture file from the missav fixtures directory."""
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

    monkeypatch.setattr(missav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(missav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(missav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(missav.utils, "eod", lambda: None)

    missav.List("https://missav.ws/en/new?page=1")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video
    assert downloads[0]["name"] == "FC2-PPV-12345 Beautiful Japanese Girl"
    assert downloads[0]["url"] == "/en/fc2-ppv-12345"
    assert downloads[0]["icon"] == "https://missav.ws/thumb1.jpg"
    assert downloads[0]["duration"] == "01:23:45"

    # Check second video (x-on:mouseenter)
    assert downloads[1]["name"] == "SSIS-67890 Hot JAV Actress"
    assert downloads[1]["url"] == "/en/ssis-67890"
    assert downloads[1]["icon"] == "https://missav.ws/thumb2.jpg"
    assert downloads[1]["duration"] == "45:30"

    # Check third video
    assert downloads[2]["name"] == "STARS-98765 Amazing Performance"
    assert downloads[2]["url"] == "/en/stars-98765"
    assert downloads[2]["duration"] == "58:12"


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

    monkeypatch.setattr(missav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(missav.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(missav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(missav.utils, "eod", lambda: None)

    missav.List("https://missav.ws/en/new?page=1")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert next_pages[0]["url"] == "/en/new?page=2"
    # Should show page 2/10
    assert "2/10" in next_pages[0]["name"] or "2" in next_pages[0]["name"]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(missav.site, "search_dir", fake_search_dir)

    missav.Search("https://missav.ws/en/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded search."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(missav, "List", fake_list)

    missav.Search("https://missav.ws/en/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "test%2Bquery" in list_calls[0]
