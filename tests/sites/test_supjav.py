"""Comprehensive tests for supjav site implementation."""

from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import supjav


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "supjav"


def load_fixture(name):
    """Load a fixture file from the supjav fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    # Mock the get_cookies function
    monkeypatch.setattr(supjav, "get_cookies", lambda: "cf_clearance=test123")

    def fake_get_html_cf(url, *args, **kwargs):
        return html, "cf_clearance=test123"

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
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

    monkeypatch.setattr(supjav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(supjav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(supjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.List("https://supjav.com/popular?sort=week")

    # Should have 3 videos
    assert len(downloads) == 3


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos gracefully."""
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div class="no-posts">No content</div>
    </body>
    </html>
    """

    downloads = []

    monkeypatch.setattr(supjav, "get_cookies", lambda: "")

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    monkeypatch.setattr(supjav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(
        supjav.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(supjav.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.List("https://supjav.com/popular/page/999/")

    # Should have no videos
    assert len(downloads) == 0


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses category menu items."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_dir(name, url, mode, iconimage=None, desc=""):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(supjav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(supjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.Cat("https://supjav.com/")

    # Should have 3 categories (menu-item-object-category items only)
    assert len(dirs) == 3


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(supjav.site, "search_dir", fake_search_dir)

    supjav.Search("https://supjav.com/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(supjav, "List", fake_list)

    supjav.Search("https://supjav.com/?s=", keyword="ipx 100")

    assert len(list_calls) == 1
    assert "ipx+100" in list_calls[0]


def test_list_pagination_with_page_numbers(monkeypatch):
    """Test that List correctly extracts pagination with current/last page."""
    html = load_fixture("listing.html")

    dirs = []

    monkeypatch.setattr(supjav, "get_cookies", lambda: "")

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
            }
        )

    monkeypatch.setattr(supjav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(supjav.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(supjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.List("https://supjav.com/popular?sort=week")

    # Should have pagination with page numbers
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    # Current page is 1, next is 2, last is 5
    assert "(2/5)" in next_pages[0]["name"]


def test_main(monkeypatch):
    """Test Main() function."""
    dirs = []
    monkeypatch.setattr(supjav.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(supjav, "List", lambda *a: None)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)
    
    supjav.Main()
    assert len(dirs) == 2


def test_get_cookies(monkeypatch):
    """Test get_cookies() function."""
    class MockCookie:
        def __init__(self, domain, name, value):
            self.domain = domain
            self.name = name
            self.value = value
            
    monkeypatch.setattr(supjav.utils, "cj", [
        MockCookie("supjav.com", "cf_clearance", "clear123"),
        MockCookie("supjav.com", "PHPSESSID", "sess456"),
        MockCookie("other.com", "foo", "bar")
    ])
    monkeypatch.setattr(supjav.utils, "kodilog", lambda *a: None)
    
    cookies = supjav.get_cookies()
    assert "cf_clearance=clear123" in cookies
    assert "PHPSESSID=sess456" in cookies


def test_playvid_success_and_parts(monkeypatch):
    """Test Playvid() success paths."""
    html_single = '<div class="btns"><a class="btn-server" data-link="link1">VV</a></div>'
    html_parts = """
    <div class="btns">
        <div class="cd-server">
            <a class="btn-server" data-link="part1_vv">VV</a>
        </div>
        <div class="cd-server">
            <a class="btn-server" data-link="part2_vv">VV</a>
        </div>
    </div>
    """
    
    selected = []
    
    class MockPlayer:
        def __init__(self, *a, **k):
            self.progress = MagicMock()
        def play_from_link_to_resolve(self, url):
            selected.append(url)

    monkeypatch.setattr(supjav.utils, "VideoPlayer", MockPlayer)
    monkeypatch.setattr(supjav.utils, "selector", lambda title, sources: list(sources.values())[0])
    monkeypatch.setattr(supjav.utils, "getVideoLink", lambda vurl, surl: "resolved_link")

    # 1. Single part
    monkeypatch.setattr(supjav.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html_single, ""))
    supjav.Playvid("https://supjav.com/v1", "Name")
    assert "resolved_link" in selected

    # 2. Multiple parts
    selected.clear()
    monkeypatch.setattr(supjav.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html_parts, ""))
    supjav.Playvid("https://supjav.com/v1", "Name")
    assert "resolved_link" in selected
