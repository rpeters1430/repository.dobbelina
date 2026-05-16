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


def test_list2_parses_redesigned_contest_payload(monkeypatch):
    payload = {
        "data": {
            "topRooms": {
                "content": {
                    "winners": {
                        "timePeriod": "Current hour",
                        "thumbs": [
                            {
                                "liveBadge": {},
                                "footer": {"displayName": "Model One"},
                                "link": {"url": {"url": "/modelone/"}},
                                "avatar": {"src": "//img.example/model.jpg"},
                                "stripe": {"place": "1"},
                                "content": [
                                    {"text": "123 members"},
                                    {"text": "Prize $100"},
                                ],
                            }
                        ],
                    }
                }
            }
        }
    }
    links = []

    monkeypatch.setattr(
        bongacams.utils,
        "get_html_with_cloudflare_retry",
        lambda *a, **k: (json.dumps(payload), False),
    )
    monkeypatch.setattr(
        bongacams.site,
        "add_download_link",
        lambda *a, **k: links.append({"name": a[0], "url": a[1], "desc": a[4]}),
    )
    monkeypatch.setattr(bongacams.utils.addon, "getSetting", lambda x: "false")
    monkeypatch.setattr(bongacams.utils, "eod", lambda: None)

    bongacams.List2("https://bongacams.com/contest/top-room?cp=1")

    assert any("Current contest standings: Current hour" in item["name"] for item in links)
    model_link = [item for item in links if item["name"] == "Model One"][0]
    assert model_link["url"] == "modelone"
    assert "Viewers: 123" in model_link["desc"]


def test_playvid_uses_performer_username(monkeypatch):
    mock_amf_data = {
        "status": "success",
        "performerData": {"showType": "public", "username": "CanonicalName"},
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
    monkeypatch.setattr(bongacams.utils, "_getHtml", lambda *a, **k: "#EXTM3U")
    monkeypatch.setattr(bongacams.utils, "VideoPlayer", FakeVideoPlayer)

    bongacams.Playvid("OldName", "Model")

    assert "stream_CanonicalName" in play_calls[0]
