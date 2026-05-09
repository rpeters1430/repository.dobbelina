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

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
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

    monkeypatch.setattr(luxuretv.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(luxuretv.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(luxuretv.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.List("https://luxuretv.com/")

    # Check if we parsed videos
    assert len(downloads) > 0


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses category/channel links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(luxuretv.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(luxuretv.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.Cat("https://luxuretv.com/channels/")

    # Should have categories
    assert len(dirs) > 0


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

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    monkeypatch.setattr(luxuretv.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(
        luxuretv.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(luxuretv.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(luxuretv.utils, "eod", lambda: None)

    luxuretv.List("https://luxuretv.com/")

    # Should have no videos
    assert len(downloads) == 0
