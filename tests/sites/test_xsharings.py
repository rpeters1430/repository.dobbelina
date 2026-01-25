from resources.lib.sites import xsharings
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
                "mode": xsharings.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": xsharings.site.get_full_mode(mode),
            }
        )


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, xsharings, {"page/1": "sites/xsharings/listing.html"}
    )
    monkeypatch.setattr(xsharings.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(xsharings.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xsharings.utils, "eod", lambda *args, **kwargs: None)

    xsharings.List("https://xsharings.com/page/1?filter=latest")

    assert recorder.downloads == [
        {
            "name": "First Video",
            "url": "https://xsharings.com/video/first",
            "mode": "xsharings.Play",
            "icon": "https://cdn.xsharings.com/thumb-first.jpg",
            "duration": "10:11",
        },
        {
            "name": "Second Video",
            "url": "https://xsharings.com/video/second",
            "mode": "xsharings.Play",
            "icon": "https://cdn.xsharings.com/thumb-second.jpg",
            "duration": "02:03",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "Next Page (2/5)",
            "url": "https://xsharings.com/page/2/",
            "mode": "xsharings.List",
        }
    ]


def test_categories_parses_entries(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, xsharings, {"categories/": "sites/xsharings/categories.html"}
    )
    monkeypatch.setattr(xsharings.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xsharings.utils, "eod", lambda *args, **kwargs: None)

    xsharings.Categories("https://xsharings.com/categories/")

    assert recorder.dirs == [
        {
            "name": "First Category",
            "url": "https://xsharings.com/category/first",
            "mode": "xsharings.List",
        },
        {
            "name": "Second Category",
            "url": "https://xsharings.com/category/second",
            "mode": "xsharings.List",
        },
        {
            "name": "Next Page",
            "url": "https://xsharings.com/categories/page/2/",
            "mode": "xsharings.Categories",
        },
    ]
