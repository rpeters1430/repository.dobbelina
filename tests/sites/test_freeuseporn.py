"""Tests for freeuseporn BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import freeuseporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "freeuseporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(freeuseporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(freeuseporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        freeuseporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(
        freeuseporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    freeuseporn.List("https://www.freeuseporn.com/videos?o=mr&page=1")

    # Real 2026 listing: video cards are a.thumb-wrap-link -> /video/<id>/<slug>;
    # /videos/<name> links are categories and must not be listed as videos.
    assert len(downloads) == 20
    assert downloads[0]["name"] == "magic manipulation lexia"
    assert downloads[0]["url"] == "https://www.freeuseporn.com/video/10629/magic-manipulation-lexia"
    assert all("/video/" in d["url"] for d in downloads)
    assert dirs == [{"name": "Next Page (2)", "url": "https://www.freeuseporn.com/videos?o=mr&page=2"}]


def test_tags_parses_items(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(freeuseporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(freeuseporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        freeuseporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "keyword": kwargs.get("keyword")}
        ),
    )

    freeuseporn.Tags("https://www.freeuseporn.com/tags/")

    assert len(dirs) == 2
    assert dirs[0]["keyword"] == "tag-one"
