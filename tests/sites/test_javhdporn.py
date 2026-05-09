"""Tests for javhdporn site implementation."""

from pathlib import Path

from resources.lib.sites import javhdporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "javhdporn"


def load_fixture(name):
    """Load a fixture file from the javhdporn fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
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

    monkeypatch.setattr(javhdporn.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(javhdporn.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(javhdporn.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javhdporn.utils, "eod", lambda: None)

    javhdporn.List("https://www4.javhdporn.net/")

    # Should have 3 videos
    assert len(downloads) == 3


def test_list_pagination(monkeypatch):
    """Test that List correctly adds pagination."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(javhdporn.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(javhdporn.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(javhdporn.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javhdporn.utils, "eod", lambda: None)

    javhdporn.List("https://www4.javhdporn.net/")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
