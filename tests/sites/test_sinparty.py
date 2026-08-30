"""Tests for sinparty.com site implementation."""

import json
from pathlib import Path

from resources.lib.sites import sinparty


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "sinparty"


def load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items_and_skips_missing_hash(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(sinparty.utils, "_getHtml", lambda url, **k: load_fixture("list.json"))
    monkeypatch.setattr(
        sinparty.site,
        "add_download_link",
        lambda name, url, mode, icon, desc="", **k: downloads.append(
            {"name": name, "url": url, "mode": mode, "desc": desc}
        ),
    )
    monkeypatch.setattr(
        sinparty.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(sinparty.utils, "eod", lambda: None)
    monkeypatch.setattr(sinparty.utils, "notify", lambda *a, **k: None)

    sinparty.List("https://api.sinparty.com/v2/web/live-cams/web-rtc/girls?per_page=5&page=1")

    # Third fixture item has no creator_user_hash and should be skipped.
    assert len(downloads) == 2
    assert downloads[0]["name"] == "Nyx_Savage"
    assert downloads[0]["url"] == "https://api.sinparty.com/v2/web/live-cams/web-rtc/user6a67a0ec132e2"
    assert "Age:" in downloads[0]["desc"]
    assert "PL" in downloads[0]["desc"]

    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "page=2" in dirs[0]["url"]


def test_list_notifies_and_stops_on_error(monkeypatch):
    notified = []

    def raise_error(url, **k):
        raise ValueError("boom")

    monkeypatch.setattr(sinparty.utils, "_getHtml", raise_error)
    monkeypatch.setattr(sinparty.utils, "notify", lambda *a, **k: notified.append(a))
    monkeypatch.setattr(sinparty.utils, "eod", lambda: None)
    monkeypatch.setattr(sinparty.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(sinparty.site, "add_dir", lambda *a, **k: None)

    sinparty.List(sinparty.API_URL.format("girls", "f"))

    assert notified


def test_playvid_plays_public_stream(monkeypatch):
    captured = {}

    class _DummyVP:
        def __init__(self, name, IA_check=None, **kwargs):
            self.progress = type(
                "P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None}
            )()

        def play_from_direct_link(self, url):
            captured["url"] = url

    monkeypatch.setattr(sinparty.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(
        sinparty.utils, "_getHtml", lambda url, **k: load_fixture("playback_public.json")
    )

    sinparty.Playvid(
        "https://api.sinparty.com/v2/web/live-cams/web-rtc/user6a67a0ec132e2", "Nyx_Savage"
    )

    assert captured["url"] == (
        "https://edge-cdn2.streamparty.online/LiveApp/streams/user6a67a0ec132e2/example_adaptive.m3u8"
    )


def test_playvid_blocks_offline_model(monkeypatch):
    captured = {}

    class _DummyVP:
        def __init__(self, name, IA_check=None, **kwargs):
            self.progress = type(
                "P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None}
            )()

        def play_from_direct_link(self, url):
            captured["url"] = url

    offline_payload = json.dumps({"data": {"isLive": False}})

    monkeypatch.setattr(sinparty.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(sinparty.utils, "_getHtml", lambda url, **k: offline_payload)
    notified = []
    monkeypatch.setattr(sinparty.utils, "notify", lambda *a, **k: notified.append(a))

    sinparty.Playvid("https://api.sinparty.com/v2/web/live-cams/web-rtc/user123", "Offline_Model")

    assert "url" not in captured
    assert notified


def test_search_without_keyword_shows_dialog(monkeypatch):
    search_called = []
    monkeypatch.setattr(
        sinparty.site, "search_dir", lambda url, mode: search_called.append((url, mode))
    )

    sinparty.Search(sinparty.site.url)

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"
