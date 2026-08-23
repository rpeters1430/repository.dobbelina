"""Comprehensive tests for LemonCams scraper and multi-provider stream resolution."""

import json
from resources.lib.sites import lemoncams


def test_main_menu(monkeypatch):
    dirs = []

    def fake_add_dir(name, url, mode, iconimage="", page=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "page": page})

    monkeypatch.setattr(lemoncams.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(lemoncams.utils, "eod", lambda: None)

    lemoncams.Main()

    modes = [d["mode"] for d in dirs]
    urls = [d["url"] for d in dirs]

    assert "List" in modes
    assert "Search" in modes
    assert "__top__" in urls
    assert "stripchat" in urls
    assert "camsoda" in urls
    assert "myfreecams" in urls


def test_list_parses_multi_provider_models(monkeypatch):
    added_links = []
    added_dirs = []

    def fake_api_get(params):
        return {
            "cams": [
                {
                    "username": "model_sc",
                    "provider": "stripchat",
                    "title": "Stripchat Live",
                    "numberOfUsers": 1200,
                    "gender": "female",
                    "country": "us",
                    "imageUrl": "https://img.example/sc.jpg",
                    "embedUrl": None,
                },
                {
                    "username": "model_cs",
                    "provider": "camsoda",
                    "title": "Camsoda Live",
                    "numberOfUsers": 450,
                    "gender": "female",
                    "country": "co",
                    "imageUrl": "https://img.example/cs.jpg",
                    "embedUrl": "https://stream.example/cs.m3u8",
                },
            ],
            "maxPage": 5,
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
                "icon": iconimage,
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

    lemoncams.List("__top__", page=1)

    assert len(added_links) == 2
    assert "model_sc" in added_links[0]["name"]
    assert "Stripchat" in added_links[0]["name"]
    assert added_links[0]["url"] == "https://www.lemoncams.com/stripchat/model_sc"

    assert "model_cs" in added_links[1]["name"]
    assert "CamSoda" in added_links[1]["name"]
    assert added_links[1]["url"] == "https://www.lemoncams.com/camsoda/model_cs|https://stream.example/cs.m3u8"

    assert len(added_dirs) == 1
    assert added_dirs[0]["page"] == 2


def test_playvid_plays_cached_stream_url_directly(monkeypatch):
    played = []

    class FakePlayer:
        def __init__(self, name, IA_check=None):
            self.progress = self

        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

        def play_from_direct_link(self, link):
            played.append(link)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakePlayer)

    lemoncams.Playvid(
        "https://www.lemoncams.com/camsoda/model_cs|https://stream.example/cs.m3u8",
        "Model CS",
    )

    assert len(played) == 1
    assert played[0].startswith("https://stream.example/cs.m3u8|")
    assert "User-Agent=" in played[0]


def test_playvid_resolves_stripchat_via_widget_api(monkeypatch):
    played = []

    def fake_get_html(url, *args, **kwargs):
        if "stripchat.com/api/external/v4/widget" in url:
            return json.dumps({
                "models": [
                    {
                        "username": "nicdani_1",
                        "stream": {
                            "urls": {
                                "480p": "https://edge-hls.example/nicdani_480p.m3u8",
                            }
                        }
                    }
                ]
            })
        return ""

    class FakePlayer:
        def __init__(self, name, IA_check=None):
            self.progress = self

        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

        def play_from_direct_link(self, link):
            played.append(link)

    monkeypatch.setattr(lemoncams.utils, "_getHtml", fake_get_html)
    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakePlayer)

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/nicdani_1", "nicdani_1")

    assert len(played) == 1
    assert "https://edge-hls.example/nicdani_480p.m3u8|" in played[0]


def test_playvid_notifies_offline_when_stream_not_found(monkeypatch):
    notifications = []

    class FakePlayer:
        def __init__(self, name, IA_check=None):
            self.progress = self

        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakePlayer)
    monkeypatch.setattr(lemoncams, "_resolve_stripchat_stream", lambda username: None)
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/offline_model", "offline_model")

    assert len(notifications) == 1
    assert "offline" in notifications[0][1].lower()


def test_search_adds_model_link(monkeypatch):
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

    lemoncams.Search("any", "camsoda:desirerodriguez")

    assert len(added_links) == 1
    assert "desirerodriguez" in added_links[0]["name"]
    assert added_links[0]["url"] == "https://www.lemoncams.com/camsoda/desirerodriguez"
    assert added_links[0]["mode"] == "Playvid"
