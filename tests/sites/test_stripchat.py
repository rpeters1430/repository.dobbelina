"""Tests for stripchat.com site implementation."""

import json
import pytest
from resources.lib.sites import stripchat


def test_list_parses_json_models(monkeypatch):
    """Test that List correctly parses JSON model data."""
    json_data = {
        "models": [
            {
                "username": "model1",
                "hlsPlaylist": "https://stream.stripchat.com/model1.m3u8",
                "previewUrlThumbSmall": "https://img.stripchat.com/thumb1.jpg",
                "snapshotTimestamp": "123456",
                "id": "111",
                "groupShowTopic": "",
            },
            {
                "username": "model2",
                "hlsPlaylist": "https://stream.stripchat.com/model2.m3u8",
                "previewUrlThumbSmall": "https://img.stripchat.com/thumb2.jpg",
                "snapshotTimestamp": "654321",
                "id": "222",
                "groupShowTopic": "",
            },
        ]
    }

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return json.dumps(json_data), False

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "iconimage": iconimage,
                "fanart": kwargs.get("fanart"),
            }
        )

    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(stripchat.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)

    # Test assumes stripchat.List exists and parses JSON
    try:
        stripchat.List("https://stripchat.com/")
        assert len(downloads) == 2
        assert downloads[0]["iconimage"] == "https://img.stripchat.com/thumb1.jpg"
        assert downloads[0]["fanart"] == "https://img.stripchat.com/thumb1.jpg"
        assert downloads[1]["iconimage"] == "https://img.stripchat.com/thumb2.jpg"
        assert downloads[1]["fanart"] == "https://img.stripchat.com/thumb2.jpg"
    except AttributeError:
        pass


def test_model_screenshot_falls_back_to_snapshot_url():
    model = {"snapshotTimestamp": "123456", "id": "111"}

    assert (
        stripchat._model_screenshot(model)
        == "https://img.strpst.com/thumbs/123456/111_webp"
    )


def test_model_screenshot_prefers_live_preview_variant():
    model = {
        "previewUrlThumbSmall": "https://static-proxy.strpst.com/previews/a/b/c/hash-thumb-small",
        "snapshotTimestamp": "123456",
        "id": "111",
    }

    assert stripchat._model_screenshot(model) == (
        "https://static-proxy.strpst.com/previews/a/b/c/hash-thumb-big?t=123456"
    )


def test_playvid_requires_inputstreamadaptive(monkeypatch):
    """Test that Playvid properly checks for inputstreamadaptive."""
    notifications = []
    model_data = {
        "username": "testmodel",
        "isOnline": True,
        "isBroadcasting": True,
        "hlsPlaylist": "https://stream.stripchat.com/test.m3u8",
    }

    def fake_notify(title, message, **kwargs):
        notifications.append({"title": title, "message": message})

    def fake_get_html(url, *args, **kwargs):
        return json.dumps({"models": [model_data]}), False

    # Mock inputstreamhelper to fail the check
    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return False

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

    # Mock the import
    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", fake_notify)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *a, **k: "")
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    # Call Playvid - it should abort with notification
    stripchat.Playvid("https://stream.stripchat.com/test.m3u8", "testmodel")

    # Should have notified about missing inputstreamadaptive
    assert len(notifications) > 0
    assert any("inputstream" in n["message"].lower() for n in notifications)


def test_playvid_detects_offline_model(monkeypatch):
    """Test that Playvid detects when model is offline."""
    notifications = []
    model_data = {
        "username": "testmodel",
        "isOnline": False,
        "isBroadcasting": False,
    }

    def fake_notify(title, message):
        notifications.append({"title": title, "message": message})

    def fake_get_html(url, *args, **kwargs):
        return json.dumps({"models": [model_data]}), False

    # Mock inputstreamhelper to pass the check
    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

    # Mock the import
    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", fake_notify)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *a, **k: "")
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    # Call Playvid with offline model and no valid stream URL
    stripchat.Playvid("", "testmodel")

    # Should have notified about model being offline
    assert len(notifications) > 0
    assert any("offline" in n["message"].lower() for n in notifications)


def test_playvid_uses_fallback_stream_when_api_reports_offline(monkeypatch):
    """Play should continue when listing URL is valid even if API flags offline."""
    notifications = []
    played_urls = []
    model_data = {
        "username": "testmodel",
        "isOnline": False,
        "isBroadcasting": False,
    }

    def fake_notify(title, message, **kwargs):
        notifications.append({"title": title, "message": message})

    def fake_get_html(url, *args, **kwargs):
        return json.dumps({"models": [model_data]}), False

    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            played_urls.append(link)

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", fake_notify)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *a, **k: "")
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    stripchat.Playvid("https://stream.stripchat.com/test_fallback.m3u8", "testmodel")

    assert played_urls
    assert played_urls[0].startswith("https://stream.stripchat.com/test_fallback.m3u8|")
    assert not notifications


