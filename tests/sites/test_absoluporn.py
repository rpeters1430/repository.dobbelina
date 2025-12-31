"""Tests for AbsoluPorn BeautifulSoup migration."""

from pathlib import Path
import importlib

absoluporn = importlib.import_module("resources.lib.sites.absoluporn")


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "absoluporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_next_page(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(absoluporn.utils, "getHtml", lambda url, ref="": html)
    monkeypatch.setattr(
        absoluporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {
                "name": name,
                "url": url,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        ),
    )
    monkeypatch.setattr(
        absoluporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(absoluporn.utils, "eod", lambda: None)

    absoluporn.List("http://www.absoluporn.com/en/wall-date-1.html")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Alpha Clip"
    assert downloads[0]["duration"] == "05:55"
    assert downloads[0]["quality"] == "FULLHD"
    assert downloads[1]["quality"] == "HD"
    assert any(d["name"] == "Next Page" for d in dirs)


def test_cat_parses_categories(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(absoluporn.utils, "getHtml", lambda url, ref="": html)
    monkeypatch.setattr(
        absoluporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(absoluporn.utils, "eod", lambda: None)

    absoluporn.Cat("http://www.absoluporn.com/en")

    assert len(dirs) == 2
    assert "Category One" in dirs[0]["name"]
    assert dirs[0]["url"].endswith("/cat-1.html")
