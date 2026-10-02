import json
from unittest.mock import MagicMock
from urllib.error import HTTPError

import pytest

from resources.lib.sites import stripchat


_real_probe_stream = stripchat._probe_stream


@pytest.fixture(autouse=True)
def _no_live_stream_probe(monkeypatch):
    """Playback tests must not hit the CDN; probe tests call _real_probe_stream."""
    monkeypatch.setattr(stripchat, "_probe_stream", lambda url: "")


class _Recorder:
    def __init__(self):
        self.play_calls = []
        self.notifications = []


def _model_payload(username, stream_url=None, is_live=True):
    model = {
        "username": username,
        "isLive": is_live,
    }
    if stream_url:
        model["hlsPlaylist"] = stream_url
    return json.dumps({"models": [model]})


def test_main_menu(monkeypatch):
    dirs = []

    def fake_add_dir(name, url, mode, iconimage="", Folder=True, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "folder": Folder})

    monkeypatch.setattr(stripchat.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)
    monkeypatch.setattr(
        stripchat.utils.addon,
        "getSetting",
        lambda key: {"chatfemale": "true", "chatmale": "true", "chatcouple": "true", "chattrans": "true"}.get(key, "false"),
    )

    stripchat.Main()

    modes = [d["mode"] for d in dirs]
    assert "clean_database" in modes
    assert "TopModels" in modes
    assert "Search" in modes
    assert "List" in modes
    # the dispatcher drops empty arguments, and Search requires a url
    assert all(d["url"] for d in dirs if d["mode"] in ("Search", "List"))


def test_format_direct_hls_url():
    raw_url = "https://edge-hls.doppiocdn.media/hls/12345/master/12345.m3u8?playlistType=lowLatency"
    formatted = stripchat._format_direct_hls_url(raw_url)

    assert "playlistType=lowLatency" not in formatted
    assert "/hls/12345/master/12345_auto.m3u8?" in formatted
    assert "pkey=B0p93vi8Uj6AYyZb" in formatted
    assert "User-Agent=" in formatted
    assert "Origin=https%3A%2F%2Fstripchat.com" in formatted
    assert "Referer=https%3A%2F%2Fstripchat.com%2F" in formatted
    assert "manifest_headers=1" in formatted


def test_playvid_plays_direct_hls_url(monkeypatch):
    recorder = _Recorder()

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None, *args, **kwargs):
            self.name = name
            self.IA_check = IA_check
            self.progress = type(
                "P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None}
            )()

        def play_from_direct_link(self, url):
            recorder.play_calls.append(url)

    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg="", *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    test_url = "https://edge-hls.doppiocdn.media/hls/999/master/999.m3u8?playlistType=lowLatency"
    stripchat.Playvid(test_url, "SomeModel")

    assert len(recorder.play_calls) == 1
    assert "pkey=B0p93vi8Uj6AYyZb" in recorder.play_calls[0]
    assert "playlistType=lowLatency" not in recorder.play_calls[0]
    assert "manifest_headers=1" in recorder.play_calls[0]
    assert recorder.notifications == []


def test_playvid_resolves_username_stream(monkeypatch):
    recorder = _Recorder()

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None, *args, **kwargs):
            self.name = name
            self.IA_check = IA_check
            self.progress = type(
                "P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None}
            )()

        def play_from_direct_link(self, url):
            recorder.play_calls.append(url)

    def fake_cloudflare_retry(url, *args, **kwargs):
        if "search/group/username?query=model1" in url:
            return (json.dumps({"models": [{"username": "model1", "id": 111, "isLive": True}]}), False)
        return ("", False)

    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(stripchat.utils, "get_html_with_cloudflare_retry", fake_cloudflare_retry)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg="", *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/model1", "model1")

    assert len(recorder.play_calls) == 1
    assert "hls/111/master/111_auto.m3u8" in recorder.play_calls[0]
    assert "pkey=B0p93vi8Uj6AYyZb" in recorder.play_calls[0]
    assert recorder.notifications == []


