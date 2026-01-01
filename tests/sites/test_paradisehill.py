"""Tests for paradisehill BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import paradisehill


FIXTURE_DIR = (
    Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "paradisehill"
)


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(paradisehill.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(paradisehill.utils, "eod", lambda: None)
    monkeypatch.setattr(
        paradisehill.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(
        paradisehill.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    paradisehill.List("https://en.paradisehill.cc/all/?sort=created_at")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Hill"
    assert downloads[1]["url"].endswith("/video/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_cat_parses_items(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(paradisehill.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(paradisehill.utils, "eod", lambda: None)
    monkeypatch.setattr(
        paradisehill.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    paradisehill.Cat("https://en.paradisehill.cc/categories/")

    cat_dirs = [d for d in dirs if d["name"] == "Alpha"]
    assert len(cat_dirs) == 1
