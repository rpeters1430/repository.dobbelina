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

    def fake_post_html(url, *args, **kwargs):
        return html

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

    # Should have 1 video
    assert len(downloads) == 1

    # Should have pagination
    assert len(dirs) == 1

    assert "Next Page" in dirs[0]["name"]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses category links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, *args, **kwargs):
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

    pornhoarder.Categories("https://pornhoarder.io/categories/")

    # Should have categories
    assert len(dirs) > 0


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(pornhoarder.site, "search_dir", fake_search_dir)

    pornhoarder.Search("https://pornhoarder.io/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(search="", page=1, **kwargs):
        list_calls.append((search, page))

    monkeypatch.setattr(pornhoarder, "List", fake_list)

    pornhoarder.Search("https://pornhoarder.io/", keyword="test query")

    assert len(list_calls) == 1
    assert list_calls[0][0] == "test query"
    assert list_calls[0][1] == 1
