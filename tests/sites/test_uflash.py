"""Tests for uflash BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import uflash


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "uflash"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []

    monkeypatch.setattr(uflash.utils, "_getHtml", lambda *a, **k: html)
    monkeypatch.setattr(uflash.utils, "eod", lambda: None)
    monkeypatch.setattr(
        uflash.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(uflash.site, "add_dir", lambda *a, **k: None)

    uflash.List("https://www.uflash.tv/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Uflash"
    assert downloads[0]["url"].endswith("/video/first")
    assert downloads[1]["duration"] == "09:00"
