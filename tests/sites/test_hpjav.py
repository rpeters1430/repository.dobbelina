"""Comprehensive tests for hpjav site implementation."""

from pathlib import Path

from resources.lib.sites import hpjav


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "hpjav"


def load_fixture(name):
    """Load a fixture file from the hpjav fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html, 200

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
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

    monkeypatch.setattr(hpjav.utils, "get_html_with_cloudflare_retry", fake_get_html)
    monkeypatch.setattr(hpjav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hpjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hpjav.utils, "eod", lambda: None)

    hpjav.List("https://hpjav.in/trend/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video
    assert downloads[0]["name"] == "IPX-001 Beautiful Debut Special"
    assert "/censored/ipx-001-beautiful-debut/" in downloads[0]["url"]
    assert "ipx001.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "45"

    # Check second video
    assert downloads[1]["name"] == "ABC-234 Uncensored Beauty"
    assert "/uncensored/abc-234-uncensored-beauty/" in downloads[1]["url"]
    assert downloads[1]["duration"] == "120"

    # Check third video
    assert downloads[2]["name"] == "FC2-789 Amateur Fun Time"
    assert "/fc2ppv/fc2-789-amateur-fun/" in downloads[2]["url"]
    assert downloads[2]["duration"] == "30"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "Page 1 of 10" in dirs[0]["name"]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos gracefully."""
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div class="no-results">Nothing found</div>
    </body>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html, 200

    monkeypatch.setattr(hpjav.utils, "get_html_with_cloudflare_retry", fake_get_html)
    monkeypatch.setattr(
        hpjav.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(hpjav.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(hpjav.utils, "eod", lambda: None)

    hpjav.List("https://hpjav.in/trend/page/999/")

    # Should have no videos
    assert len(downloads) == 0


def test_list_handles_timeout_gracefully(monkeypatch):
    """Test that List handles timeout errors gracefully."""

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        raise Exception("Timeout")

    monkeypatch.setattr(hpjav.utils, "get_html_with_cloudflare_retry", fake_get_html)
    monkeypatch.setattr(hpjav.utils, "eod", lambda: None)

    # Should not crash
    hpjav.List("https://hpjav.in/trend/")


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(hpjav.site, "search_dir", fake_search_dir)

    hpjav.Search("https://hpjav.in/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(hpjav, "List", fake_list)

    hpjav.Search("https://hpjav.in/?s=", keyword="ipx 001")

    assert len(list_calls) == 1
    assert "ipx+001" in list_calls[0]


def test_list_duration_cleaning(monkeypatch):
    """Test that List correctly cleans duration (removes 'min.' suffix)."""
    html = load_fixture("listing.html")

    downloads = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html, 200

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "duration": kwargs.get("duration", ""),
            }
        )

    monkeypatch.setattr(hpjav.utils, "get_html_with_cloudflare_retry", fake_get_html)
    monkeypatch.setattr(hpjav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hpjav.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(hpjav.utils, "eod", lambda: None)

    hpjav.List("https://hpjav.in/trend/")

    # Durations should have "min." suffix removed
    assert downloads[0]["duration"] == "45"
    assert downloads[1]["duration"] == "120"
    assert downloads[2]["duration"] == "30"


def test_list_pagination_with_page_info(monkeypatch):
    """Test that List correctly extracts pagination page info."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html, 200

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
            }
        )

    monkeypatch.setattr(hpjav.utils, "get_html_with_cloudflare_retry", fake_get_html)
    monkeypatch.setattr(hpjav.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(hpjav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hpjav.utils, "eod", lambda: None)

    hpjav.List("https://hpjav.in/trend/")

    # Should have pagination with page info
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "Page 1 of 10" in next_pages[0]["name"]
    assert "/page/2/" in next_pages[0]["url"]
