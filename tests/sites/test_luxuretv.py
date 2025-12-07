"""Tests for luxuretv.com site implementation."""
from pathlib import Path

from resources.lib.sites import luxuretv


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "luxuretv"


def load_fixture(name):
    """Load a fixture file from the luxuretv fixtures directory."""
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
        })

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(luxuretv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(luxuretv.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(luxuretv.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.List("https://luxuretv.com/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (src, duration in <b> tag)
    assert downloads[0]["name"] == "Stepmom Passion"
    assert "12345" in downloads[0]["url"]
    assert "12345.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "10:30"

    # Check second video (data-src fallback, duration direct text)
    assert downloads[1]["name"] == "college-adventure"  # From URL
    assert "67890" in downloads[1]["url"]
    assert "67890.jpg" in downloads[1]["icon"]
    assert downloads[1]["duration"] == "15:45"

    # Check third video (content-item class variant)
    assert downloads[2]["name"] == "Passionate Night"
    assert "11223" in downloads[2]["url"]
    assert downloads[2]["duration"] == "08:20"

    # Should have pagination (Suivante = Next in French)
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "page2.html" in dirs[0]["url"]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses category/channel links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
        })

    monkeypatch.setattr(luxuretv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(luxuretv.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.Cat("https://luxuretv.com/channels/")

    # Should have 3 categories
    assert len(dirs) == 3

    # Check categories
    assert dirs[0]["name"] == "MILF"
    assert "channels/milf" in dirs[0]["url"]
    assert "milf.jpg" in dirs[0]["icon"]

    assert dirs[1]["name"] == "Teen"
    assert "channels/teen" in dirs[1]["url"]
    assert "teen.jpg" in dirs[1]["icon"]

    assert dirs[2]["name"] == "Anal"
    assert "channels/anal" in dirs[2]["url"]


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(luxuretv.site, "search_dir", fake_search_dir)

    luxuretv.Search("https://luxuretv.com/searchgate/videos/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(luxuretv, "List", fake_list)

    luxuretv.Search("https://luxuretv.com/searchgate/videos/", keyword="test query")

    assert len(list_calls) == 1
    assert "test-query" in list_calls[0]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos."""
    html = "<html><body></body></html>"

    downloads = []

    def fake_get_html(url):
        return html

    monkeypatch.setattr(luxuretv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(luxuretv.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(luxuretv.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.List("https://luxuretv.com/")

    # Should have no videos
    assert len(downloads) == 0


def test_list_handles_no_pagination(monkeypatch):
    """Test that List handles pages without pagination."""
    html = """
    <html>
    <body>
    <div class="content">
        <a href="/videos/123/test/" title="Test">
            <img src="test.jpg">
        </a>
        <div class="time">10:00</div>
    </div>
    </body>
    </html>
    """

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name})

    monkeypatch.setattr(luxuretv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(luxuretv.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(luxuretv.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.List("https://luxuretv.com/")

    # Should have no pagination
    assert len(dirs) == 0
