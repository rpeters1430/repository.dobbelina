"""Tests for 6xtube BeautifulSoup migration."""

from pathlib import Path
import importlib

six_tube = importlib.import_module("resources.lib.sites.6xtube")


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "6xtube"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_pagination(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(six_tube.utils, "getHtml", lambda url, ref="": html)
    monkeypatch.setattr(
        six_tube.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {
                "name": name,
                "url": url,
                "img": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        ),
    )
    monkeypatch.setattr(
        six_tube.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(six_tube.utils, "eod", lambda: None)

    six_tube.List("http://www.6xtube.com/most-recent/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Alpha Video"
    assert downloads[0]["duration"] == "12:34"
    assert downloads[0]["quality"] == "HD"
    assert downloads[1]["url"] == "http://www.6xtube.com/video/456"
    assert any("Next Page (2/5)" == d["name"] for d in dirs)


def test_categories_parses_entries(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(six_tube.utils, "getHtml", lambda url, ref="": html)
    monkeypatch.setattr(
        six_tube.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "img": iconimage}
        ),
    )
    monkeypatch.setattr(six_tube.utils, "eod", lambda: None)

    six_tube.Categories("http://www.6xtube.com/channels/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Category One"
    assert dirs[0]["url"] == "http://www.6xtube.com/channels/cat1"
    assert dirs[1]["img"] == "http://www.6xtube.com/cat2.jpg"
