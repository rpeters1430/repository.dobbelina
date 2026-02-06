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
