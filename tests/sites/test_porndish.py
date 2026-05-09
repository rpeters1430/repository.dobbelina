"""Comprehensive tests for porndish site implementation."""

from pathlib import Path

from resources.lib.sites import porndish


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "porndish"


def load_fixture(name):
    """Load a fixture file from the porndish fixtures directory."""
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

    monkeypatch.setattr(porndish.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(porndish.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(porndish.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(porndish.utils, "eod", lambda: None)

    porndish.List("https://www.porndish.com/page/1/")

    # Should have 2 videos
    assert len(downloads) == 2


def test_playvid_implementation(monkeypatch):
    """Test that Playvid handles Cloudflare retry."""
    html = '<html><iframe src="https://player.com/e/123"></iframe></html>'
    
    played = {}
    
    class MockPlayer:
        def __init__(self, *a, **k):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()
        def play_from_site_link(self, url, ref):
            played["page_url"] = url
            
    monkeypatch.setattr(porndish.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, ""))
    monkeypatch.setattr(porndish.utils, "VideoPlayer", MockPlayer)
    
    porndish.Playvid("https://www.porndish.com/video-one/", "Test")
    
    assert played["page_url"] == "https://www.porndish.com/video-one/"
