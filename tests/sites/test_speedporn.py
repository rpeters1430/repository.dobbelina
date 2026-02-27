"""Tests for speedporn BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import speedporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "speedporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(speedporn.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, False))
    monkeypatch.setattr(speedporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        speedporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(
        speedporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    speedporn.List("https://speedporn.net/?filter=latest")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Speed"
    assert downloads[0]["duration"] == "10m"
    assert downloads[1]["url"].endswith("/video/second")
    assert any("Next Page" in d["name"] for d in dirs)
