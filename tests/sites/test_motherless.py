"""Comprehensive tests for motherless site implementation."""

from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import motherless


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "motherless"


def load_fixture(name):
    """Load a fixture file from the motherless fixtures directory."""
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
            }
        )

    def fake_add_dir(name, url, mode, *args, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(motherless.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(motherless.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(motherless.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(motherless.utils, "eod", lambda: None)

    motherless.List("https://motherless.xxx/videos/recent")

    # Should have videos from the fixture
    assert len(downloads) > 0


def test_cat_parses_categories(monkeypatch):
    """Test that Categories correctly parses category items."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    def fake_add_dir(name, url, mode, *args, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(motherless.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(motherless.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(motherless.utils, "eod", lambda: None)

    motherless.Categories("https://motherless.xxx/categories")

    # Should have categories
    assert len(dirs) > 0


def test_playvid_implementation(monkeypatch):
    """Test that Playvid handles source extraction."""
    html = '<html><video><source src="https://cdn.com/video.mp4"></video></html>'
    
    played = {}
    
    class MockPlayer:
        def __init__(self, *a, **k):
            self.progress = MagicMock()
        def play_from_direct_link(self, url):
            played["url"] = url
            
    monkeypatch.setattr(motherless.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, ""))
    monkeypatch.setattr(motherless.utils, "VideoPlayer", MockPlayer)
    
    motherless.Playvid("https://motherless.xxx/v1", "Test")
    
    assert played.get("url") or played.get("resolve")
