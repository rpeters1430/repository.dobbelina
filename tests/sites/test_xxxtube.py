from resources.lib.sites import xxxtube
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": xxxtube.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": xxxtube.site.get_full_mode(mode),
            }
        )


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, xxxtube, {"videos/": "sites/xxxtube/listing.html"}
    )
    monkeypatch.setattr(xxxtube.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(xxxtube.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xxxtube.utils, "eod", lambda *args, **kwargs: None)

    xxxtube.List("https://x-x-x.tube/videos/?by=post_date")

    assert recorder.downloads == [
        {
            "name": "First Video",
            "url": "https://x-x-x.tube/video/first",
            "mode": "xxxtube.Playvid",
            "icon": "https://cdn.xxxtube.com/thumb-first.jpg",
            "duration": "12:34",
        },
        {
            "name": "Second Video",
            "url": "https://x-x-x.tube/video/second",
            "mode": "xxxtube.Playvid",
            "icon": "https://cdn.xxxtube.com/thumb-second.jpg",
            "duration": "05:06",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "Next Page (2/5)",
            "url": "https://x-x-x.tube/videos/2/",
            "mode": "xxxtube.List",
        }
    ]
