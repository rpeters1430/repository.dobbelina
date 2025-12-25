"""Tests for Tube8 site implementation."""

from pathlib import Path

from resources.lib.sites import tube8

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "tube8"


def load_fixture(name):
    """Load a fixture file from the tube8 fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html_data = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html_data

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

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(tube8.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(tube8.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(tube8.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(tube8.utils, "eod", lambda: None)

    tube8.List("https://www.tube8.com/")

    # Check that we parsed videos
    assert len(downloads) > 0, "Should parse at least one video"

    # Check first video has required fields
    assert downloads[0]["name"], "Video should have a title"
    assert downloads[0]["url"].startswith("https://www.tube8.com/"), (
        "Video URL should be absolute"
    )
    assert downloads[0]["icon"], "Video should have a thumbnail"


def test_list_handles_pagination(monkeypatch):
    """Test that List adds Next Page when pagination is present."""
    html_data = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html_data

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(tube8.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(tube8.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(tube8.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(tube8.utils, "eod", lambda: None)

    tube8.List("https://www.tube8.com/")

    # Should have Next Page if pagination exists
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    if next_pages:
        assert "page" in next_pages[0]["url"].lower(), (
            "Next page URL should contain 'page'"
        )


def test_categories_parses_and_sorts(monkeypatch):
    """Test that Categories correctly parses categories."""
    html_data = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html_data

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(tube8.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(tube8.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(tube8.utils, "eod", lambda: None)

    tube8.Categories("https://www.tube8.com/categories.html")

    # Should parse categories
    assert len(dirs) > 0, "Should parse at least one category"

    # Check categories have required fields
    for cat in dirs:
        assert cat["name"], "Category should have a name"
        assert cat["url"].startswith("https://www.tube8.com/"), (
            "Category URL should be absolute"
        )

    # Check that categories are sorted alphabetically (first should come before last)
    if len(dirs) >= 2:
        assert dirs[0]["name"].lower() <= dirs[-1]["name"].lower(), (
            "Categories should be sorted alphabetically"
        )


def test_search_builds_correct_url(monkeypatch):
    """Test that Search builds the correct URL with search parameter."""
    called_urls = []

    def fake_list(url):
        called_urls.append(url)

    monkeypatch.setattr(tube8, "List", fake_list)

    tube8.Search("https://www.tube8.com/search/", keyword="test search")

    assert len(called_urls) == 1
    assert "test+search" in called_urls[0]
    assert called_urls[0].endswith("/")
