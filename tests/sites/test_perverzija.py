"""Tests for perverzija BeautifulSoup migration."""
from pathlib import Path

from resources.lib.sites import perverzija


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "perverzija"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(perverzija.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, contextm=None, duration="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "contextm": contextm,
                "duration": duration,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(perverzija.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(perverzija.site, "add_dir", fake_add_dir)

    perverzija.List("https://tube.perverzija.com/page/1/")

    assert len(downloads) == 2

    first = downloads[0]
    assert first["name"] == "First Video"
    assert first["url"] == "https://tube.perverzija.com/videos/first-video"
    assert first["icon"] == "https://tube.perverzija.com/thumbs/first.jpg"
    assert first["duration"] == "10:21"
    assert first["contextm"][0][0].startswith("[COLOR deeppink]Lookup info")

    second = downloads[1]
    assert second["name"] == "Second Video"
    assert second["url"] == "https://tube.perverzija.com/videos/second-video"
    assert second["contextm"] is not None

    assert any(d["mode"] == "List" for d in dirs)


def test_list_pagination(monkeypatch):
    html = load_fixture("list.html")
    dirs = []

    monkeypatch.setattr(perverzija.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)
    monkeypatch.setattr(perverzija.site, "add_download_link", lambda *a, **k: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(perverzija.site, "add_dir", fake_add_dir)

    perverzija.List("https://tube.perverzija.com/page/1/")

    assert dirs[0]["name"] == "Next Page... (Currently in Page 1 of 3)"
    assert dirs[0]["url"] == "https://tube.perverzija.com/page/2/"


def test_tag_parsing(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(perverzija.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(perverzija.site, "add_dir", fake_add_dir)

    perverzija.Tag("https://tube.perverzija.com/tags/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Bondage (12)"
    assert dirs[0]["url"] == "https://tube.perverzija.com/tag/bondage/"


def test_studios_parsing(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(perverzija.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(perverzija.site, "add_dir", fake_add_dir)

    perverzija.Studios("https://tube.perverzija.com/studios/")

    assert len(dirs) == 2
    assert dirs[1]["name"] == "Studio Two (9)"
    assert dirs[1]["url"] == "https://tube.perverzija.com/studio/studio-two/"


def test_stars_parsing(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(perverzija.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(perverzija.site, "add_dir", fake_add_dir)

    perverzija.Stars("https://tube.perverzija.com/stars/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Star One (3)"
    assert dirs[0]["url"] == "https://tube.perverzija.com/stars/star-one/"
