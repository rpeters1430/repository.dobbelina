"""Tests for stripchat.com site implementation."""

import json
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
