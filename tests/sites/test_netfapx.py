from pathlib import Path

from resources.lib.sites import netfapx


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "netfapx"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_cards_and_pagination(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(netfapx.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(netfapx.utils, "eod", lambda: None)
    monkeypatch.setattr(netfapx.site, "add_download_link",
                        lambda name, url, mode, iconimage, desc='', duration='', **kwargs: downloads.append(
                            {"name": name, "url": url, "mode": mode, "icon": iconimage, "duration": duration}
                        ))
    monkeypatch.setattr(netfapx.site, "add_dir",
                        lambda name, url, mode, iconimage=None, contextm=None, **kwargs: dirs.append(
                            {"name": name, "url": url, "mode": mode, "contextm": contextm}
                        ))

    netfapx.List("https://netfapx.com/?orderby=newest")

    assert len(downloads) == 3
    assert downloads[0]["name"] == "Video One"
    assert downloads[0]["url"] == "https://netfapx.com/video-one"
    assert downloads[0]["duration"] == "10:01"
    assert downloads[1]["url"] == "https://netfapx.com/video-two"
    assert downloads[2]["icon"].endswith("3.jpg")

    next_entries = [d for d in dirs if d["mode"] == "netfapx.List"]
    assert len(next_entries) == 1
    assert next_entries[0]["url"] == "/page/2/"
    assert next_entries[0]["contextm"] is not None
    assert "(2/5)" in next_entries[0]["name"]


def test_categories_and_tags(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(netfapx.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(netfapx.utils, "eod", lambda: None)
    monkeypatch.setattr(netfapx.site, "add_dir",
                        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
                            {"name": name, "url": url, "mode": mode, "icon": iconimage}
                        ))

    netfapx.Categories("https://netfapx.com/categories")

    cats = [d for d in dirs if not d["name"].startswith("[tag]")]
    tags = [d for d in dirs if d["name"].startswith("[tag]")]

    assert len(cats) == 2
    assert cats[0]["name"] == "anal"
    assert cats[0]["url"] == "https://netfapx.com/category/anal"
    assert tags[0]["name"] == "[tag] Big Tits"
    assert tags[1]["url"] == "/tag/blonde"


def test_pornstars(monkeypatch):
    html = load_fixture("pornstars.html")
    dirs = []

    monkeypatch.setattr(netfapx.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(netfapx.utils, "eod", lambda: None)
    monkeypatch.setattr(netfapx.site, "add_dir",
                        lambda name, url, mode, iconimage=None, contextm=None, **kwargs: dirs.append(
                            {"name": name, "url": url, "mode": mode, "icon": iconimage, "contextm": contextm}
                        ))

    netfapx.Pornstars("https://netfapx.com/pornstar/?orderby=popular")

    assert len(dirs) == 3
    first = dirs[0]
    assert "Jane Doe" in first["name"]
    assert "(12 videos)" in first["name"]
    assert first["url"] == "https://netfapx.com/videos/jane-doe/"
    assert dirs[-1]["mode"] == "netfapx.Pornstars"
    assert dirs[-1]["contextm"] is not None
