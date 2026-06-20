"""Tests for LemonCams pagination and playback routing."""

from resources.lib.sites import lemoncams


def test_list_uses_real_pagination_and_adds_next_page(monkeypatch):
    added_links = []
    added_dirs = []

    def fake_api_get(params):
        assert params["function"] == "cams"
        assert params["provider"] == "stripchat"
        assert params["page"] == "1"
        return {
            "cams": [
                {
                    "username": "model1",
                    "provider": "stripchat",
                    "title": "test title",
                    "numberOfUsers": 12,
                    "imageUrl": "https://img.example/model1.jpg",
                    "embedUrl": "https://stream.example/model1.m3u8"
                }
            ],
            "maxPage": 3,
        }

    monkeypatch.setattr(lemoncams, "_api_get", fake_api_get)
    monkeypatch.setattr(
        lemoncams.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: added_links.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        ),
    )
    monkeypatch.setattr(
        lemoncams.site,
        "add_dir",
        lambda name, url, mode, iconimage="", page=None, **kwargs: added_dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "page": page,
            }
        ),
    )
    monkeypatch.setattr(lemoncams.utils, "eod", lambda: None)

    lemoncams.List("stripchat", page=1)

    assert len(added_links) == 1
    assert "model1" in added_links[0]["name"]
    # URL should contain the piped stream URL now
    assert "https://www.lemoncams.com/stripchat/model1|https://stream.example/model1.m3u8" == added_links[0]["url"]
    
    assert added_dirs == [
        {
            "name": "Next Page (2/3)",
            "url": "stripchat",
            "mode": "List",
            "page": 2,
        }
    ]


def test_playvid_plays_cached_hls_directly_with_lemoncams_headers(monkeypatch):
    played = []

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None):
            assert name == "model1"
            assert IA_check == "IA"

        def play_from_direct_link(self, url):
            played.append(url)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakeVideoPlayer)

    lemoncams.Playvid(
        "https://www.lemoncams.com/stripchat/model1|"
        "https://edge.example/master.m3u8",
        "Model 1",
    )

    assert len(played) == 1
    assert played[0].startswith("https://edge.example/master.m3u8|")
    assert "User-Agent=" in played[0]
    assert "Referer=https%3A//www.lemoncams.com/" in played[0]
    assert "Origin=https%3A//www.lemoncams.com/" in played[0]
    assert "manifest_headers=1" in played[0]


def test_playvid_refreshes_missing_stream_before_direct_playback(monkeypatch):
    played = []
    searches = []

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None):
            assert name == "model1"
            assert IA_check == "IA"

        def play_from_direct_link(self, url):
            played.append(url)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(
        lemoncams,
        "_find_model_stream",
        lambda provider, username: (
            searches.append((provider, username))
            or "https://edge.example/refreshed.m3u8"
        ),
    )

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/model1", "Model 1")

    assert searches == [("stripchat", "model1")]
    assert played[0].startswith("https://edge.example/refreshed.m3u8|")


def test_playvid_notifies_when_refreshed_stream_is_missing(monkeypatch):
    notifications = []

    monkeypatch.setattr(lemoncams, "_find_model_stream", lambda *args: "")
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda heading, message, *args, **kwargs: notifications.append(
            (heading, message)
        ),
    )

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/model1", "Model 1")

    assert notifications == [
        ("LemonCams", "Model offline or no stream found")
    ]


def test_search_rejects_non_stripchat_provider(monkeypatch):
    notifications = []

    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )
    monkeypatch.setattr(lemoncams.utils, "eod", lambda: None)

    lemoncams.Search("url", "https://www.lemoncams.com/chaturbate/beckymadsons")

    assert notifications == [("LemonCams", "Only Stripchat models are supported")]


def test_playvid_rejects_non_stripchat_provider(monkeypatch):
    notifications = []
    player_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None):
            player_calls.append(name)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    lemoncams.Playvid("https://www.lemoncams.com/chaturbate/beckymadsons", "beckymadsons")

    assert notifications == [("LemonCams", "Only Stripchat models are supported")]
    assert player_calls == []

