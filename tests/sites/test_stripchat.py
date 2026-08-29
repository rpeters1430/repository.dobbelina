import json

from resources.lib.sites import stripchat


class _Recorder:
    def __init__(self):
        self.play_calls = []
        self.notifications = []


def _model_payload(stream_url):
    return json.dumps(
        {
            "models": [
                {
                    "username": "model1",
                    "isOnline": True,
                    "stream": {
                        "url": stream_url,
                    },
                }
            ]
        }
    )


def test_playvid_uses_proxy_when_required(monkeypatch):
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

    class FakeResponse:
        def __init__(self, text="", status_code=200):
            self.text = text
            self.status_code = status_code

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils.addon,
        "getSetting",
        lambda key: {
            "stripchat_proxy": "true",
            "stripchat_mirror": "true",
        }.get(key, ""),
    )
    monkeypatch.setattr(
        stripchat.utils,
        "get_html_with_cloudflare_retry",
        lambda *args, **kwargs: (_model_payload("https://edge.example.com/live/master.m3u8"), False),
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *args, **kwargs: "")
    monkeypatch.setattr(stripchat.requests, "get", lambda *args, **kwargs: FakeResponse())
    monkeypatch.setattr(stripchat, "_prime_stream_session", lambda *args, **kwargs: None)
    monkeypatch.setattr(stripchat, "_should_use_manifest_proxy", lambda url: True)
    monkeypatch.setattr(
        stripchat, "_start_manifest_proxy", lambda url, name: "http://127.0.0.1:9150/manifest.m3u8"
    )
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg, *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/model1", "model1")

    assert recorder.play_calls == ["http://127.0.0.1:9150/manifest.m3u8"]
    assert recorder.notifications == []


def test_playvid_refuses_raw_playback_when_proxy_disabled(monkeypatch):
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

    class FakeResponse:
        def __init__(self, text="", status_code=200):
            self.text = text
            self.status_code = status_code

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils.addon,
        "getSetting",
        lambda key: {
            "stripchat_proxy": "false",
            "stripchat_mirror": "true",
        }.get(key, ""),
    )
    monkeypatch.setattr(
        stripchat.utils,
        "get_html_with_cloudflare_retry",
        lambda *args, **kwargs: (_model_payload("https://edge.example.com/live/master.m3u8"), False),
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *args, **kwargs: "")
    monkeypatch.setattr(stripchat.requests, "get", lambda *args, **kwargs: FakeResponse())
    monkeypatch.setattr(stripchat, "_prime_stream_session", lambda *args, **kwargs: None)
    monkeypatch.setattr(stripchat, "_should_use_manifest_proxy", lambda url: True)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg, *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/model1", "model1")

    assert recorder.play_calls == []
    assert recorder.notifications == [
        ("Stripchat", "Proxy is disabled. Raw playback would hit 404 placeholder segments.")
    ]


def test_playvid_uses_direct_headers_when_proxy_not_needed(monkeypatch):
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

    class FakeResponse:
        def __init__(self, text="", status_code=200):
            self.text = text
            self.status_code = status_code

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils.addon,
        "getSetting",
        lambda key: {
            "stripchat_proxy": "true",
            "stripchat_mirror": "true",
        }.get(key, ""),
    )
    monkeypatch.setattr(
        stripchat.utils,
        "get_html_with_cloudflare_retry",
        lambda *args, **kwargs: (_model_payload("https://edge.example.com/live/master.m3u8"), False),
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *args, **kwargs: "")
    monkeypatch.setattr(stripchat.requests, "get", lambda *args, **kwargs: FakeResponse())
    monkeypatch.setattr(stripchat, "_prime_stream_session", lambda *args, **kwargs: None)
    monkeypatch.setattr(stripchat, "_should_use_manifest_proxy", lambda url: False)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg, *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/model1", "model1")

    assert len(recorder.play_calls) == 1
    assert recorder.play_calls[0].startswith(
        "https://edge.example.com/live/master.m3u8?playlistType=lowLatency|"
    )
    assert "Origin=https%3A%2F%2Fstripchat.com" in recorder.play_calls[0]
    assert "Referer=https%3A%2F%2Fstripchat.com%2F" in recorder.play_calls[0]
    assert "manifest_headers=1" in recorder.play_calls[0]
    assert recorder.notifications == []


