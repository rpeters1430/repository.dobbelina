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


def _mock_stripchat_module(monkeypatch, stripchat_module):
    import sys
    import resources.lib.sites

    monkeypatch.setitem(sys.modules, "resources.lib.sites.stripchat", stripchat_module)
    if hasattr(resources.lib.sites, "stripchat"):
        monkeypatch.setattr(resources.lib.sites, "stripchat", stripchat_module)


def test_playvid_delegates_to_stripchat(monkeypatch):
    delegated = []

    class MockStripchat:
        @staticmethod
        def _play_stripchat_model(url, username):
            delegated.append((url, username))

    _mock_stripchat_module(monkeypatch, MockStripchat)

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/model1", "Model 1")

    assert delegated == [("https://stripchat.com/model1", "model1")]


def test_playvid_plays_cached_stream_url_directly_when_delegation_fails(monkeypatch):
    class FailingStripchat:
        @staticmethod
        def _play_stripchat_model(url, username):
            raise RuntimeError("boom")

    _mock_stripchat_module(monkeypatch, FailingStripchat)

    played = []

    class FakePlayer:
        def __init__(self, name, IA_check=None):
            self.name = name

        def play_from_direct_link(self, link):
            played.append(link)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakePlayer)

    lemoncams.Playvid(
        "https://www.lemoncams.com/stripchat/model1|https://stream.example/model1.m3u8",
        "Model 1",
    )

    assert len(played) == 1
    assert played[0].startswith("https://stream.example/model1.m3u8|")


def test_playvid_falls_back_to_listing_search_when_no_cached_url(monkeypatch):
    class FailingStripchat:
        @staticmethod
        def _play_stripchat_model(url, username):
            raise RuntimeError("boom")

    _mock_stripchat_module(monkeypatch, FailingStripchat)

    monkeypatch.setattr(lemoncams, "_find_model_stream", lambda provider, username, **kw: "")
    notifications = []
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/model1", "Model 1")

    assert notifications == [("LemonCams", "Model offline or no stream found")]


def test_playvid_rejects_non_stripchat_provider(monkeypatch):
    notifications = []

    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    lemoncams.Playvid("https://www.lemoncams.com/chaturbate/beckymadsons", "beckymadsons")

    assert notifications == [("LemonCams", "Only Stripchat models are supported")]


def test_search_adds_download_link_directly(monkeypatch):
    added_links = []

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
    monkeypatch.setattr(lemoncams.utils, "eod", lambda: None)

    lemoncams.Search("any", "model1")

    assert len(added_links) == 1
    assert added_links[0]["name"] == "model1"
    assert added_links[0]["url"] == "https://www.lemoncams.com/stripchat/model1"
    assert added_links[0]["mode"] == "Playvid"


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

