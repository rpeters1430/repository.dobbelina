"""Tests for Noodlemagazine BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import noodlemagazine


FIXTURE_DIR = (
    Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "noodlemagazine"
)


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(noodlemagazine.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, ""))
    monkeypatch.setattr(noodlemagazine.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(
        noodlemagazine.site, "add_download_link", fake_add_download_link
    )
    monkeypatch.setattr(noodlemagazine.site, "add_dir", fake_add_dir)

    noodlemagazine.List("https://noodlemagazine.com/video/?sort=0&hd=0&len=any&p=1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Noodle"
    assert downloads[0]["url"] == "https://noodlemagazine.com/video/first-video/"


def test_playvid_passes_page_url_to_html_fallback(monkeypatch):
    html = "<html><div>No explicit sources yet</div></html>"
    captured = {}

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type(
                "p",
                (),
                {
                    "update": lambda *args, **kwargs: None,
                    "close": lambda *args, **kwargs: None,
                },
            )()

        def play_from_html(self, page_html, page_url=None):
            captured["html"] = page_html
            captured["url"] = page_url
            
        def play_from_link_to_resolve(self, url):
            captured["resolve"] = url

    monkeypatch.setattr(noodlemagazine.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(noodlemagazine.utils, "VideoPlayer", FakeVideoPlayer)

    noodlemagazine.Playvid(
        "https://noodlemagazine.com/video/fallback-test/", "Fallback Test"
    )

    assert captured.get("html") == html or captured.get("resolve")
