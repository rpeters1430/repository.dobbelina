"""Tests for justfullporn site module"""

from resources.lib.sites import justfullporn
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
                "mode": justfullporn.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": justfullporn.site.get_full_mode(mode),
            }
        )


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch,
        justfullporn,
        {"justfullporn.net/": "sites/justfullporn/listing.html"},
    )
    monkeypatch.setattr(justfullporn.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(justfullporn.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(justfullporn.utils, "eod", lambda *args, **kwargs: None)

    justfullporn.List("https://justfullporn.net/")

    assert recorder.downloads == [
        {
            "name": "First Video",
            "url": "https://justfullporn.net/video/first",
            "mode": "justfullporn.Playvid",
            "icon": "https://cdn.justfullporn.net/thumb1.jpg",
        },
        {
            "name": "Second Video",
            "url": "https://justfullporn.net/video/second",
            "mode": "justfullporn.Playvid",
            "icon": "https://cdn.justfullporn.net/thumb2.jpg",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "Next Page (2/4)",
            "url": "https://justfullporn.net/page/2/",
            "mode": "justfullporn.List",
        }
    ]


def test_categories_parses_entries(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, justfullporn, {"categories/": "sites/justfullporn/categories.html"}
    )
    monkeypatch.setattr(justfullporn.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(justfullporn.utils, "eod", lambda *args, **kwargs: None)

    justfullporn.Categories("https://justfullporn.net/categories/")

    assert recorder.dirs == [
        {
            "name": "First Category [COLOR blue]12 Videos[/COLOR]",
            "url": "https://justfullporn.net/category/first",
            "mode": "justfullporn.List",
        },
        {
            "name": "Second Category [COLOR blue]5 Videos[/COLOR]",
            "url": "https://justfullporn.net/category/second",
            "mode": "justfullporn.List",
        },
        {
            "name": "Next Page (2)",
            "url": "https://justfullporn.net/categories/page/2/",
            "mode": "justfullporn.Categories",
        },
    ]


def test_tags_parses_entries(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, justfullporn, {"tags/": "sites/justfullporn/tags.html"}
    )
    monkeypatch.setattr(justfullporn.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(justfullporn.utils, "eod", lambda *args, **kwargs: None)

    justfullporn.Tags("https://justfullporn.net/tags/")

    assert recorder.dirs == [
        {
            "name": "First Tag",
            "url": "https://justfullporn.net/tag/first",
            "mode": "justfullporn.List",
        },
        {
            "name": "Second Tag",
            "url": "/tag/second",
            "mode": "justfullporn.List",
        },
    ]


def test_search_without_keyword(monkeypatch):
    called = {}

    def _search_dir(url, mode):
        called["url"] = url
        called["mode"] = mode

    monkeypatch.setattr(justfullporn.site, "search_dir", _search_dir)

    justfullporn.Search("https://justfullporn.net/?s=")

    assert called["url"] == "https://justfullporn.net/?s="
    assert called["mode"] == "Search"