def test_playvid_falls_back_to_exact_username_profile_when_widget_mismatches(monkeypatch):
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
        if "api/external/v4/widget" in url:
            return (
                json.dumps(
                    {
                        "models": [
                            {
                                "username": "SomeoneElse",
                                "stream": {"url": "https://edge.example.com/live/wrong.m3u8"},
                            }
                        ]
                    }
                ),
                False,
            )
        if "api/front/models/username/model1" in url:
            return (
                json.dumps(
                    {
                        "id": 123,
                        "username": "model1",
                        "isOnline": True,
                        "stream": {"url": "https://edge.example.com/live/master.m3u8"},
                    }
                ),
                False,
            )
        return ("", False)

    class FakeResponse:
        def __init__(self, text="", status_code=200):
            self.text = text
            self.status_code = status_code

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils.addon,
        "getSetting",
        lambda key: {
            "stripchat_proxy": "true",
            "stripchat_mirror": "true",
        }.get(key, ""),
    )
    monkeypatch.setattr(
        stripchat.utils,
        "get_html_with_cloudflare_retry",
        fake_cloudflare_retry,
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *args, **kwargs: "")
    monkeypatch.setattr(stripchat.requests, "get", lambda *args, **kwargs: FakeResponse())
    monkeypatch.setattr(stripchat, "_prime_stream_session", lambda *args, **kwargs: None)
    monkeypatch.setattr(stripchat, "_should_use_manifest_proxy", lambda url: False)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg, *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/model1", "model1")

    assert len(recorder.play_calls) == 1
    assert recorder.play_calls[0].startswith(
        "https://edge.example.com/live/master.m3u8?playlistType=lowLatency|"
    )
    assert recorder.notifications == []


def test_playvid_does_not_treat_model_page_as_stream_fallback(monkeypatch):
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
        if "api/external/v4/widget" in url:
            return (json.dumps({"models": [{"username": "SomeoneElse"}]}), False)
        if "api/front/models/username/model1" in url:
            return (
                json.dumps(
                    {
                        "id": 123,
                        "username": "model1",
                        "isOnline": True,
                        "status": "private",
                    }
                ),
                False,
            )
        return ("", False)

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils.addon,
        "getSetting",
        lambda key: {
            "stripchat_proxy": "true",
            "stripchat_mirror": "true",
        }.get(key, ""),
    )
    monkeypatch.setattr(
        stripchat.utils,
        "get_html_with_cloudflare_retry",
        fake_cloudflare_retry,
    )
    monkeypatch.setattr(stripchat, "_prime_stream_session", lambda *args, **kwargs: None)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        stripchat.utils,
        "notify",
        lambda header, msg, *args, **kwargs: recorder.notifications.append((header, msg)),
    )

    stripchat.Playvid("https://stripchat.com/model1", "model1")

    assert recorder.play_calls == []
    assert recorder.notifications == [("Stripchat", "Model is offline")]


def test_proxy_manifest_uses_stable_encoded_segment_urls():
    manifest = "\n".join(
        [
            "#EXTM3U",
            '#EXT-X-MAP:URI="https://cdn.example.com/init.mp4"',
            "#EXTINF:2.0,",
            "https://cdn.example.com/seg1.mp4",
            "#EXTINF:2.0,",
            "https://cdn.example.com/seg2.mp4",
            "",
        ]
    )

    rewritten = stripchat._proxy_segment_urls_in_manifest(manifest, 9150)

    assert 'URI="http://127.0.0.1:9150/seg?u=' in rewritten
    assert rewritten.count("http://127.0.0.1:9150/seg?u=") == 3
    assert "/seg?i=" not in rewritten
    assert "https://cdn.example.com/seg1.mp4" not in rewritten
    assert "https://cdn.example.com/seg2.mp4" not in rewritten


def test_extract_manifest_segment_urls_returns_media_entries_only():
    manifest = "\n".join(
        [
            "#EXTM3U",
            "#EXTINF:2.0,",
            "https://cdn.example.com/seg1.mp4",
            "#EXTINF:2.0,",
            "https://cdn.example.com/seg2.mp4",
            "",
        ]
    )

    assert stripchat._extract_manifest_segment_urls(manifest) == [
        "https://cdn.example.com/seg1.mp4",
        "https://cdn.example.com/seg2.mp4",
    ]


def test_rewrite_mouflon_manifest_can_emit_part_segments_for_proxy():
    manifest = "\n".join(
        [
            "#EXTM3U",
            "#EXT-X-VERSION:6",
            "#EXTINF:2.0,",
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg100_part0.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="https://cdn.example.com/media.mp4",INDEPENDENT=YES',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg100_part1.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="https://cdn.example.com/media.mp4"',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg100.mp4",
            "https://cdn.example.com/media.mp4",
            "",
        ]
    )

    rewritten = stripchat._rewrite_mouflon_for_isa(
        manifest, "https://cdn.example.com/", prefer_full_segments=False
    )

    assert "https://cdn.example.com/seg100_part0.mp4" in rewritten
    assert "https://cdn.example.com/seg100_part1.mp4" in rewritten
    assert "https://cdn.example.com/seg100.mp4" not in rewritten


