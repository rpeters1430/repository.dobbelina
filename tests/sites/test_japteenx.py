"""Comprehensive tests for japteenx.com site implementation."""
from pathlib import Path

from resources.lib.sites import japteenx


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "japteenx"


def load_fixture(name):
    """Load a fixture file from the japteenx fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "duration": kwargs.get("duration"),
            "quality": kwargs.get("quality"),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(japteenx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(japteenx.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(japteenx.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(japteenx.utils, "eod", lambda: None)

    japteenx.List("https://www.japteenx.com/videos?o=mr&type=public&page=1")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (with HD marker)
    assert downloads[0]["name"] == "Cute Japanese Teen"
    assert "12345" in downloads[0]["url"]
    assert "thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "15:30"
    assert downloads[0]["quality"] == "HD"

    # Check second video (without HD marker)
    assert downloads[1]["name"] == "Japanese Schoolgirl"
    assert "67890" in downloads[1]["url"]
    assert downloads[1]["duration"] == "22:15"
    assert downloads[1]["quality"] == ""

    # Check third video (HD in text)
    assert downloads[2]["name"] == "JAV Uncensored HD"
    assert "11111" in downloads[2]["url"]
    assert downloads[2]["duration"] == "18:45"
    assert downloads[2]["quality"] == "HD"


def test_list_with_pagination(monkeypatch):
    """Test that List adds pagination when present."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(japteenx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(japteenx.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(japteenx.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(japteenx.utils, "eod", lambda: None)

    japteenx.List("https://www.japteenx.com/videos?o=mr&type=public&page=1")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "page=2" in next_pages[0]["url"]


def test_list_handles_no_videos(monkeypatch):
    """Test that List handles pages with no videos gracefully."""
    html = "<html><body><div class='container'></div></body></html>"

    def fake_get_html(url, referer=None):
        return html

    monkeypatch.setattr(japteenx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(japteenx.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(japteenx.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(japteenx.utils, "eod", lambda: None)

    # Should not raise exception
    japteenx.List("https://www.japteenx.com/videos?page=999")


def test_list_url_normalization(monkeypatch):
    """Test that List normalizes relative URLs to absolute."""
    html = """
    <html>
    <div class="well well-sm">
        <a href="/video/test/video-title">
            <img src="/thumbs/test.jpg" title="Test Video">
            <div class="duration">10:00</div>
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"url": url, "icon": iconimage})

    monkeypatch.setattr(japteenx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(japteenx.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(japteenx.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(japteenx.utils, "eod", lambda: None)

    japteenx.List("https://www.japteenx.com/videos?page=1")

    assert len(downloads) == 1
    # Relative URLs should be converted to absolute
    assert downloads[0]["url"].startswith("https://www.japteenx.com/")


def test_search_url_encoding(monkeypatch):
    """Test that Search properly encodes keywords."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(japteenx, "List", fake_list)

    japteenx.Search("https://www.japteenx.com/search/videos?search_query=", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
    assert "type=public" in list_calls[0]


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(japteenx.site, "search_dir", fake_search_dir)

    japteenx.Search("https://www.japteenx.com/search/videos?search_query=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"
