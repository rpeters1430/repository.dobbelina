"""Tests for whereismyporn BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import whereismyporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "whereismyporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(whereismyporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(whereismyporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        whereismyporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(
        whereismyporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    whereismyporn.List("https://whereismyporn.com/page/1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Post"
    assert downloads[1]["url"].endswith("/second")
    assert any("Next Page" in d["name"] for d in dirs)
