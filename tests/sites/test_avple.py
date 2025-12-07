"""Comprehensive tests for avple site implementation."""
from pathlib import Path

from resources.lib.sites import avple


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "avple"


def load_fixture(name):
    """Load a fixture file from the avple fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items from JSON data."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "duration": kwargs.get("duration", ""),
        })

    def fake_add_dir(name, url, mode, iconimage=None, desc="", **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(avple.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(avple.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(avple.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(avple.utils, "eod", lambda: None)

    avple.List("https://avple.tv/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video
    assert downloads[0]["name"] == "Beautiful Asian Girl IPX-001"
    assert "/video/12345" in downloads[0]["url"]
    assert "ipx001.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "45:30"

    # Check second video
    assert downloads[1]["name"] == "Premium JAV SNIS-456"
    assert "/video/67890" in downloads[1]["url"]
    assert downloads[1]["duration"] == "120:15"

    # Check third video (no duration)
    assert downloads[2]["name"] == "Uncensored Beauty ABC-789"
    assert "/video/11223" in downloads[2]["url"]
    assert downloads[2]["duration"] == ""

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "(2/50)" in dirs[0]["name"]


def test_list_handles_search_results_format(monkeypatch):
    """Test that List correctly handles search results JSON format."""
    html = load_fixture("search_results.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
        })

    monkeypatch.setattr(avple.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(avple.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(avple.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(avple.utils, "eod", lambda: None)

    avple.List("https://avple.tv/search?page=2&sort=date&key=test")

    # Should have 2 videos from search results
    assert len(downloads) == 2

    assert downloads[0]["name"] == "Search Result Video One"
    assert "/video/99988" in downloads[0]["url"]

    assert downloads[1]["name"] == "Search Result Video Two"
    assert "/video/77766" in downloads[1]["url"]

    # Should have pagination (currently on page 2 of 10)
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "(3/10)" in dirs[0]["name"]


def test_list_handles_404_error(monkeypatch):
    """Test that List handles 404 errors gracefully."""
    html = "<html><body><h1>404</h1><p>>404< Not Found</p></body></html>"

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html

    monkeypatch.setattr(avple.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(avple.utils, "eod", lambda: None)
    monkeypatch.setattr(avple.utils, "notify", lambda **kwargs: None)

    # Should handle 404 gracefully without crashing
    avple.List("https://avple.tv/nonexistent")


def test_list_handles_missing_json(monkeypatch):
    """Test that List handles missing JSON script tag."""
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div>No JSON here</div>
    </body>
    </html>
    """

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html

    monkeypatch.setattr(avple.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(avple.utils, "eod", lambda: None)
    monkeypatch.setattr(avple.utils, "notify", lambda *args, **kwargs: None)

    # Should handle missing JSON gracefully
    avple.List("https://avple.tv/")


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(avple.site, "search_dir", fake_search_dir)

    avple.Search("https://avple.tv/search?page=1&sort=date&key=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(avple, "List", fake_list)

    avple.Search("https://avple.tv/search?page=1&sort=date&key=", keyword="test query")

    assert len(list_calls) == 1
    assert "test%20query" in list_calls[0]


def test_cat_lists_all_tags(monkeypatch):
    """Test that Cat lists all predefined tags."""
    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, desc=""):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(avple.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(avple.utils, "eod", lambda: None)

    avple.Cat("https://avple.tv/")

    # Should have many tags (check a few known ones)
    assert len(dirs) > 50

    # Find specific tags
    tag_names = [d["name"] for d in dirs]
    assert "Big breasts" in tag_names
    assert "Creampie" in tag_names
    assert "Uncoded liberation" in tag_names  # Uncensored


def test_list_pagination_url_handling(monkeypatch):
    """Test that List correctly builds next page URLs for different URL formats."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, timeout=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "url": url,
        })

    monkeypatch.setattr(avple.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(avple.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(avple.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(avple.utils, "eod", lambda: None)

    # Test URL without page parameter
    avple.List("https://avple.tv/")

    # Should have next page link
    assert len(dirs) == 1
    # URL should remain the same since it doesn't have page= or /1/date
    assert dirs[0]["url"] == "https://avple.tv/"
