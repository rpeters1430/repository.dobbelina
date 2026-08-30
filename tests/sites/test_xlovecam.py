"""Tests for xlovecam.com site implementation."""

from resources.lib.sites import xlovecam


def _sample_list_response(next_query=None, more=True):
    return {
        "content": {
            "performerList": [
                {
                    "nickname": "IrisBlair",
                    "showType": 1,
                    "hlsPlaylist": "https://spg1-eu-nl.wlresources.com/live/playlist.m3u8",
                    "profileImg": "//img-us-ny.xlovecam.com/thumb/iris.jpg",
                    "rating": 4.32,
                    "love": 6,
                },
                {
                    "nickname": "OfflineModel",
                    "showType": 0,
                    "hlsPlaylist": None,
                    "profileImg": "//img-us-ny.xlovecam.com/thumb/offline.jpg",
                },
            ],
            "nextQuery": next_query or {"from": 35, "time": 1788117136, "off": None},
            "moreItemAvailable": more,
        }
    }


def test_csrf_regex_matches_both_markup_shapes():
    # Legacy `var csrfProtectionToken = "..."` form.
    assert xlovecam.CSRF_RE.search('var csrfProtectionToken = "abc123"').group(1) == "abc123"
    # Current JSON-embedded form (no `=`, quoted key) -- upstream's original
    # regex only matched the legacy `=` form and stopped finding a token at
    # all once the site switched to this shape.
    assert xlovecam.CSRF_RE.search('"csrfProtectionToken":"xyz789"').group(1) == "xyz789"


def test_list_skips_offline_models_and_adds_pagination(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(xlovecam, "_online_list", lambda next_query=None, nickname="": _sample_list_response())
    monkeypatch.setattr(
        xlovecam.site,
        "add_download_link",
        lambda name, url, mode, icon, desc="", **k: downloads.append(
            {"name": name, "url": url, "mode": mode, "icon": icon}
        ),
    )
    monkeypatch.setattr(
        xlovecam.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url}),
    )
    monkeypatch.setattr(xlovecam.utils, "eod", lambda: None)
    monkeypatch.setattr(xlovecam.utils, "notify", lambda *a, **k: None)

    xlovecam.List(xlovecam.site.url)

    assert len(downloads) == 1
    assert downloads[0]["name"] == "IrisBlair"
    assert downloads[0]["url"] == "https://spg1-eu-nl.wlresources.com/live/playlist.m3u8"
    assert downloads[0]["icon"] == "https://img-us-ny.xlovecam.com/thumb/iris.jpg"

    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]


def test_list_omits_pagination_when_no_more_items(monkeypatch):
    dirs = []
    monkeypatch.setattr(
        xlovecam, "_online_list", lambda next_query=None, nickname="": _sample_list_response(more=False)
    )
    monkeypatch.setattr(xlovecam.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(
        xlovecam.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append(name),
    )
    monkeypatch.setattr(xlovecam.utils, "eod", lambda: None)
    monkeypatch.setattr(xlovecam.utils, "notify", lambda *a, **k: None)

    xlovecam.List(xlovecam.site.url)

    assert dirs == []


def test_list_decodes_next_query_cursor(monkeypatch):
    captured_next_query = {}

    def fake_online_list(next_query=None, nickname=""):
        captured_next_query["value"] = next_query
        return _sample_list_response()

    monkeypatch.setattr(xlovecam, "_online_list", fake_online_list)
    monkeypatch.setattr(xlovecam.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(xlovecam.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(xlovecam.utils, "eod", lambda: None)
    monkeypatch.setattr(xlovecam.utils, "notify", lambda *a, **k: None)

    xlovecam.List("%7B%22from%22%3A%2035%2C%20%22time%22%3A%201788117136%2C%20%22off%22%3A%20null%7D")

    assert captured_next_query["value"] == {"from": 35, "time": 1788117136, "off": None}


def test_search_without_keyword_shows_dialog(monkeypatch):
    search_called = []
    monkeypatch.setattr(
        xlovecam.site, "search_dir", lambda url, mode: search_called.append((url, mode))
    )

    xlovecam.Search(xlovecam.site.url)

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_filters_online_models_by_nickname(monkeypatch):
    captured_nickname = {}
    downloads = []

    def fake_online_list(next_query=None, nickname=""):
        captured_nickname["value"] = nickname
        return _sample_list_response()

    monkeypatch.setattr(xlovecam, "_online_list", fake_online_list)
    monkeypatch.setattr(
        xlovecam.site,
        "add_download_link",
        lambda name, url, mode, icon, desc="", **k: downloads.append(name),
    )
    monkeypatch.setattr(xlovecam.utils, "eod", lambda: None)
    monkeypatch.setattr(xlovecam.utils, "notify", lambda *a, **k: None)

    xlovecam.Search(xlovecam.site.url, keyword="Iris Blair")

    assert captured_nickname["value"] == "Iris Blair"
    assert downloads == ["IrisBlair"]


def test_playvid_pipes_headers_to_direct_link(monkeypatch):
    captured = {}

    class _DummyVP:
        def __init__(self, name, IA_check=None, **kwargs):
            pass

        def play_from_direct_link(self, url):
            captured["url"] = url

    monkeypatch.setattr(xlovecam.utils, "VideoPlayer", _DummyVP)

    xlovecam.Playvid("https://spg1-eu-nl.wlresources.com/live/playlist.m3u8", "IrisBlair")

    assert captured["url"].startswith("https://spg1-eu-nl.wlresources.com/live/playlist.m3u8|")
    assert "User-Agent=" in captured["url"]
    assert "Referer=" in captured["url"]
