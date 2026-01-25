"""Tests for pornhits site module"""

from resources.lib.sites import pornhits
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
                "mode": pornhits.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": pornhits.site.get_full_mode(mode),
            }
        )


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch,
        pornhits,
        {"videos.php?p=1": "sites/pornhits/listing.html"},
    )
    monkeypatch.setattr(pornhits.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(pornhits.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(pornhits.utils, "eod", lambda *args, **kwargs: None)

    pornhits.List("https://www.pornhits.com/videos.php?p=1&s=l")

    assert recorder.downloads == [
        {
            "name": "First Video",
            "url": "https://www.pornhits.com/video/first",
            "mode": "pornhits.Playvid",
            "icon": "https://cdn.pornhits.com/thumb1.jpg",
            "duration": "10:11",
        },
        {
            "name": "Second Video",
            "url": "https://www.pornhits.com/video/second",
            "mode": "pornhits.Playvid",
            "icon": "https://cdn.pornhits.com/thumb2.jpg",
            "duration": "02:03",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "Next Page (2/4)",
            "url": "https://www.pornhits.com/videos.php?p=2&s=l",
            "mode": "pornhits.List",
        }
    ]


def test_categories_parses_entries(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, pornhits, {"categories.php": "sites/pornhits/categories.html"}
    )
    monkeypatch.setattr(pornhits.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(pornhits.utils, "eod", lambda *args, **kwargs: None)

    pornhits.Categories("https://www.pornhits.com/categories.php")

    assert recorder.dirs == [
        {
            "name": "First",
            "url": "https://www.pornhits.com/category/first",
            "mode": "pornhits.List",
        },
        {
            "name": "Second",
            "url": "/category/second",
            "mode": "pornhits.List",
        },
    ]


def test_search_without_keyword(monkeypatch):
    called = {}

    def _search_dir(url, mode):
        called["url"] = url
        called["mode"] = mode

    monkeypatch.setattr(pornhits.site, "search_dir", _search_dir)

    pornhits.Search("https://www.pornhits.com/videos.php?p=1&q=")

    assert called["url"] == "https://www.pornhits.com/videos.php?p=1&q="
    assert called["mode"] == "Search"
