from resources.lib.sites import youcrazyx
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
                "mode": youcrazyx.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": youcrazyx.site.get_full_mode(mode),
            }
        )


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, youcrazyx, {"most-recent/": "sites/youcrazyx/listing.html"}
    )
    monkeypatch.setattr(youcrazyx.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(youcrazyx.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(youcrazyx.utils, "eod", lambda *args, **kwargs: None)

    youcrazyx.List("https://www.youcrazyx.com/most-recent/")

    assert recorder.downloads == [
        {
            "name": "First Video",
            "url": "https://www.youcrazyx.com/video/first",
            "mode": "youcrazyx.Playvid",
            "icon": "https://cdn.youcrazyx.com/thumb-first.jpg",
            "duration": "12:34",
            "quality": "HD",
        },
        {
            "name": "Second Video",
            "url": "https://www.youcrazyx.com/video/second",
            "mode": "youcrazyx.Playvid",
            "icon": "https://cdn.youcrazyx.com/thumb-second.jpg",
            "duration": "05:00",
            "quality": "",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "Next Page (2)",
            "url": "https://www.youcrazyx.com/most-recent/page2.html",
            "mode": "youcrazyx.List",
        }
    ]


def test_categories_parses_links(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, youcrazyx, {"channels/": "sites/youcrazyx/categories.html"}
    )
    monkeypatch.setattr(youcrazyx.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(youcrazyx.utils, "eod", lambda *args, **kwargs: None)

    youcrazyx.Categories("https://www.youcrazyx.com/channels/")

    assert recorder.dirs == [
        {
            "name": "Category One",
            "url": "https://www.youcrazyx.com/channel/one/",
            "mode": "youcrazyx.List",
        },
        {
            "name": "Category Two",
            "url": "https://www.youcrazyx.com/channel/two/",
            "mode": "youcrazyx.List",
        },
    ]
