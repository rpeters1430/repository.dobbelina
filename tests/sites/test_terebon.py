"""Comprehensive tests for terebon.net site implementation."""
from pathlib import Path

from resources.lib.sites import terebon


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "terebon"


def load_fixture(name):
    """Load a fixture file from the terebon fixtures directory."""
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
            "contextm": kwargs.get("contextm"),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
            "contextm": kwargs.get("contextm"),
        })

    monkeypatch.setattr(terebon.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(terebon.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(terebon.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(terebon.utils, "eod", lambda: None)

    terebon.List("https://b.terebon.net/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (1080p quality)
    assert "Beautiful Japanese Actress" in downloads[0]["name"]
    assert "1080p" in downloads[0]["name"]
    assert "20:15" in downloads[0]["name"]
    assert "12345" in downloads[0]["url"]
    assert "thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["contextm"] is not None

    # Check second video (720p quality with data-original)
    assert "Tokyo Girl Amateur" in downloads[1]["name"]
    assert "720p" in downloads[1]["name"]
    assert "15:30" in downloads[1]["name"]
    assert "67890" in downloads[1]["url"]
    # Note: data-original has precedence, but if not loaded it falls back to src
    assert "thumb2.jpg" in downloads[1]["icon"] or "placeholder.jpg" in downloads[1]["icon"]

    # Check third video (4k quality)
    assert "Premium JAV 4K" in downloads[2]["name"]
    assert "4k" in downloads[2]["name"]
    assert "28:45" in downloads[2]["name"]
    assert "11111" in downloads[2]["url"]


def test_list_with_pagination(monkeypatch):
    """Test that List adds pagination with async parameters."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(terebon.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(terebon.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(terebon.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(terebon.utils, "eod", lambda: None)

    terebon.List("https://b.terebon.net/")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "mode=async" in next_pages[0]["url"]
    assert "block_id=list_videos_common_videos_list" in next_pages[0]["url"]
    assert "(2)" in next_pages[0]["name"]


def test_list_handles_no_data(monkeypatch):
    """Test that List handles 'There is no data in this list' message."""
    html = "There is no data in this list"

    notified = []

    def fake_get_html(url, referer=None):
        return html

    def fake_notify(msg):
        notified.append(msg)

    monkeypatch.setattr(terebon.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(terebon.utils, "notify", fake_notify)

    # Should not raise exception
    terebon.List("https://b.terebon.net/empty")

    assert len(notified) == 1
    assert "No data found" in notified[0]


def test_list_skips_captcha_items(monkeypatch):
    """Test that List skips items containing 'Captcha'."""
    html = """
    <html>
    <div class="col-lg-4">
        <a href="/video/12345/test">
            <img src="/thumb1.jpg" alt="Test Video">
            <div class="video-preview__duration">10:00</div>
        </a>
    </div>
    <div class="col-lg-4">
        Captcha verification required
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"name": name})

    monkeypatch.setattr(terebon.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(terebon.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(terebon.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(terebon.utils, "eod", lambda: None)

    terebon.List("https://b.terebon.net/")

    # Should have only 1 video (captcha item skipped)
    assert len(downloads) == 1
    # Name includes duration formatting
    assert "Test Video" in downloads[0]["name"]
    assert "10:00" in downloads[0]["name"]


def test_search_url_encoding(monkeypatch):
    """Test that Search properly encodes keywords."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(terebon, "List", fake_list)

    terebon.Search("https://b.terebon.net/search/?q=", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(terebon.site, "search_dir", fake_search_dir)

    terebon.Search("https://b.terebon.net/search/?q=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"
