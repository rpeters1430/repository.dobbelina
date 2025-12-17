"""Tests for vaginanl site BeautifulSoup parsing."""
from pathlib import Path

from resources.lib.sites import vaginanl


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "vaginanl"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_cards(monkeypatch):
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(vaginanl.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(vaginanl.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, duration="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "duration": duration,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(vaginanl.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(vaginanl.site, "add_dir", fake_add_dir)

    vaginanl.List("https://vagina.nl/sexfilms/newest")

    assert len(downloads) == 2

    first = downloads[0]
    assert first["name"] == "First Video"
    assert first["url"] == "https://vagina.nl/sexfilms/first-video"
    assert first["mode"] == "Playvid"
    assert first["icon"].startswith("https://cdn.vagina.nl/thumbs/first.jpg")
    assert first["duration"] == "12:34"

    second = downloads[1]
    assert second["name"] == "Second Video"
    assert second["url"] == "https://vagina.nl/sexfilms/second-video"
    assert second["duration"] == "08:01"

    assert len([d for d in dirs if d["mode"] == "List"]) == 1


def test_list_adds_pagination(monkeypatch):
    html = load_fixture("list.html")
    dirs = []

    monkeypatch.setattr(vaginanl.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(vaginanl.utils, "eod", lambda: None)
    monkeypatch.setattr(vaginanl.site, "add_download_link", lambda *a, **k: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(vaginanl.site, "add_dir", fake_add_dir)

    vaginanl.List("https://vagina.nl/sexfilms/newest")

    assert dirs[0]["name"] == "Next Page (2/5)"
    assert dirs[0]["url"] == "https://vagina.nl/sexfilms/newest?page=2"
    assert dirs[0]["mode"] == "List"


def test_categories_parses_cards(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(vaginanl.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(vaginanl.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(vaginanl.site, "add_dir", fake_add_dir)

    vaginanl.Categories("https://vagina.nl/categories")

    assert len(dirs) == 2

    first = dirs[0]
    assert first["name"] == "Teen"
    assert first["url"] == "https://vagina.nl/categories/teen"
    assert first["icon"] == "https://cdn.vagina.nl/cat/teen.jpg"

    second = dirs[1]
    assert second["name"] == "Hardcore"
    assert second["url"] == "https://vagina.nl/categories/hardcore"
    assert second["icon"] == "https://cdn.vagina.nl/cat/hardcore.jpg"