def test_playvid_notifies_when_model_is_offline(monkeypatch):
    recorder = _Recorder()

    def fake_cloudflare_retry(url, *args, **kwargs):
        return (json.dumps({"models": [{"username": "offline_girl", "isLive": False}]}), False)

    monkeypatch.setattr(stripchat.utils, "get_html_with_cloudflare_retry", fake_cloudflare_retry)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg="", *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/offline_girl", "offline_girl")

    assert recorder.play_calls == []
    assert len(recorder.notifications) == 1
    assert "offline" in recorder.notifications[0][1].lower() or "offline" in recorder.notifications[0][0].lower()


def test_playvid_blocks_offline_labeled_model(monkeypatch):
    recorder = _Recorder()
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg="", *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("", "TestModel [COLOR yellow][Offline][/COLOR]")

    assert recorder.play_calls == []
    assert len(recorder.notifications) == 1
    assert "offline" in recorder.notifications[0][0].lower()


def test_play_stripchat_model_interop(monkeypatch):
    """Verify _play_stripchat_model works directly (as called by LemonCams)."""
    recorder = _Recorder()

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None, *args, **kwargs):
            self.name = name
            self.progress = type(
                "P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None}
            )()

        def play_from_direct_link(self, url):
            recorder.play_calls.append(url)

    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    stripchat._play_stripchat_model(
        "https://edge-hls.doppiocdn.media/hls/555/master/555.m3u8",
        "model555"
    )

    assert len(recorder.play_calls) == 1
    assert "555_auto.m3u8?pkey=B0p93vi8Uj6AYyZb" in recorder.play_calls[0]


def test_add_model_download_link_labels_offline_models(monkeypatch):
    added = []

    monkeypatch.setattr(
        stripchat.site,
        "add_download_link",
        lambda name, url, mode, img, desc, **k: added.append(name),
    )

    online_model = {"username": "OnlineModel", "isLive": True}
    offline_model = {"username": "OfflineModel", "isLive": False}

    assert stripchat._add_model_download_link(online_model) is True
    assert stripchat._add_model_download_link(offline_model) is True

    assert added[0] == "OnlineModel"
    assert "OfflineModel" in added[1]
    assert "[Offline]" in added[1]


def test_add_model_download_link_can_skip_offline(monkeypatch):
    added = []
    monkeypatch.setattr(
        stripchat.site,
        "add_download_link",
        lambda name, url, mode, img, desc, **k: added.append(name),
    )

    offline_model = {"username": "OfflineModel", "isLive": False}

    result = stripchat._add_model_download_link(offline_model, skip_offline=True)

    assert result is False
    assert added == []


def test_add_model_download_link_skips_items_without_username():
    assert stripchat._add_model_download_link({"isLive": True}) is False


def test_list_parses_models_and_pagination(monkeypatch):
    added_links = []
    added_dirs = []

    models_response = json.dumps({
        "models": [
            {
                "username": "CamGirl1",
                "isLive": True,
                "hlsPlaylist": "https://edge-hls.example/1.m3u8",
                "viewersCount": 1500,
                "country": "us",
            },
            {
                "username": "CamGirl2",
                "isLive": False,
            }
        ],
        "filteredCount": 200,
    })

    monkeypatch.setattr(
        stripchat.utils,
        "get_html_with_cloudflare_retry",
        lambda *a, **k: (models_response, {}),
    )
    monkeypatch.setattr(
        stripchat.site,
        "add_download_link",
        lambda name, url, mode, img, desc, **k: added_links.append(name),
    )
    monkeypatch.setattr(
        stripchat.site,
        "add_dir",
        lambda name, url, mode, img, page, **k: added_dirs.append((name, url, page)),
    )
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)

    stripchat.List("https://stripchat.com/api/front/models?limit=80&offset=0", page=1)

    assert len(added_links) == 2
    assert added_links[0] == "CamGirl1"
    assert "CamGirl2" in added_links[1]
    assert len(added_dirs) == 1
    assert "offset=80" in added_dirs[0][1]
    assert added_dirs[0][2] == 2


