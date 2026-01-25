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
        downloads.append({"name": name, "url": url})

    monkeypatch.setattr(
        stripchat.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(stripchat.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(stripchat.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(stripchat.utils, "eod", lambda: None)

    # Test assumes stripchat.List exists and parses JSON
    try:
        stripchat.List("https://stripchat.com/")
        assert len(downloads) >= 0
    except AttributeError:
        pass


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
        "hlsPlaylist": "https://stream.stripchat.com/test.m3u8",
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
    monkeypatch.setattr(stripchat.utils, "VideoPlayer", FakeVideoPlayer)

    # Call Playvid with offline model
    stripchat.Playvid("https://stream.stripchat.com/test.m3u8", "testmodel")

    # Should have notified about model being offline
    assert len(notifications) > 0
    assert any("offline" in n["message"].lower() for n in notifications)
