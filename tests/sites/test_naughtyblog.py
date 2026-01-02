"""Tests for naughtyblog BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import naughtyblog


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "naughtyblog"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(naughtyblog.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(naughtyblog.utils, "eod", lambda: None)
    monkeypatch.setattr(
        naughtyblog.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(
        naughtyblog.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    naughtyblog.List("https://naughtyblog.org/category/clips/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Naughty"
    assert downloads[1]["url"].endswith("/post/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_categories_parses_items(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(naughtyblog.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(naughtyblog.utils, "eod", lambda: None)
    monkeypatch.setattr(
        naughtyblog.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    naughtyblog.Categories("https://naughtyblog.org/categories/")

    assert len(dirs) == 2
    assert dirs[0]["name"].startswith("Alpha")
