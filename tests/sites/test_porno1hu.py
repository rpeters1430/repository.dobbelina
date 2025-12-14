"""Tests for Porno1.hu BeautifulSoup migration."""
from pathlib import Path

from resources.lib.sites import porno1hu


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "porno1hu"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items_and_next(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(porno1hu.utils, "getHtml", lambda url, ref='': html)

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"name": name, "url": url, "img": iconimage, "duration": kwargs.get("duration")})

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(porno1hu.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(porno1hu.site, "add_dir", fake_add_dir)

    porno1hu.List("https://porno1.hu/friss-porno/", 1)

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Video A"
    assert downloads[1]["duration"] == "06:00"
    assert any(d["mode"] == "List" for d in dirs)


def test_categories_parse_and_format(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(porno1hu.utils, "getHtml", lambda url, ref='': html)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(porno1hu.site, "add_dir", fake_add_dir)

    porno1hu.Categories("https://porno1.hu/kategoriak/")

    assert len(dirs) == 2
    assert "(12)" in dirs[0]["name"]
    assert "mode=async" in dirs[0]["url"]


def test_playvid_decodes_kvs(monkeypatch):
    video_page = load_fixture("video_page.html")
    embed_page = load_fixture("embed_page.html")
    player_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.name = name
            self.download = download
            self.progress = type("p", (), {"update": lambda *args, **kwargs: None, "close": lambda *args, **kwargs: None})()

        def play_from_direct_link(self, url):
            player_calls.append(url)

    def fake_get_html(url, ref=None, hdr=None):
        if "embed" in url:
            return embed_page
        return video_page

    monkeypatch.setattr(porno1hu.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(porno1hu.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(porno1hu, "kvs_decode", lambda video_url, license_code: "https://cdn.example.com/decoded.mp4")

    porno1hu.Playvid("https://porno1.hu/video/test", "Test Video")

    assert player_calls
    assert player_calls[0].startswith("https://cdn.example.com/decoded.mp4")
    assert "referer=" in player_calls[0]
