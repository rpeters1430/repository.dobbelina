"""Tests for seaporn BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import seaporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "seaporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(seaporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(seaporn.utils.progress, "create", lambda *a, **k: None)
    monkeypatch.setattr(seaporn.utils.progress, "update", lambda *a, **k: None)
    monkeypatch.setattr(seaporn.utils.progress, "close", lambda *a, **k: None)
    monkeypatch.setattr(
        seaporn.utils.progress, "iscanceled", lambda: False, raising=False
    )
    monkeypatch.setattr(seaporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        seaporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(
        seaporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    seaporn.List("https://seaporn.org/")

    assert len(downloads) == 2
    assert downloads[0]["name"].startswith("First Sea")
    assert any("Next Page" in d["name"] for d in dirs)
