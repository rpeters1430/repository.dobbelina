"""Tests for camsoda.com site implementation (API-based)."""

import json
from resources.lib.sites import camsoda


def test_list_parses_json(monkeypatch):
    """Test that List correctly parses API JSON data."""
    mock_data = {
        "userList": [
            {
                "username": "Model1",
                "displayName": "Display1",
                "subjectText": "Topic 1",
                "connectionCount": 100,
                "status": "Online",
                "thumbUrl": "https://img.jpg",
                "offlinePictureUrl": "https://fanart.jpg"
            }
        ],
        "perPageCount": 60,
        "totalCount": 120
    }

    downloads = []
    dirs = []

    monkeypatch.setattr(camsoda.utils, "_getHtml", lambda *a, **k: json.dumps(mock_data))
    monkeypatch.setattr(camsoda.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(camsoda.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(camsoda.utils, "eod", lambda: None)
    monkeypatch.setattr(camsoda.utils.addon, "getSetting", lambda x: "false")

    camsoda.List("bu_url", page=1)

    assert len(downloads) == 1
    assert downloads[0] == "Display1"
    
    assert len(dirs) == 1
    assert "Next Page.." in dirs[0]


def test_playvid_parses_json(monkeypatch):
    """Test that Playvid correctly parses stream info JSON."""
    mock_play_data = {
        "stream": {
            "edge_servers": ["edge1.com"],
            "stream_name": "stream1",
            "token": "token1"
        }
    }

    play_calls = []

    class FakeVideoPlayer:
        def __init__(self, name):
            pass
        def play_from_direct_link(self, url):
            play_calls.append(url)

    monkeypatch.setattr(camsoda.utils, "_getHtml", lambda *a, **k: json.dumps(mock_play_data))
    monkeypatch.setattr(camsoda.utils, "VideoPlayer", FakeVideoPlayer)

    camsoda.Playvid("https://www.camsoda.com/api/v1/chat/react/Model1", "Model1")

    assert len(play_calls) == 1
    assert "edge1.com" in play_calls[0]
    assert "token1" in play_calls[0]
