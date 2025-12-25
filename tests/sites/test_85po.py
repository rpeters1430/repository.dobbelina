"""Comprehensive tests for 85po.com site implementation."""

from pathlib import Path
import importlib

# Import module with numeric name using importlib
po85 = importlib.import_module("resources.lib.sites.85po")


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "85po"


def load_fixture(name):
    """Load a fixture file from the 85po fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "contextm": kwargs.get("contextm"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "contextm": kwargs.get("contextm"),
            }
        )

    monkeypatch.setattr(po85.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(po85.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(po85.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(po85.utils, "eod", lambda: None)

    po85.List("https://85po.com/en/latest-updates/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (4K quality normalized to 2160p)
    assert "Japanese Beauty 4K" in downloads[0]["name"]
    assert "2160p" in downloads[0]["name"]
    assert "25:30" in downloads[0]["name"]
    assert "12345" in downloads[0]["url"]
    assert "thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["contextm"] is not None

    # Check second video (2K quality normalized to 1080p)
    assert "Tokyo Amateur 2K" in downloads[1]["name"]
    assert "1080p" in downloads[1]["name"]
    assert "18:45" in downloads[1]["name"]
    assert "67890" in downloads[1]["url"]

    # Check third video (1K quality normalized to 720p)
    assert "JAV Uncensored Premium" in downloads[2]["name"]
    assert "720p" in downloads[2]["name"]
    assert "32:10" in downloads[2]["name"]
    assert "11111" in downloads[2]["url"]


def test_list_with_pagination(monkeypatch):
    """Test that List adds pagination with async parameters."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(po85.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(po85.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(po85.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(po85.utils, "eod", lambda: None)

    po85.List("https://85po.com/en/latest-updates/")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "mode=async" in next_pages[0]["url"]
    assert "block_id=list_videos_common_videos_list" in next_pages[0]["url"]
    # Pagination shows current and last page number: (2) or (2/3)
    assert "(2" in next_pages[0]["name"]


def test_list_handles_no_data(monkeypatch):
    """Test that List handles 'There is no data in this list' message."""
    html = "There is no data in this list."

    notified = []

    def fake_get_html(url):
        return html

    def fake_notify(msg):
        notified.append(msg)

    monkeypatch.setattr(po85.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(po85.utils, "notify", fake_notify)

    # Should not raise exception
    po85.List("https://85po.com/en/empty/")

    assert len(notified) == 1
    assert "No videos found" in notified[0]


def test_list_quality_normalization(monkeypatch):
    """Test that List correctly normalizes quality labels."""
    html = """
    <html>
    <div class="thumb item">
        <a href="/video/1/test-1k" title="Test 1K">
            <img src="/thumb1.jpg">
            <div class="qualtiy">1K</div>
            <span class="fa-clock">10:00</span>
        </a>
    </div>
    <div class="thumb item">
        <a href="/video/2/test-2k" title="Test 2K">
            <img src="/thumb2.jpg">
            <div class="qualtiy">2K</div>
            <span class="fa-clock">15:00</span>
        </a>
    </div>
    <div class="thumb item">
        <a href="/video/3/test-4k" title="Test 4K">
            <img src="/thumb3.jpg">
            <div class="qualtiy">4K</div>
            <span class="fa-clock">20:00</span>
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"name": name})

    monkeypatch.setattr(po85.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(po85.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(po85.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(po85.utils, "eod", lambda: None)

    po85.List("https://85po.com/en/latest-updates/")

    assert len(downloads) == 3
    # Check quality normalization
    assert "720p" in downloads[0]["name"]  # 1K -> 720p
    assert "1080p" in downloads[1]["name"]  # 2K -> 1080p
    assert "2160p" in downloads[2]["name"]  # 4K -> 2160p


def test_search_url_formatting(monkeypatch):
    """Test that Search properly formats search URLs."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(po85, "List", fake_list)

    po85.Search("https://85po.com/en/search/{}/", keyword="test query")

    assert len(list_calls) == 1
    # Spaces should be replaced with hyphens
    assert "test-query" in list_calls[0]


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(po85.site, "search_dir", fake_search_dir)

    po85.Search("https://85po.com/en/search/{}/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"
