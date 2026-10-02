"""Comprehensive tests for LemonCams scraper and multi-provider stream resolution."""

import pytest

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
                    "imageUrl": "https://img.doppiocdn.com/thumbs/1790816100/200459374",
                    "embedUrl": "https://creative.example/widgets/Player/lib.js?userId=abc",
                },
                {
                    "username": "model_cb",
                    "provider": "chaturbate",
                    "title": "Not playable here",
                    "numberOfUsers": 900,
                    "imageUrl": "https://img.example/cb.jpg",
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
    assert added_links[0]["url"] == (
        "https://www.lemoncams.com/stripchat/model_sc"
        "|https://edge-hls.doppiocdn.media/hls/200459374/master/200459374_auto.m3u8"
    )
    # unsupported providers (chaturbate) are left out
    assert not any("model_cb" in link["name"] for link in added_links)

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


def test_playvid_delegates_stripchat_to_stripchat_module(monkeypatch):
    from resources.lib.sites import stripchat

    calls = []

    def fake_play_stripchat_model(url, name):
        calls.append((url, name))

    monkeypatch.setattr(stripchat, "_play_stripchat_model", fake_play_stripchat_model)
    monkeypatch.setattr(lemoncams, "_api_get", lambda params: {"cams": []})

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/nicdani_1", "nicdani_1")

    assert calls == [("nicdani_1", "nicdani_1")]


def test_playvid_resolves_stripchat_stream_through_lemoncams_query(monkeypatch):
    from resources.lib.sites import stripchat

    calls = []
    queries = []

    def fake_api_get(params):
        queries.append(params.get("query"))
        return {
            "cams": [
                {"username": "other", "provider": "stripchat",
                 "imageUrl": "https://img.doppiocdn.com/thumbs/1/999"},
                {"username": "Nicdani_1", "provider": "stripchat",
                 "imageUrl": "https://img.doppiocdn.com/thumbs/1790816100/4242"},
            ]
        }

    monkeypatch.setattr(stripchat, "_play_stripchat_model", lambda url, name: calls.append((url, name)))
    monkeypatch.setattr(lemoncams, "_api_get", fake_api_get)

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/nicdani_1", "nicdani_1")

    assert queries == ["nicdani_1"]
    assert calls == [("https://edge-hls.doppiocdn.media/hls/4242/master/4242_auto.m3u8", "nicdani_1")]


def test_playvid_delegates_stripchat_with_cached_stream_url(monkeypatch):
    from resources.lib.sites import stripchat

    calls = []

    def fake_play_stripchat_model(url, name):
        calls.append((url, name))

    monkeypatch.setattr(stripchat, "_play_stripchat_model", fake_play_stripchat_model)

    lemoncams.Playvid(
        "https://www.lemoncams.com/stripchat/nicdani_1|https://edge-hls.example/nicdani.m3u8",
        "nicdani_1",
    )

    assert calls == [("https://edge-hls.example/nicdani.m3u8", "nicdani_1")]


@pytest.mark.parametrize(
    "keyword",
    ["desirerodriguez", "camsoda:desirerodriguez", "https://www.lemoncams.com/camsoda/desirerodriguez"],
)
def test_search_lists_api_results_for_model(monkeypatch, keyword):
    list_calls = []
    monkeypatch.setattr(lemoncams, "List", lambda url, page: list_calls.append((url, page)))

    lemoncams.Search("any", keyword)

    assert list_calls == [("query=desirerodriguez", 1)]


def test_search_without_keyword_opens_search_dir(monkeypatch):
    calls = []
    monkeypatch.setattr(lemoncams.site, "search_dir", lambda url, mode: calls.append((url, mode)))

    lemoncams.Search("any")

    assert calls == [("any", "Search")]


def test_query_target_is_sent_to_api(monkeypatch):
    seen = []
    monkeypatch.setattr(lemoncams, "_api_get", lambda params: seen.append(params) or {"cams": []})

    lemoncams._fetch_provider_payload("query=blonde", 2)

    assert seen[0]["query"] == "blonde"
    assert seen[0]["page"] == "2"
    assert "provider" not in seen[0]