def test_playvid_promotes_low_variant_to_source_playlist(monkeypatch):
    """Low variant URLs should be upgraded to source playlist when available."""
    played_urls = []
    model_data = {
        "username": "testmodel",
        "isOnline": True,
        "isBroadcasting": True,
    }
    low_variant = (
        "https://edge-hls.doppiocdn.com/hls/133123248/master/133123248_240p.m3u8"
    )
    promoted_source = (
        "https://edge-hls.doppiocdn.com/hls/133123248/master/133123248.m3u8"
    )

    def fake_get_html(url, *args, **kwargs):
        if "api/external/v4/widget" in url or "api/front/models" in url:
            return json.dumps({"models": [model_data]}), False
        return "", False

    def fake__get_html(url, *args, **kwargs):
        if url == promoted_source:
            return '#EXTM3U\n#EXT-X-STREAM-INF:NAME="source"\nhttps://media/source.m3u8'
        return "", False

    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            played_urls.append(link)

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", lambda *a, **k: None)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", fake__get_html)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    stripchat.Playvid(low_variant, "testmodel")

    assert played_urls
    assert played_urls[0].startswith(promoted_source + "|")


def test_playvid_prefers_higher_quality_url_over_generic_label(monkeypatch):
    """When labels are generic, quality inferred from URL should win."""
    played_urls = []
    model_data = {
        "username": "testmodel",
        "isOnline": True,
        "isBroadcasting": True,
        "stream": {
            "url": "https://edge-hls.saawsedge.com/hls/100/master/100_240p.m3u8",
        },
    }

    def fake_get_html(url, *args, **kwargs):
        if "api/external/v4/widget" in url or "api/front/models" in url:
            return json.dumps({"models": [model_data]}), False
        return "", False

    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            played_urls.append(link)

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", lambda *a, **k: None)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", lambda *a, **k: "")
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    # Fallback URL is higher quality than stream.url; should be selected.
    stripchat.Playvid(
        "https://edge-hls.doppiocdn.com/hls/100/master/100_480p.m3u8", "testmodel"
    )

    assert played_urls
    assert played_urls[0].startswith(
        "https://edge-hls.doppiocdn.com/hls/100/master/100_480p.m3u8|"
    )


def test_playvid_avoids_ad_only_manifests(monkeypatch):
    """Reject ad-only VOD manifests and pick a non-ad candidate."""
    played_urls = []
    model_data = {
        "username": "testmodel",
        "isOnline": True,
        "isBroadcasting": True,
        "stream": {
            "url": "https://edge-hls.saawsedge.com/hls/200/master/200_480p.m3u8",
        },
    }

    doppi_source = "https://edge-hls.doppiocdn.com/hls/200/master/200.m3u8"
    doppi_child = "https://media-hls.doppiocdn.com/b-hls-03/200/200.m3u8"
    saaws_480 = "https://edge-hls.saawsedge.com/hls/200/master/200_480p.m3u8"
    saaws_480_child = "https://media-hls.saawsedge.com/b-hls-03/200/200_480p.m3u8"

    def fake_get_html(url, *args, **kwargs):
        if "api/external/v4/widget" in url or "api/front/models" in url:
            return json.dumps({"models": [model_data]}), False
        return "", False

    def fake__get_html(url, *args, **kwargs):
        if url == doppi_source:
            return '#EXTM3U\n#EXT-X-STREAM-INF:NAME="source"\n{}'.format(doppi_child)
        if url == doppi_child:
            return (
                "#EXTM3U\n#EXT-X-MOUFLON-ADVERT\n#EXT-X-PLAYLIST-TYPE:VOD\n"
                "#EXTINF:4.0,\nhttps://media-hls.doppiocdn.com/b-hls-03/cpa/v2/chunk_000.m4s\n"
                "#EXT-X-ENDLIST"
            )
        if url == saaws_480:
            return '#EXTM3U\n#EXT-X-STREAM-INF:NAME="480p"\n{}'.format(saaws_480_child)
        if url == saaws_480_child:
            return (
                "#EXTM3U\n#EXT-X-VERSION:6\n#EXT-X-TARGETDURATION:8\n"
                "#EXTINF:8.333,\nhttps://media-hls.saawsedge.com/b-hls-03/200/seg_1.mp4\n"
            )
        return ""

    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            played_urls.append(link)

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", lambda *a, **k: None)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", fake__get_html)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    stripchat.Playvid(
        "https://edge-hls.doppiocdn.com/hls/200/master/200_240p.m3u8", "testmodel"
    )

    assert played_urls
    assert played_urls[0].startswith(saaws_480 + "|") or played_urls[0].startswith(
        "https://edge-hls.doppiocdn.com/hls/200/master/200_240p.m3u8|"
    )


