"""Tests for watcherotic site module"""

from resources.lib.sites import watcherotic
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
                "mode": watcherotic.site.get_full_mode(mode),
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
                "mode": watcherotic.site.get_full_mode(mode),
            }
        )


class _Thumbs:
    def __init__(self, *_args, **_kwargs):
        pass

    def fix_img(self, img):
        return img


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, watcherotic, {"latest-updates/": "sites/watcherotic/listing.html"}
    )
    monkeypatch.setattr(watcherotic.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(watcherotic.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(watcherotic.utils, "eod", lambda *args, **kwargs: None)
    monkeypatch.setattr(watcherotic.utils, "Thumbnails", _Thumbs)
    monkeypatch.setattr(watcherotic.time, "time", lambda: 1700000000.0)

    watcherotic.List("https://watcherotic.com/latest-updates/")

    assert recorder.downloads == [
        {
            "name": "First Video",
            "url": "https://watcherotic.com/video/first",
            "mode": "watcherotic.Play",
            "icon": "https://cdn.watcherotic.com/thumb-first.jpg",
            "duration": "12:34",
            "quality": "HD",
        },
        {
            "name": "Second Video",
            "url": "https://watcherotic.com/video/second",
            "mode": "watcherotic.Play",
            "icon": "https://cdn.watcherotic.com/thumb-second.jpg",
            "duration": "05:06",
            "quality": "",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "[COLOR hotpink]Next Page...[/COLOR] (2)",
            "url": (
                "https://watcherotic.com/latest-updates/"
                "?mode=async&function=get_block&block_id=block123"
                "&from=2&sort_by=post_date&from_albums=2&_="
                "1700000000000"
            ),
            "mode": "watcherotic.List",
        }
    ]


def test_cat_parses_tag_cloud(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, watcherotic, {"tags/": "sites/watcherotic/categories.html"}
    )
    monkeypatch.setattr(watcherotic.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(watcherotic.utils, "eod", lambda *args, **kwargs: None)

    watcherotic.Cat("https://watcherotic.com/tags/")

    assert recorder.dirs == [
        {
            "name": "Tag One",
            "url": "https://watcherotic.com/tags/tag-one/",
            "mode": "watcherotic.List",
        },
        {
            "name": "Tag Two",
            "url": "/tags/tag-two/",
            "mode": "watcherotic.List",
        },
    ]


def test_search_without_keyword(monkeypatch):
    called = {}

    def _search_dir(url, mode):
        called["url"] = url
        called["mode"] = mode

    monkeypatch.setattr(watcherotic.site, "search_dir", _search_dir)

    watcherotic.Search("https://watcherotic.com/search/")

    assert called["url"] == "https://watcherotic.com/search/"
    assert called["mode"] == "Search"
