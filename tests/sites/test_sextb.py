"""Comprehensive tests for sextb.net site implementation."""

from pathlib import Path

from resources.lib.sites import sextb


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "sextb"


def load_fixture(name):
    """Load a fixture file from the sextb fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
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

    monkeypatch.setattr(sextb.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sextb.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(sextb.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(sextb.utils, "eod", lambda: None)

    sextb.List("https://sextb.net/uncensored/pg-1")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (data-src attribute)
    assert downloads[0]["name"] == "Japanese Beauty Uncensored"
    assert "abc-123" in downloads[0]["url"]
    assert "thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "25:30"

    # Check second video (src fallback)
    assert downloads[1]["name"] == "Tokyo Amateur Girl"
    assert "def-456" in downloads[1]["url"]
    assert "thumb2.jpg" in downloads[1]["icon"]
    assert downloads[1]["duration"] == "18:45"

    # Check third video
    assert downloads[2]["name"] == "JAV Censored Premium"
    assert "ghi-789" in downloads[2]["url"]
    assert downloads[2]["duration"] == "32:10"


def test_list_with_pagination(monkeypatch):
    """Test that List adds pagination when present."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(sextb.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sextb.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(sextb.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(sextb.utils, "eod", lambda: None)

    sextb.List("https://sextb.net/uncensored/pg-1")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "pg-2" in next_pages[0]["url"]
    assert "(Currently in Page 1)" in next_pages[0]["name"]


def test_list_handles_no_videos(monkeypatch):
    """Test that List handles 'No Video were found' message."""
    html = "No Video were found that matched your search query"

    def fake_get_html(url, referer=None):
        return html

    monkeypatch.setattr(sextb.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sextb.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(sextb.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(sextb.utils, "eod", lambda: None)

    # Should not raise exception
    sextb.List("https://sextb.net/search/nonexistent")


def test_list_handles_empty_html(monkeypatch):
    """Test that List handles very short HTML responses."""
    html = "<html></html>"

    def fake_get_html(url, referer=None):
        return html

    monkeypatch.setattr(sextb.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sextb.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(sextb.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(sextb.utils, "eod", lambda: None)

    # Should not raise exception
    sextb.List("https://sextb.net/uncensored/pg-999")


def test_search_url_formatting(monkeypatch):
    """Test that Search properly formats search URLs."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(sextb, "List", fake_list)

    sextb.Search("https://sextb.net/search/", keyword="test query")

    assert len(list_calls) == 1
    # Spaces should be replaced with hyphens
    assert "test-query" in list_calls[0]


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(sextb.site, "search_dir", fake_search_dir)

    sextb.Search("https://sextb.net/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_list_url_normalization(monkeypatch):
    """Test that List normalizes relative URLs to absolute."""
    html = """
    <html>
    <div class="tray-item">
        <a href="/video/test/video-title">
            <img src="/thumbs/test.jpg">
            <div class="title">Test Video</div>
            <div class="time">10:00</div>
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"url": url})

    monkeypatch.setattr(sextb.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sextb.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(sextb.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(sextb.utils, "eod", lambda: None)

    sextb.List("https://sextb.net/uncensored/pg-1")

    assert len(downloads) == 1
    # Video URL should be normalized to absolute
    assert downloads[0]["url"].startswith("https://sextb.net/video/")


def test_get_page_html_cloudflare_fallback(monkeypatch):
    """Cloudflare challenge pages should trigger flaresolve fallback."""
    challenge_html = "<html><title>Checking your browser before accessing</title></html>"
    solved_html = "<html><body>ok</body></html>"
    calls = []

    def fake_get_html(url, referer=None, error=None):
        calls.append(("getHtml", url, referer, error))
        return challenge_html

    def fake_flaresolve(url, referer=None):
        calls.append(("flaresolve", url, referer))
        return solved_html

    monkeypatch.setattr(sextb.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sextb.utils, "flaresolve", fake_flaresolve)

    html = sextb._get_page_html("https://sextb.net/uncensored/pg-1", "https://sextb.net/")

    assert html == solved_html
    assert calls[0][0] == "getHtml"
    assert calls[0][3] is True
    assert calls[1][0] == "flaresolve"