def test_list_parses_top_models_response(monkeypatch):
    added = []

    top_response = json.dumps(
        {
            "tops": [
                {
                    "winners": [
                        {"model": {"username": "Winner1", "isLive": True}},
                        {"model": {"username": "Winner2", "isLive": False}},
                    ]
                }
            ]
        }
    )

    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (top_response, {})
    )
    monkeypatch.setattr(
        stripchat.site,
        "add_download_link",
        lambda name, url, mode, img, desc, **k: added.append(name),
    )
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)

    stripchat.List("https://stripchat.com/api/front/v5/models/top?gender=female")

    assert added == ["Winner1", "Winner2 [COLOR yellow][Offline][/COLOR]"]


def test_top_models_prompts_gender_and_delegates_to_list(monkeypatch):
    list_calls = []

    class FakeDialog:
        def select(self, heading, options):
            return 0  # Pick first option

    monkeypatch.setattr(stripchat.xbmcgui, "Dialog", FakeDialog)
    monkeypatch.setattr(stripchat, "List", lambda url: list_calls.append(url))

    stripchat.TopModels()

    assert len(list_calls) == 1
    assert "gender=female" in list_calls[0]
    # the API rejects female rankings without a continent
    assert "continent=eu" in list_calls[0]


def test_top_models_returns_without_prompting_list_when_dialog_cancelled(monkeypatch):
    list_calls = []

    class FakeDialog:
        def select(self, heading, options):
            return -1

    eod_calls = []
    monkeypatch.setattr(stripchat.xbmcgui, "Dialog", FakeDialog)
    monkeypatch.setattr(stripchat, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(stripchat.utils, "eod", lambda: eod_calls.append(True))

    stripchat.TopModels()

    assert list_calls == []
    assert eod_calls == [True]


def test_search_with_keyword_delegates_to_list(monkeypatch):
    list_calls = []
    monkeypatch.setattr(stripchat, "List", lambda url: list_calls.append(url))

    stripchat.Search("search", keyword="chloe")

    assert len(list_calls) == 1
    assert "search/group/username?query=chloe" in list_calls[0]
    assert "primaryTag=" in list_calls[0]


def test_search_without_keyword_opens_search_dir(monkeypatch):
    calls = []
    monkeypatch.setattr(stripchat.site, "search_dir", lambda url, mode: calls.append((url, mode)))

    stripchat.Search("")

    assert calls == [("", "Search")]


def test_clean_database_executes_safely(monkeypatch):
    monkeypatch.setattr(stripchat.sqlite3, "connect", MagicMock())
    monkeypatch.setattr(stripchat.utils, "TRANSLATEPATH", lambda p: p)
    notifications = []
    monkeypatch.setattr(stripchat.utils, "notify", lambda h, m: notifications.append((h, m)))

    stripchat.clean_database(showdialog=True)
    assert notifications == [("Finished", "Stripchat images cleared")]


def test_format_direct_hls_url_upgrades_240p_master_to_auto():
    formatted = stripchat._format_direct_hls_url(
        "https://edge-hls.doppiocdn.media/hls/201593528/master/201593528_240p.m3u8"
    )

    assert formatted.startswith(
        "https://edge-hls.doppiocdn.media/hls/201593528/master/201593528_auto.m3u8?pkey=B0p93vi8Uj6AYyZb|"
    )


def test_list_accepts_missing_page_from_menu(monkeypatch):
    added_links = []
    added_dirs = []
    response = json.dumps({"models": [{"username": "CamGirl1", "isLive": True}], "filteredCount": 200})

    monkeypatch.setattr(stripchat.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (response, {}))
    monkeypatch.setattr(
        stripchat.site, "add_download_link", lambda name, url, mode, img, desc, **k: added_links.append(name)
    )
    monkeypatch.setattr(
        stripchat.site, "add_dir", lambda name, url, mode, img, page, **k: added_dirs.append((url, page))
    )
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)

    # Kodi passes page=None for menu entries that were added without a page
    stripchat.List("https://stripchat.com/api/front/models?limit=80&offset=0", page=None)

    assert added_links == ["CamGirl1"]
    assert added_dirs == [("https://stripchat.com/api/front/models?limit=80&offset=80", 2)]