def test_rewrite_mouflon_prefer_full_segments_with_real_layout():
    """prefer_full_segments=True must pick the full-segment MOUFLON URI even
    when part URIs arrive *before* #EXTINF (the actual Stripchat layout)."""
    manifest = "\n".join(
        [
            "#EXTM3U",
            "#EXT-X-VERSION:6",
            "#EXT-X-TARGETDURATION:2",
            '#EXT-X-MAP:URI="https://cdn.example.com/init.mp4"',
            "#EXT-X-MEDIA-SEQUENCE:4138",
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4138_part0.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="../media.mp4",INDEPENDENT=YES',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4138_part1.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="../media.mp4"',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4138_part2.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="../media.mp4"',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4138_part3.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="../media.mp4"',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4138.mp4",
            "#EXTINF:2.0,",
            "../media.mp4",
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4139_part0.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="../media.mp4",INDEPENDENT=YES',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4139_part1.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="../media.mp4"',
            "#EXT-X-MOUFLON:URI:https://cdn.example.com/seg4139.mp4",
            "#EXTINF:2.0,",
            "../media.mp4",
            "",
        ]
    )

    result = stripchat._rewrite_mouflon_for_isa(
        manifest, "https://cdn.example.com/", prefer_full_segments=True
    )
    lines = result.splitlines()
    full_segs = [line for line in lines if line.startswith("https://cdn.example.com/seg") and "_part" not in line]
    part_segs = [line for line in lines if "_part" in line]
    placeholders = [line for line in lines if "media.mp4" in line and not line.startswith("#")]

    assert len(full_segs) == 2
    assert "https://cdn.example.com/seg4138.mp4" in full_segs
    assert "https://cdn.example.com/seg4139.mp4" in full_segs
    assert part_segs == []
    assert placeholders == []


def test_rewrite_mouflon_prefer_full_segments_with_actual_doppiocdn_layout():
    """Real Stripchat/DoppioCDN layout: #EXTINF appears BEFORE the full-segment
    #EXT-X-MOUFLON:URI tag and after the part tags."""
    manifest = "\n".join(
        [
            "#EXTM3U",
            "#EXT-X-VERSION:6",
            "#EXT-X-TARGETDURATION:2",
            '#EXT-X-MAP:URI="https://media-hls.doppiocdn.media/b-hls-09/228262913/init.mp4"',
            "#EXT-X-MEDIA-SEQUENCE:1590",
            "#EXT-X-MOUFLON:URI:https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1590_part0.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="https://media-hls.doppiocdn.media/b-hls-09/media.mp4",INDEPENDENT=YES',
            "#EXT-X-MOUFLON:URI:https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1590_part1.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="https://media-hls.doppiocdn.media/b-hls-09/media.mp4"',
            "#EXT-X-PROGRAM-DATE-TIME:2026-08-29T00:36:01.433+0000",
            "#EXTINF:2.000",
            "#EXT-X-MOUFLON:URI:https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1590.mp4",
            "https://media-hls.doppiocdn.media/b-hls-09/media.mp4",
            "#EXT-X-MOUFLON:URI:https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1591_part0.mp4",
            '#EXT-X-PART:DURATION=0.500,URI="https://media-hls.doppiocdn.media/b-hls-09/media.mp4",INDEPENDENT=YES',
            "#EXT-X-PROGRAM-DATE-TIME:2026-08-29T00:36:03.458+0000",
            "#EXTINF:2.000",
            "#EXT-X-MOUFLON:URI:https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1591.mp4",
            "https://media-hls.doppiocdn.media/b-hls-09/media.mp4",
            "",
        ]
    )

    result = stripchat._rewrite_mouflon_for_isa(
        manifest, "https://media-hls.doppiocdn.media/b-hls-09/228262913/", prefer_full_segments=True
    )
    lines = result.splitlines()
    full_segs = [line for line in lines if line.startswith("https://media-hls.doppiocdn.media/") and "_part" not in line and not line.startswith("#")]
    part_segs = [line for line in lines if "_part" in line]
    placeholders = [line for line in lines if "media.mp4" in line and not line.startswith("#")]

    assert len(full_segs) == 2
    assert "https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1590.mp4" in full_segs
    assert "https://media-hls.doppiocdn.media/b-hls-09/228262913/seg1591.mp4" in full_segs
    assert part_segs == []
    assert placeholders == []