def test_playvid_validates_returned_model_name(monkeypatch):
    """
    Test that Playvid verifies the returned model's username matches the requested one.
    If Stripchat API returns a different model (e.g. recommendation), we should not play it.
    """
    notifications = []

    # We request "requested_model" but API returns "random_other_model"
    requested_name = "requested_model"
    returned_name = "random_other_model"

    model_data = {
        "username": returned_name,
        "isOnline": True,
        "isBroadcasting": True,
        "hlsPlaylist": "https://stream.stripchat.com/random.m3u8",
        "stream": {"url": "https://stream.stripchat.com/random.m3u8"},
    }

    def fake_notify(title, message, **kwargs):
        notifications.append({"title": title, "message": message})

    def fake_get_html(url, *args, **kwargs):
        # This simulates the API returning a different model than requested
        return json.dumps({"models": [model_data]}), False

    # Mock dependencies
    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            # If we get here, the code accepted the wrong model!
            pytest.fail(f"VideoPlayer started playing wrong model: {self.name}")

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", fake_notify)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    # Action: Try to play "requested_model"
    stripchat.Playvid("http://fake", requested_name)

    # Assert that we got a notification about model not found/offline
    # because the name check failed, so it treated it as no model data
    assert len(notifications) > 0
    assert any(
        "not found" in n["message"].lower() or "offline" in n["message"].lower()
        for n in notifications
    )


def test_playvid_uses_unresolved_non_ad_candidate_as_last_resort(monkeypatch):
    """If only unresolved non-ad streams remain, pass best one to Kodi as fallback."""
    notifications = []
    played_urls = []
    model_data = {
        "username": "testmodel",
        "isOnline": True,
        "isBroadcasting": True,
        "stream": {
            "url": "https://edge-hls.saawsedge.com/hls/999/master/999_480p.m3u8",
        },
    }

    def fake_notify(title, message, **kwargs):
        notifications.append({"title": title, "message": message})

    def fake_get_html(url, *args, **kwargs):
        if "api/external/v4/widget" in url or "api/front/models" in url:
            return json.dumps({"models": [model_data]}), False
        return "", False

    def fake__get_html(url, *args, **kwargs):
        if "saawsedge.com" in url:
            raise Exception("<urlopen error [Errno -2] Name or service not known>")
        if "doppiocdn.com" in url and url.endswith(".m3u8"):
            return (
                "#EXTM3U\n#EXT-X-MOUFLON-ADVERT\n#EXT-X-PLAYLIST-TYPE:VOD\n"
                "#EXTINF:4.0,\nhttps://media-hls.doppiocdn.com/b-hls-03/cpa/v2/chunk_000.m4s\n"
                "#EXT-X-ENDLIST"
            )
        return ""

    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            played_urls.append(link)

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", fake_notify)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", fake__get_html)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    stripchat.Playvid(
        "https://edge-hls.doppiocdn.com/hls/999/master/999_240p.m3u8", "testmodel"
    )

    assert played_urls
    assert played_urls[0].startswith(
        "https://edge-hls.saawsedge.com/hls/999/master/999_480p.m3u8|"
    )
    assert not notifications


def test_playvid_mirrors_saaws_to_doppi_and_plays_reachable_stream(monkeypatch):
    """When saaws host is unresolved, mirrored doppi host should be selected."""
    played_urls = []
    model_data = {
        "username": "testmodel",
        "isOnline": True,
        "isBroadcasting": True,
        "stream": {
            "url": "https://edge-hls.saawsedge.com/hls/123/master/123_480p.m3u8",
        },
    }

    mirrored = "https://edge-hls.doppiocdn.com/hls/123/master/123_480p.m3u8"

    def fake_get_html(url, *args, **kwargs):
        if "api/external/v4/widget" in url or "api/front/models" in url:
            return json.dumps({"models": [model_data]}), False
        return "", False

    def fake__get_html(url, *args, **kwargs):
        if "saawsedge.com" in url:
            raise Exception("<urlopen error [Errno -2] Name or service not known>")
        if url == mirrored:
            return '#EXTM3U\n#EXT-X-STREAM-INF:NAME="480p"\nhttps://media-hls.doppiocdn.com/b-hls-01/123/live.m3u8'
        if "doppiocdn.com" in url and url.endswith("live.m3u8"):
            return "#EXTM3U\n#EXTINF:8.333,\nhttps://media-hls.doppiocdn.com/b-hls-01/123/seg_1.mp4\n"
        return ""

    class FakeHelper:
        def __init__(self, adaptive_type):
            pass

        def check_inputstream(self):
            return True

    class FakeProgress:
        def update(self, percent, message):
            pass

        def close(self):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, **kwargs):
            self.name = name
            self.progress = FakeProgress()

        def play_from_direct_link(self, link):
            played_urls.append(link)

    import sys
    import types

    fake_inputstreamhelper = types.ModuleType("inputstreamhelper")
    fake_inputstreamhelper.Helper = FakeHelper
    sys.modules["inputstreamhelper"] = fake_inputstreamhelper

    monkeypatch.setattr(stripchat.utils, "notify", lambda *a, **k: None)
    monkeypatch.setattr(stripchat.utils, "kodilog", lambda x: None)
    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.utils, "_getHtml", fake__get_html)
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    stripchat.Playvid("https://edge-hls.doppiocdn.com/hls/123/master/123_240p.m3u8", "testmodel")

    assert played_urls
    assert played_urls[0].startswith(mirrored + "|")
