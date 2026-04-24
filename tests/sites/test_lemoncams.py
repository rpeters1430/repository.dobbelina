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


class MockKodiPlayer:
    def __init__(self):
        self._playing = True
    def isPlaying(self):
        res = self._playing
        self._playing = False # Stop after one check to exit loop
        return res
    def stop(self):
        pass


def test_playvid_uses_direct_stream(monkeypatch):
    play_calls = []

    monkeypatch.setattr(lemoncams.xbmc, "Player", MockKodiPlayer)
    
    class MockVP:
        def __init__(self, name):
            self.name = name
            self.IA_check = None
        def play_from_direct_link(self, url):
            play_calls.append({"name": self.name, "url": url})

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", MockVP)
    
    # Test with piped URL
    url = "https://www.lemoncams.com/stripchat/model1|https://stream.example/model1.m3u8"
    lemoncams.Playvid(url, "Model 1")
    
    assert len(play_calls) == 1
    assert play_calls[0]["name"] == "Model 1"
    assert "https://stream.example/model1.m3u8" in play_calls[0]["url"]
    assert "User-Agent=" in play_calls[0]["url"]
    assert "Referer=" in play_calls[0]["url"]


def test_playvid_searches_if_no_cached_stream(monkeypatch):
    play_calls = []
    
    def fake_fetch_payload(provider, page):
        return {
            "cams": [
                {
                    "username": "model1",
                    "provider": "stripchat",
                    "embedUrl": "https://newstream.example/model1.m3u8"
                }
            ]
        }

    class MockVP:
        def __init__(self, name):
            self.name = name
        def play_from_direct_link(self, url):
            play_calls.append({"url": url})

    monkeypatch.setattr(lemoncams, "_fetch_provider_payload", fake_fetch_payload)
    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", MockVP)
    monkeypatch.setattr(lemoncams.xbmc, "Player", MockKodiPlayer)
    
    # Test with URL without piped stream
    url = "https://www.lemoncams.com/stripchat/model1"
    lemoncams.Playvid(url, "Model 1")
    
    assert len(play_calls) == 1
    assert "https://newstream.example/model1.m3u8" in play_calls[0]["url"]


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
    play_calls = []

    class MockVP:
        def __init__(self, name):
            self.name = name
        def play_from_direct_link(self, url):
            play_calls.append(url)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", MockVP)
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    lemoncams.Playvid("https://www.lemoncams.com/chaturbate/beckymadsons", "beckymadsons")

    assert notifications == [("LemonCams", "Only Stripchat models are supported")]
    assert play_calls == []
