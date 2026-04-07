import json
from resources.lib.sites import chaturbate
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", *args, **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": chaturbate.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": chaturbate.site.get_full_mode(mode),
            }
        )


def test_list_populates_cams(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, chaturbate, {"room-list": "sites/chaturbate/list.json"}
    )
    monkeypatch.setattr(chaturbate.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(chaturbate.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(chaturbate.utils, "eod", lambda *args, **kwargs: None)

    chaturbate.List(
        "https://chaturbate.com/api/ts/roomlist/room-list/?limit=10&offset=0"
    )

    assert len(recorder.downloads) > 0
    # Check that first item is from the JSON
    with open("tests/fixtures/sites/chaturbate/list.json", "r") as f:
        data = json.load(f)
        first_room = data["rooms"][0]
        assert recorder.downloads[0]["name"].startswith(first_room["username"])


def test_playvid_uses_room_referer_and_inputstream_adaptive(monkeypatch):
    room_data = {
        "hls_source": "https://edge.example.com/live/master.m3u8",
        "broadcaster_username": "model1",
        "viewer_username": "viewer1",
        "room_pass": "pass1",
        "edge_auth": "auth1",
    }
    escaped = json.dumps(room_data).replace("\\", "\\\\").replace('"', '\\"')
    html = '<script>initialRoomDossier = "{}"</script>'.format(escaped)

    play_calls = []

    class FakeVideoPlayer:
        def __init__(self, name):
            self.name = name
            self.IA_check = None
            play_calls.append({"name": name, "ia_check": None, "url": None, "player": self})

        def play_from_direct_link(self, url):
            play_calls[-1]["url"] = url
            play_calls[-1]["ia_check"] = self.IA_check

    monkeypatch.setattr(chaturbate.addon, "getSetting", lambda key: "0" if key == "chatplay" else "")
    monkeypatch.setattr(
        chaturbate.utils,
        "get_html_with_cloudflare_retry",
        lambda *args, **kwargs: (html, False),
    )
    monkeypatch.setattr(chaturbate.utils, "VideoPlayer", FakeVideoPlayer)

    room_url = "https://chaturbate.com/model1/"
    chaturbate.Playvid(room_url, "Model 1")

    assert len(play_calls) == 1
    assert play_calls[0]["ia_check"] == "IA"
    assert "master.m3u8" in play_calls[0]["url"]
    assert "Referer=https%3A%2F%2Fchaturbate.com%2Fmodel1%2F" in play_calls[0]["url"]


def test_playvid_handles_missing_hls_source(monkeypatch):
    room_data = {"broadcaster_username": "model1"}
    escaped = json.dumps(room_data).replace("\\", "\\\\").replace('"', '\\"')
    html = '<script>initialRoomDossier = "{}"</script>'.format(escaped)

    notifications = []
    play_calls = []

    class FakeVideoPlayer:
        def __init__(self, name):
            pass

        def play_from_direct_link(self, url):
            play_calls.append(url)

    monkeypatch.setattr(chaturbate.addon, "getSetting", lambda key: "0" if key == "chatplay" else "")
    monkeypatch.setattr(
        chaturbate.utils,
        "get_html_with_cloudflare_retry",
        lambda *args, **kwargs: (html, False),
    )
    monkeypatch.setattr(chaturbate.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(
        chaturbate.utils,
        "notify",
        lambda header, msg, *args, **kwargs: notifications.append((header, msg)),
    )

    chaturbate.Playvid("https://chaturbate.com/model1/", "Model 1")

    assert play_calls == []
    assert notifications == [("Oh oh", "Couldn't find a playable webcam link")]
