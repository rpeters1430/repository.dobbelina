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


def test_playvid_delegates_to_stripchat_with_cached_stream(monkeypatch):
    calls = []

    monkeypatch.setattr(
        lemoncams,
        "stripchat_playvid",
        lambda url, name: calls.append({"url": url, "name": name}),
    )

    # Test with piped URL
    url = "https://www.lemoncams.com/stripchat/model1|https://stream.example/model1.m3u8"
    lemoncams.Playvid(url, "Model 1")

    assert calls == [
        {"url": "https://stream.example/model1.m3u8", "name": "model1"}
    ]


def test_playvid_delegates_to_stripchat_without_cached_stream(monkeypatch):
    calls = []

    monkeypatch.setattr(
        lemoncams,
        "stripchat_playvid",
        lambda url, name: calls.append({"url": url, "name": name}),
    )

    # Test with URL without piped stream - LemonCams should not resolve a
    # stream itself; Stripchat's pipeline does its own model lookup.
    url = "https://www.lemoncams.com/stripchat/model1"
    lemoncams.Playvid(url, "Model 1")

    assert calls == [{"url": "", "name": "model1"}]


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
    calls = []

    monkeypatch.setattr(
        lemoncams,
        "stripchat_playvid",
        lambda url, name: calls.append({"url": url, "name": name}),
    )
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    lemoncams.Playvid("https://www.lemoncams.com/chaturbate/beckymadsons", "beckymadsons")

    assert notifications == [("LemonCams", "Only Stripchat models are supported")]
    assert calls == []
