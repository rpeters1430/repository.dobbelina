"""Tests for pornmz.com site implementation."""

from pathlib import Path

from resources.lib.sites import pornmz


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "pornmz"


def load_fixture(name):
    """Load a fixture file from the pornmz fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(pornmz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornmz.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(pornmz.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornmz.utils, "eod", lambda: None)

    pornmz.List("https://pornmz.com/page/1/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (img src, HD quality from >HD< in HTML)
    assert downloads[0]["name"] == "Hot Stepmom Action"
    assert "12345" in downloads[0]["url"]
    assert "12345.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "10:30"
    assert downloads[0]["quality"] == "HD"

    # Check second video (img data-src, no HD)
    assert downloads[1]["name"] == "college-girls"  # From URL
    assert "67890" in downloads[1]["url"]
    assert "67890.jpg" in downloads[1]["icon"]
    assert downloads[1]["duration"] == "8:15"
    assert downloads[1]["quality"] == ""

    # Check third video (video poster fallback)
    assert downloads[2]["name"] == "Passionate Night"
    assert "11223" in downloads[2]["url"]
    assert "11223.jpg" in downloads[2]["icon"]
    assert downloads[2]["duration"] == "12:00"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "(2)" in dirs[0]["name"]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses category links."""
    html = load_fixture("categories.html")

    dirs = []
    url = "https://pornmz.com/categories/"

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(pornmz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornmz.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornmz.utils, "eod", lambda: None)

    pornmz.Categories(url)

    # Should have 3 categories (Categories function loops through all pages)
    assert len(dirs) == 3

    # Check categories
    assert dirs[0]["name"] == "MILF"
    assert "category/milf" in dirs[0]["url"]
    assert "filter=latest" in dirs[0]["url"]

    assert dirs[1]["name"] == "Teen"
    assert "category/teen" in dirs[1]["url"]

    assert dirs[2]["name"] == "Anal"
    assert "category/anal" in dirs[2]["url"]


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(pornmz.site, "search_dir", fake_search_dir)

    pornmz.Search("https://pornmz.com/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(pornmz, "List", fake_list)

    pornmz.Search("https://pornmz.com/?s=", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos."""
    html = "<html><body></body></html>"

    downloads = []

    def fake_get_html(url):
        return html

    monkeypatch.setattr(pornmz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        pornmz.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(pornmz.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(pornmz.utils, "eod", lambda: None)

    pornmz.List("https://pornmz.com/page/1/")

    # Should have no videos
    assert len(downloads) == 0


def test_list_handles_no_pagination(monkeypatch):
    """Test that List handles pages without pagination."""
    html = """
    <html>
    <body>
    <article data-video-id="123">
        <a href="/video/123/test/" title="Test">
            <img src="test.jpg">
        </a>
    </article>
    <div class="pagination">
        <span class="current">1</span>
    </div>
    </body>
    </html>
    """

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name})

    monkeypatch.setattr(pornmz.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornmz.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(pornmz.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornmz.utils, "eod", lambda: None)

    pornmz.List("https://pornmz.com/page/1/")

    # Should have no pagination (current page is last page)
    assert len(dirs) == 0
