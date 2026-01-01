"""Tests for nonktube BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import nonktube


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "nonktube"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(nonktube.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(nonktube.utils, "eod", lambda: None)
    monkeypatch.setattr(
        nonktube.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(
        nonktube.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    nonktube.List("https://www.nonktube.com/?sorting=latest")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Nonk"
    assert downloads[1]["url"].endswith("/video/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_cat_parses_items(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(nonktube.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(nonktube.utils, "eod", lambda: None)
    monkeypatch.setattr(
        nonktube.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    nonktube.Cat("https://www.nonktube.com/categories/")

    assert len(dirs) == 1
    assert "Alpha" in dirs[0]["name"]