def test_normalize_and_validate_proxy_segment_url_supported_cdns():
    valid_urls = [
        "https://media-hls.doppiocdn.com/b-hls-20/267251460/init.mp4",
        "https://media-hls.doppiocdn.net/b-hls-20/267251460/init.mp4",
        "https://media-hls.doppiocdn.media/b-hls-09/228262913/init.mp4",
        "https://media-hls.doppiocdn.org/b-hls-09/228262913/init.mp4",
        "https://media-hls.doppiocdn.live/b-hls-09/228262913/init.mp4",
        "https://edge-hls.saawsedge.com/hls/267251460/master.m3u8",
        "https://static-proxy.strpst.com/avatars/test.jpg",
        "https://stripchat.com/api/test",
        "https://stripchat.global/api/test",
    ]
    for url in valid_urls:
        validated = stripchat._normalize_and_validate_proxy_segment_url(url)
        assert validated != "", f"Failed for {url}"

    invalid_urls = [
        "https://evil.com/exploit.mp4",
        "https://doppiocdn.com.evil.com/init.mp4",
        "ftp://doppiocdn.com/file",
        "",
        None,
    ]
    for url in invalid_urls:
        assert stripchat._normalize_and_validate_proxy_segment_url(url) == ""


def test_keep_only_part_window_skips_live_edge_parts():
    manifest = "\n".join(
        [
            "#EXTM3U",
            "#EXT-X-VERSION:6",
            "#EXT-X-MEDIA-SEQUENCE:100",
            '#EXT-X-MAP:URI="https://cdn.example.com/init.mp4"',
            "#EXTINF:0.5,",
            "https://cdn.example.com/p0.mp4",
            "#EXTINF:0.5,",
            "https://cdn.example.com/p1.mp4",
            "#EXTINF:0.5,",
            "https://cdn.example.com/p2.mp4",
            "#EXTINF:0.5,",
            "https://cdn.example.com/p3.mp4",
            "#EXTINF:0.5,",
            "https://cdn.example.com/p4.mp4",
            "#EXTINF:0.5,",
            "https://cdn.example.com/p5.mp4",
            "",
        ]
    )

    rewritten = stripchat._keep_only_part_window(manifest, keep_count=2, edge_buffer=2)

    assert "https://cdn.example.com/p2.mp4" in rewritten
    assert "https://cdn.example.com/p3.mp4" in rewritten
    assert "https://cdn.example.com/p4.mp4" not in rewritten
    assert "https://cdn.example.com/p5.mp4" not in rewritten


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


def test_playvid_blocks_offline_models(monkeypatch):
    notifications = []
    play_calls = []

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils, "notify", lambda header, msg="": notifications.append((header, msg))
    )
    monkeypatch.setattr(
        stripchat, "_play_stripchat_model", lambda url, name: play_calls.append((url, name))
    )

    stripchat.Playvid("", "SomeModel [COLOR yellow][Offline][/COLOR]")

    assert play_calls == []
    assert len(notifications) == 1
    assert "offline" in notifications[0][0].lower()


def test_playvid_plays_online_models(monkeypatch):
    play_calls = []

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat, "_play_stripchat_model", lambda url, name: play_calls.append((url, name))
    )

    stripchat.Playvid("https://stripchat.com/x", "SomeModel")

    assert play_calls == [("https://stripchat.com/x", "SomeModel")]


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

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (top_response, {})
    )
    monkeypatch.setattr(
        stripchat.utils.addon, "getSetting", lambda key: "false" if key == "online_only" else ""
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

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)

    class FakeDialog:
        def select(self, heading, options):
            # Always pick "Girls" (index 0), which triggers a region prompt too.
            return 0

    monkeypatch.setattr(stripchat.xbmcgui, "Dialog", FakeDialog)
    monkeypatch.setattr(
        stripchat.utils.addon, "getSetting", lambda key: "false" if key == "online_only" else ""
    )
    monkeypatch.setattr(stripchat.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(stripchat, "List", lambda url: list_calls.append(url))

    stripchat.TopModels()

    assert len(list_calls) == 1
    assert "gender=female" in list_calls[0]
    assert "continent=" in list_calls[0]


def test_top_models_returns_without_prompting_list_when_dialog_cancelled(monkeypatch):
    list_calls = []

    monkeypatch.setattr(stripchat, "STRIPCHAT_DISABLED", False)

    class FakeDialog:
        def select(self, heading, options):
            return -1

    monkeypatch.setattr(stripchat.xbmcgui, "Dialog", FakeDialog)
    monkeypatch.setattr(stripchat, "List", lambda url: list_calls.append(url))

    stripchat.TopModels()

    assert list_calls == []
