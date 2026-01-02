"""Tests for premiumporn BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import premiumporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "premiumporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(premiumporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(premiumporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        premiumporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(
        premiumporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    premiumporn.List("https://premiumporn.org/page/1?filter=latest")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Premium"
    assert downloads[1]["url"].endswith("/video/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_categories_parses_items(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(premiumporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(premiumporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        premiumporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    premiumporn.Categories("https://premiumporn.org/actors/")

    cat_dirs = [d for d in dirs if "Alpha" in d["name"]]
    assert len(cat_dirs) == 1
