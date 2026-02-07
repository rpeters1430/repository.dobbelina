"""Tests for bongacams.com site implementation (API-based)."""

import json
from resources.lib.sites import bongacams


def test_list_parses_json(monkeypatch):
    """Test that List correctly parses API JSON data."""
    mock_data = [
        {
            "username": "Model1",
            "display_name": "Display1",
            "display_age": 22,
            "hd_cam": True,
            "profile_images": {"thumbnail_image_big_live": "//img.jpg"},
            "gender": "Female",
            "ethnicity": "Ethnicity1",
            "primary_language": "English",
            "secondary_language": None,
            "hair_color": "Brown",
            "eye_color": "Blue",
            "height": "170",
            "weight": "60",
            "bust_penis_size": "Large",
            "pubic_hair": "Smooth",
            "vibratoy": True,
            "turns_on": "Likes",
            "turns_off": "Dislikes",
            "tags": ["Tag1", "Tag2"],
        }
    ]

    downloads = []

    monkeypatch.setattr(
        bongacams.utils, "_getHtml", lambda *a, **k: json.dumps(mock_data)
    )
    monkeypatch.setattr(
        bongacams.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(bongacams.utils, "eod", lambda: None)
    monkeypatch.setattr(bongacams.utils.addon, "getSetting", lambda x: "false")

    bongacams.List("bu_url")

    assert len(downloads) == 1
    assert "Display1" in downloads[0]
    assert "[22]" in downloads[0]
    assert "HD" in downloads[0]


def test_playvid_parses_json(monkeypatch):
    """Test that Playvid correctly parses AMF JSON response."""
    mock_amf_data = {
        "status": "success",
        "performerData": {"showType": "public"},
        "localData": {"videoServerUrl": "//server.com"},
    }

    play_calls = []

    class FakeVideoPlayer:
        def __init__(self, name):
            self.progress = type(
                "obj", (object,), {"update": lambda *a: None, "close": lambda *a: None}
            )

        def play_from_direct_link(self, url):
            play_calls.append(url)

    monkeypatch.setattr(
        bongacams.utils, "_postHtml", lambda *a, **k: json.dumps(mock_amf_data)
    )
    monkeypatch.setattr(
        bongacams.utils, "_getHtml", lambda *a, **k: "dummy m3u8 content"
    )
    monkeypatch.setattr(bongacams.utils, "VideoPlayer", FakeVideoPlayer)

    bongacams.Playvid("Model1", "Model1")

    assert len(play_calls) == 1
    assert "server.com" in play_calls[0]
    assert "stream_Model1" in play_calls[0]
