"""Comprehensive tests for kissjav site implementation."""

from pathlib import Path

from resources.lib.sites import kissjav


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "kissjav"


def load_fixture(name):
    """Load a fixture file from the kissjav fixtures directory."""
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
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, desc="", **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(kissjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(kissjav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(kissjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(kissjav.utils, "eod", lambda: None)

    kissjav.List("https://kissjav.com/latest-updates/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video
    assert downloads[0]["name"] == "CAWD-123 Kawaii Debut"
    assert "cawd-123" in downloads[0]["url"]
    assert "cawd123.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "45:30"
    assert downloads[0]["quality"] == "HD"

    # Check second video
    assert downloads[1]["name"] == "MIDE-456 Ultimate Orgasm"
    assert "mide-456" in downloads[1]["url"]
    assert "mide456.jpg" in downloads[1]["icon"]
    assert downloads[1]["duration"] == "120:15"

    # Check third video
    assert downloads[2]["name"] == "SSNI-789 Beautiful Body"
    assert "ssni-789" in downloads[2]["url"]

    # Should have pagination (note: kissjav includes page numbers in pagination)
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) >= 1


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos gracefully."""
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div class="no-content">Nothing here</div>
    </body>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(kissjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        kissjav.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(kissjav.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(kissjav.utils, "eod", lambda: None)

    kissjav.List("https://kissjav.com/latest-updates/999/")

    # Should have no videos
    assert len(downloads) == 0


def test_categories_parses_category_items(monkeypatch):
    """Test that Categories correctly parses category items."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, desc=""):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage or "",
            }
        )

    monkeypatch.setattr(kissjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(kissjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(kissjav.utils, "eod", lambda: None)
    # Mock xbmcplugin.addSortMethod
    monkeypatch.setattr(kissjav.xbmcplugin, "addSortMethod", lambda *a, **k: None)

    kissjav.Categories("https://kissjav.com/categories/")

    # Should have 3 categories
    assert len(dirs) == 3

    # Check categories
    assert dirs[0]["name"] == "Big Tits"
    assert "/category/big-tits/" in dirs[0]["url"]
    assert "bigtits.jpg" in dirs[0]["icon"]

    assert dirs[1]["name"] == "Creampie"
    assert "/category/creampie/" in dirs[1]["url"]

    assert dirs[2]["name"] == "Schoolgirl"


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(kissjav.site, "search_dir", fake_search_dir)

    kissjav.Search("https://kissjav.com/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(kissjav, "List", fake_list)

    kissjav.Search("https://kissjav.com/search/", keyword="cawd 123")

    assert len(list_calls) == 1
    assert "cawd-123" in list_calls[0]


def test_list_with_pagination_context_menu(monkeypatch):
    """Test that List adds pagination with page numbers."""
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

    monkeypatch.setattr(kissjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(kissjav.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(kissjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(kissjav.utils, "eod", lambda: None)

    kissjav.List("https://kissjav.com/latest-updates/")

    # Should have next page with page info
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) >= 1
    # Page info may be present
    if next_pages and "Currently" in next_pages[0]["name"]:
        assert "1" in next_pages[0]["name"]
