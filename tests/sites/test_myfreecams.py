"""Tests for myfreecams BeautifulSoup migration."""

from pathlib import Path

import pytest

pytest.importorskip("websocket")

from resources.lib.sites import myfreecams


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "myfreecams"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []

    monkeypatch.setattr(myfreecams.utils, "_getHtml", lambda *a, **k: html)
    monkeypatch.setattr(myfreecams.utils, "eod", lambda: None)
    monkeypatch.setattr(
        myfreecams.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(myfreecams.site, "add_dir", lambda *a, **k: None)

    myfreecams.List("https://www.myfreecams.com/php/model_explorer.php?get_contents=1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Model One"


def test_tags_parses_items(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(myfreecams.utils, "_getHtml", lambda *a, **k: html)
    monkeypatch.setattr(myfreecams.utils, "eod", lambda: None)
    monkeypatch.setattr(
        myfreecams.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, page=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    myfreecams.Tags("https://www.myfreecams.com/php/model_tags.php")

    assert len(dirs) == 2
    assert "tag-one" in dirs[0]["name"]


def test_tags_list_parses_items(monkeypatch):
    html = load_fixture("tags_list.html")
    downloads = []

    monkeypatch.setattr(myfreecams.utils, "_getHtml", lambda *a, **k: html)
    monkeypatch.setattr(myfreecams.utils, "eod", lambda: None)
    monkeypatch.setattr(
        myfreecams.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )

    myfreecams.TagsList("https://www.myfreecams.com/php/model_tags.php?get_users=1")

    assert len(downloads) == 2
    assert downloads[1]["name"] == "Model Four"
