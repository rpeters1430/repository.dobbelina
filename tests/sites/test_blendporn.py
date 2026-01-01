"""Tests for blendporn BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import blendporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "blendporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(blendporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(blendporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        blendporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "quality": kwargs.get("quality")}
        ),
    )
    monkeypatch.setattr(
        blendporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    blendporn.List("https://blendporn.com/most-recent/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Blend"
    assert downloads[0]["quality"] == "HD"
    assert downloads[1]["url"].endswith("/video/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_categories_parses_items(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(blendporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(blendporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        blendporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    blendporn.Categories("https://blendporn.com/channels/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Alpha"
