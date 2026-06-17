"""Tests for cumlouder BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import cumlouder


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "cumlouder"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(cumlouder.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(cumlouder.utils, "eod", lambda: None)
    monkeypatch.setattr(
        cumlouder.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "quality": kwargs.get("quality")}
        ),
    )
    monkeypatch.setattr(
        cumlouder.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    cumlouder.List("https://www.cumlouder.com/porn/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Scene"
    assert downloads[0]["quality"] == "HD"
    assert downloads[1]["url"].endswith("/porn/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_list_uses_porn_index_for_site_root(monkeypatch):
    html = load_fixture("listing.html")
    requested_urls = []

    def fake_get_html(url, *args, **kwargs):
        requested_urls.append(url)
        return html

    monkeypatch.setattr(cumlouder.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cumlouder.utils, "eod", lambda: None)
    monkeypatch.setattr(cumlouder.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(cumlouder.site, "add_dir", lambda *a, **k: None)

    cumlouder.List("https://www.cumlouder.com/")

    assert requested_urls == ["https://www.cumlouder.com/porn/"]
