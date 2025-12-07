"""Comprehensive tests for supjav site implementation."""
from pathlib import Path

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

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
        })

    def fake_add_dir(name, url, mode, iconimage=None, desc="", **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(supjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(supjav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(supjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.List("https://supjav.com/popular?sort=week")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video
    assert downloads[0]["name"] == "IPX-100 Beautiful Debut"
    assert "ipx-100-beautiful-debut" in downloads[0]["url"]
    assert "ipx100.jpg" in downloads[0]["icon"]
    # Should have cookie string in image URL
    assert "Cookie=" in downloads[0]["icon"]

    # Check second video
    assert downloads[1]["name"] == "ABP-200 Premium Experience"
    assert "abp-200-premium-experience" in downloads[1]["url"]

    # Check third video
    assert downloads[2]["name"] == "SNIS-300 Gorgeous Girl Special"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "(2/5)" in dirs[0]["name"]


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

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(supjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(supjav.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(supjav.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.List("https://supjav.com/popular/page/999/")

    # Should have no videos
    assert len(downloads) == 0


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses category menu items."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, desc=""):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(supjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(supjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.Cat("https://supjav.com/")

    # Should have 3 categories (menu-item-object-category items only)
    assert len(dirs) == 3

    # Check categories
    assert dirs[0]["name"] == "Big Tits"
    assert "/category/big-tits/" in dirs[0]["url"]

    assert dirs[1]["name"] == "Creampie"
    assert dirs[2]["name"] == "Uncensored"


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

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
        })

    monkeypatch.setattr(supjav.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(supjav.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(supjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(supjav.utils, "eod", lambda: None)

    supjav.List("https://supjav.com/popular?sort=week")

    # Should have pagination with page numbers
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    # Current page is 1, next is 2, last is 5
    assert "(2/5)" in next_pages[0]["name"]
