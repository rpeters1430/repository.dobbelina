"""Tests for asianviralhub.com site implementation."""

from pathlib import Path

from resources.lib.sites import asianviralhub


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "asianviralhub"


def load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(asianviralhub.utils, "getHtml", lambda url, referer=None: html)
    monkeypatch.setattr(
        asianviralhub.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(
        asianviralhub.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(asianviralhub.utils, "eod", lambda: None)

    asianviralhub.List("https://asianviralhub.com/latest-updates/")

    assert len(downloads) == 3
    assert downloads[0]["name"] == "Rocketreyna Enjoys A Couch Orgasm Onlyfans"
    assert downloads[0]["url"] == "https://asianviralhub.com/video/54689/rocketreyna-enjoys-a-couch-orgasm-onlyfans/"
    assert downloads[0]["icon"] == "https://asianviralhub.com/contents/videos_screenshots/54000/54689/320x180/1.jpg"
    assert downloads[0]["mode"] == "Playvid"

    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://asianviralhub.com/latest-updates/2/"


def test_search_without_keyword(monkeypatch):
    search_called = []
    monkeypatch.setattr(
        asianviralhub.site,
        "search_dir",
        lambda url, mode: search_called.append((url, mode)),
    )

    asianviralhub.Search("https://asianviralhub.com/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    list_calls = []
    monkeypatch.setattr(asianviralhub, "List", lambda url: list_calls.append(url))

    asianviralhub.Search("https://asianviralhub.com/search/", keyword="asian teen")

    assert list_calls == ["https://asianviralhub.com/search/asian-teen/"]


def test_playvid_uses_kt_player(monkeypatch):
    captured = {}

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            self.progress = type(
                "P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None}
            )()

        def play_from_kt_player(self, html, url=None):
            captured["html"] = html
            captured["url"] = url

    monkeypatch.setattr(asianviralhub.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(
        asianviralhub.utils,
        "getHtml",
        lambda url, referer=None: "<script>var player_obj = kt_player('kt_player', ...)</script>",
    )

    asianviralhub.Playvid("https://asianviralhub.com/video/54689/example/", "Example")

    assert captured["url"] == "https://asianviralhub.com/video/54689/example/"
