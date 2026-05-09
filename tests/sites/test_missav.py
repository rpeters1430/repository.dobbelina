"""Comprehensive tests for missav site implementation."""

from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import missav


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "missav"


def load_fixture(name):
    """Load a fixture file from the missav fixtures directory."""
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

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(missav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(missav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(missav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(missav.utils, "eod", lambda: None)

    missav.List("https://missav.ws/en/new?page=1")

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

    monkeypatch.setattr(missav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(missav.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(missav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(missav.utils, "eod", lambda: None)

    missav.List("https://missav.ws/en/new?page=1")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1


def test_models_parses_items(monkeypatch):
    """Test that Models correctly parses model items."""
    html = load_fixture("models.html")

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

    monkeypatch.setattr(missav.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(missav.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(missav.utils, "eod", lambda: None)

    missav.Models("https://missav.ws/en/actresses")

    # Should have models from the fixture
    assert len(dirs) > 0


def test_playvid_implementation(monkeypatch):
    """Test that Playvid handles packed JS extraction."""
    html = '<script>eval(function(p,a,c,k,e,d){}(...))</script>'
    
    played = {}
    
    class MockPlayer:
        def __init__(self, *a, **k):
            self.progress = MagicMock()
        def play_from_direct_link(self, url):
            played["url"] = url
            
    monkeypatch.setattr(missav.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, ""))
    monkeypatch.setattr(missav, "jsunpack", type("obj", (object,), {"unpack": lambda x: "var source='https://cdn.com/video.m3u8';"}))
    monkeypatch.setattr(missav.utils, "VideoPlayer", MockPlayer)
    
    missav.Playvid("https://missav.ws/v1", "Test")
    
    assert played["url"] == "https://cdn.com/video.m3u8|Referer=https://missav.ws/"
