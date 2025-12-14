"""Tests for Porno365 BeautifulSoup migration."""
from pathlib import Path

from resources.lib.sites import porno365


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "porno365"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_next(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(porno365.utils, "getHtml", lambda url, ref=None, headers=None: html)

    monkeypatch.setattr(porno365.site, "add_download_link", lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append({"name": name, "url": url, "duration": kwargs.get("duration")}))
    monkeypatch.setattr(porno365.site, "add_dir", lambda name, url, mode, iconimage=None, **kwargs: dirs.append({"name": name, "url": url, "mode": mode}))

    porno365.List("http://m.porno365.pics/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Video One"
    assert downloads[1]["duration"] == "06:00"
    assert any(d["mode"] == "List" for d in dirs)


def test_categories_parse(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []
    monkeypatch.setattr(porno365.utils, "getHtml", lambda url, headers=None: html)
    monkeypatch.setattr(porno365.site, "add_dir", lambda name, url, mode, iconimage=None, **kwargs: dirs.append({"name": name, "url": url}))

    porno365.Categories("http://m.porno365.pics/categories")

    assert len(dirs) == 2
    assert "(10 videos)" in dirs[0]["name"]
    assert dirs[0]["url"].startswith("http://m.porno365.pics/")


def test_models_parse_next(monkeypatch):
    html = load_fixture("models.html")
    dirs = []
    monkeypatch.setattr(porno365.utils, "getHtml", lambda url, headers=None: html)
    monkeypatch.setattr(porno365.site, "add_dir", lambda name, url, mode, iconimage=None, **kwargs: dirs.append({"name": name, "url": url, "mode": mode}))

    porno365.Models("http://m.porno365.pics/models")

    assert len(dirs) == 3
    assert any("Next Page" in d["name"] for d in dirs)


def test_playvid_uses_videoplayer(monkeypatch):
    html = load_fixture("video.html")
    calls = []

    class FakeVP:
        def __init__(self, name, download=None, direct_regex=None):
            self.progress = type("p", (), {"update": lambda *args, **kwargs: None})()
            calls.append(("init", name, direct_regex))

        def play_from_html(self, page_html):
            calls.append(("play_html", page_html))

    monkeypatch.setattr(porno365.utils, "getHtml", lambda url, ref=None, headers=None: html)
    monkeypatch.setattr(porno365.utils, "VideoPlayer", FakeVP)

    porno365.Playvid("http://m.porno365.pics/video", "Test Video")

    assert calls[0][0] == "init"
    assert calls[0][2]
    assert calls[1][0] == "play_html"