def test_list_parses_current_top_models_response(monkeypatch):
    added = []
    added_dirs = []
    response = json.dumps({
        "total": 250,
        "items": [
            {"position": 1, "model": {"username": "Top1", "id": 11, "isLive": True, "status": "public"}},
            {"position": 2, "model": {"username": "Top2", "id": 12, "isLive": False, "status": "off"}},
        ],
    })

    monkeypatch.setattr(stripchat.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (response, {}))
    monkeypatch.setattr(
        stripchat.site, "add_download_link", lambda name, url, mode, img, desc, **k: added.append((name, url))
    )
    monkeypatch.setattr(
        stripchat.site, "add_dir", lambda name, url, mode, img, page, **k: added_dirs.append((url, page))
    )
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)

    stripchat.List("https://stripchat.com/api/front/v5/models/top?gender=male&offset=0&limit=100")

    assert added[0] == ("Top1", "https://edge-hls.doppiocdn.media/hls/11/master/11_auto.m3u8")
    assert added[1][0] == "Top2 [COLOR yellow][Offline][/COLOR]"
    assert added_dirs == [("https://stripchat.com/api/front/v5/models/top?gender=male&offset=100&limit=100", 2)]


def test_add_model_download_link_labels_private_shows(monkeypatch):
    added = []
    monkeypatch.setattr(
        stripchat.site, "add_download_link", lambda name, url, mode, img, desc, **k: added.append(name)
    )

    stripchat._add_model_download_link({"username": "Pub", "isLive": True, "status": "public"})
    stripchat._add_model_download_link({"username": "Grp", "isLive": True, "status": "groupShow"})

    assert added == ["Pub", "Grp [COLOR yellow][Private][/COLOR]"]


def test_playvid_blocks_private_labeled_model(monkeypatch):
    recorder = _Recorder()
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg="", *args, **kwargs: recorder.notifications.append((header, msg)),
    )
    monkeypatch.setattr(stripchat, "_play_stripchat_model", lambda url, name: recorder.play_calls.append(url))

    stripchat.Playvid("https://edge-hls.doppiocdn.media/hls/1/master/1_auto.m3u8", "Grp [COLOR yellow][Private][/COLOR]")

    assert recorder.play_calls == []
    assert recorder.notifications == [("Stripchat", "Grp is in a private show")]


@pytest.mark.parametrize("state, expected", [("private", "private show"), ("offline", "offline")])
def test_play_stripchat_model_notifies_when_stream_is_unavailable(monkeypatch, state, expected):
    recorder = _Recorder()
    monkeypatch.setattr(stripchat, "_probe_stream", lambda url: state)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", lambda *a, **k: recorder.play_calls.append(a))
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg="", *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat._play_stripchat_model("https://edge-hls.doppiocdn.media/hls/5/master/5_auto.m3u8", "m")

    assert recorder.play_calls == []
    assert len(recorder.notifications) == 1
    assert expected in recorder.notifications[0][1]


class _FakeResponse:
    def __init__(self, body=b""):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_urlopen(variant_status):
    master = b"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1\nhttps://media-hls.example/1/1.m3u8?pkey=x\n"

    def urlopen(request, timeout=None):
        url = request.full_url
        if "/master/" in url:
            assert "_auto.m3u8" in url and "pkey=B0p93vi8Uj6AYyZb" in url
            return _FakeResponse(master)
        if variant_status != 200:
            raise HTTPError(url, variant_status, "error", {}, None)
        return _FakeResponse(b"#EXTM3U\n")

    return urlopen


@pytest.mark.parametrize("status, expected", [(200, ""), (403, "private"), (404, "offline"), (500, "")])
def test_probe_stream_maps_variant_status(monkeypatch, status, expected):
    monkeypatch.setattr(stripchat, "urlopen", _fake_urlopen(status))

    result = _real_probe_stream("https://edge-hls.doppiocdn.media/hls/1/master/1_240p.m3u8")

    assert result == expected


def test_probe_stream_does_not_block_playback_on_network_error(monkeypatch):
    def boom(request, timeout=None):
        raise OSError("network down")

    monkeypatch.setattr(stripchat, "urlopen", boom)

    assert _real_probe_stream("https://edge-hls.doppiocdn.media/hls/1/master/1_auto.m3u8") == ""
