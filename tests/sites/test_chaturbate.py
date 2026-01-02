"""Tests for chaturbate.com site implementation."""

import json
from resources.lib.sites import chaturbate


def test_list_parses_json_models(monkeypatch):
    """Test that List correctly parses JSON model data."""
    json_data = {
        "rooms": [
            {
                "username": "model1",
                "display_age": 25,
                "location": "USA",
                "subject": "Welcome to my room",
                "start_timestamp": 1640000000,
                "num_users": 1234,
                "num_followers": 5678,
                "current_show": "public",
                "tags": ["blonde", "bigboobs"],
                "img": "https://thumb.live.mmcdn.com/model1.jpg",
                "is_following": False,
            },
            {
                "username": "model2",
                "display_age": 22,
                "location": "Colombia",
                "subject": "Private show #latina #teen",
                "start_timestamp": 1640001000,
                "num_users": 890,
                "num_followers": 2345,
                "current_show": "private",
                "tags": ["latina", "teen"],
                "img": "https://thumb.live.mmcdn.com/model2.jpg",
                "is_following": True,
            },
        ],
        "total_count": 2,
    }

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return json.dumps(json_data)

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url, "icon": iconimage, "desc": desc})

    monkeypatch.setattr(chaturbate.utils, "_getHtml", fake_get_html)
    monkeypatch.setattr(chaturbate.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(chaturbate.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(chaturbate.utils, "eod", lambda: None)
    monkeypatch.setattr(chaturbate.addon, "getSetting", lambda x: "false")

    chaturbate.List(
        "https://chaturbate.com/api/ts/roomlist/room-list/?limit=100&offset=0"
    )

    assert len(downloads) == 2
    assert "model1" in downloads[0]["name"]
    assert "25" in downloads[0]["name"]
    assert "public" in downloads[0]["name"]
    assert "https://chaturbate.com/model1/" in downloads[0]["url"]
    assert "model2" in downloads[1]["name"]
    assert "private" in downloads[1]["name"]


def test_list_pagination(monkeypatch):
    """Test that List handles pagination correctly."""
    json_data = {
        "rooms": [
            {
                "username": "model1",
                "display_age": 25,
                "location": "USA",
                "subject": "Test",
                "start_timestamp": 1640000000,
                "num_users": 100,
                "num_followers": 200,
                "current_show": "public",
                "tags": [],
                "img": "thumb.jpg",
                "is_following": False,
            }
        ],
        "total_count": 250,  # More than 100, so pagination needed
    }

    dirs = []

    def fake_add_dir(name, url, mode, *args, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(
        chaturbate.utils, "_getHtml", lambda *a, **k: json.dumps(json_data)
    )
    monkeypatch.setattr(chaturbate.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(chaturbate.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(chaturbate.utils, "eod", lambda: None)
    monkeypatch.setattr(chaturbate.addon, "getSetting", lambda x: "false")

    chaturbate.List(
        "https://chaturbate.com/api/ts/roomlist/room-list/?limit=100&offset=0", page=1
    )

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "offset=101" in next_pages[0]["url"]
    assert "Page 1 of 3" in next_pages[0]["name"]


def test_tags_parses_json(monkeypatch):
    """Test that Tags function parses JSON tag data."""
    json_data = {
        "hashtags": [
            {
                "hashtag": "bigboobs",
                "room_count": 123,
                "top_rooms": [{"img": "thumb1.jpg"}],
            },
            {
                "hashtag": "latina",
                "room_count": 456,
                "top_rooms": [{"img": "thumb2.jpg"}],
            },
        ],
        "total": 2,
    }

    dirs = []

    def fake_add_dir(name, url, mode, iconimage, *args, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(
        chaturbate.utils, "getHtml", lambda *a, **k: json.dumps(json_data)
    )
    monkeypatch.setattr(chaturbate.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(chaturbate.utils, "eod", lambda: None)

    chaturbate.Tags(
        "https://chaturbate.com/api/ts/hashtags/tag-table-data/?sort=ht&page=1&g=f&limit=100",
        page=1,
    )

    assert len(dirs) == 2
    assert "bigboobs" in dirs[0]["name"]
    assert "[123]" in dirs[0]["name"]
    assert "latina" in dirs[1]["name"]
    assert "[456]" in dirs[1]["name"]


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls SList with encoded query."""
    slist_calls = []

    def fake_slist(url):
        slist_calls.append(url)

    monkeypatch.setattr(chaturbate, "SList", fake_slist)

    chaturbate.Search(
        "https://chaturbate.com/ax/search/?keywords=", keyword="test query"
    )

    assert len(slist_calls) == 1
    assert "test+query" in slist_calls[0]


def test_playvid_parses_room_data(monkeypatch):
    """Test that Playvid extracts initialRoomDossier from page."""
    html = """
    <html>
    <script>
    var initialRoomDossier = "{\\"hls_source\\": \\"https://stream.chaturbate.com/live/model1.m3u8\\", \\"broadcaster_username\\": \\"model1\\", \\"viewer_username\\": \\"anonymous123\\", \\"room_pass\\": \\"pass123\\", \\"edge_auth\\": \\"auth123\\"}";
    </script>
    </html>
    """

    video_player_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.name = name
            video_player_calls.append(("init", name))

        def play_from_direct_link(self, url):
            video_player_calls.append(("play", url))

    def fake_get_html(*args, **kwargs):
        return html, False

    monkeypatch.setattr(
        chaturbate.utils, "get_html_with_cloudflare_retry", fake_get_html
    )
    monkeypatch.setattr(chaturbate.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(chaturbate.addon, "getSetting", lambda x: "0")

    chaturbate.Playvid("https://chaturbate.com/model1/", "Model1")

    assert len(video_player_calls) == 2
    assert video_player_calls[0] == ("init", "Model1")
    assert video_player_calls[1][0] == "play"
    assert "https://stream.chaturbate.com/live/model1.m3u8" in video_player_calls[1][1]
