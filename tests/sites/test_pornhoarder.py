"""Tests for pornhoarder.tv site implementation."""

from pathlib import Path

from resources.lib.sites import pornhoarder


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "pornhoarder"


def load_fixture(name):
    """Load a fixture file from the pornhoarder fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_post_html(url, headers=None, form_data=None):
        return html

    def fake_head(url, allow_redirects=True):
        class Response:
            url = "https://www.pornhoarder.tv/"

        return Response()

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

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(pornhoarder.utils, "postHtml", fake_post_html)
    monkeypatch.setattr(pornhoarder.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(pornhoarder.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornhoarder.utils, "eod", lambda: None)

    pornhoarder.List("test", page=1)

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (data-src)
    assert downloads[0]["name"] == "Stepmom Adventure"
    assert "12345" in downloads[0]["url"]
    assert "12345.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "10:25"

    # Check second video
    assert downloads[1]["name"] == "College Party"
    assert "67890" in downloads[1]["url"]
    assert downloads[1]["duration"] == "15:30"

    # Check third video (src fallback)
    assert downloads[2]["name"] == "Hot Encounter"
    assert "11223" in downloads[2]["url"]
    assert "11223.jpg" in downloads[2]["icon"]
    assert downloads[2]["duration"] == "8:45"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "(2)" in dirs[0]["name"]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses category links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(pornhoarder.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornhoarder.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornhoarder.utils, "eod", lambda: None)

    pornhoarder.Categories("https://www.pornhoarder.tv/categories/")

    # Should have 3 categories and 1 pagination
    assert len(dirs) == 4

    # Check categories
    assert dirs[0]["name"] == "MILF"
    assert dirs[0]["url"] == "milf"  # Search term extracted from URL

    assert dirs[1]["name"] == "Teen"
    assert dirs[1]["url"] == "teen"

    assert dirs[2]["name"] == "Anal"
    assert dirs[2]["url"] == "anal"

    # Check pagination
    assert "Next Page" in dirs[3]["name"]


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(pornhoarder.site, "search_dir", fake_search_dir)

    pornhoarder.Search("https://www.pornhoarder.tv/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url, page=1):
        list_calls.append((url, page))

    monkeypatch.setattr(pornhoarder, "List", fake_list)

    pornhoarder.Search("https://www.pornhoarder.tv/", keyword="test query")

    assert len(list_calls) == 1
    assert list_calls[0][0] == "test query"
    assert list_calls[0][1] == 1


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos."""
    html = "<html><body></body></html>"

    downloads = []

    def fake_post_html(url, headers=None, form_data=None):
        return html

    def fake_head(url, allow_redirects=True):
        class Response:
            url = "https://www.pornhoarder.tv/"

        return Response()

    monkeypatch.setattr(pornhoarder.utils, "postHtml", fake_post_html)
    monkeypatch.setattr(
        pornhoarder.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(pornhoarder.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(pornhoarder.utils, "eod", lambda: None)

    pornhoarder.List("test", page=1)

    # Should have no videos
    assert len(downloads) == 0
