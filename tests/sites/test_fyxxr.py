"""Tests for fyxxr.to site implementation."""

import pytest
from resources.lib.sites import fyxxr


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": fyxxr.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        )

    def add_dir(self, name, url, mode, iconimage=None, desc="", **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": fyxxr.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )


def test_main_adds_nav_and_calls_list(monkeypatch):
    recorder = _Recorder()
    list_calls = []

    monkeypatch.setattr(fyxxr.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(fyxxr, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(fyxxr.utils, "eod", lambda: None)

    fyxxr.Main()

    assert len(recorder.dirs) == 2
    assert recorder.dirs[0]["name"] == "[COLOR hotpink]Models[/COLOR]"
    assert recorder.dirs[1]["name"] == "[COLOR hotpink]Search[/COLOR]"
    assert list_calls == [fyxxr.site.url + "latest-updates/"]


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()
    html = """
    <div class="item">
        <a href="/v1/" title="Video 1">
            <img data-original="1.jpg">
        </a>
        <div class="duration">10:00</div>
        <div class="is-hd">HD</div>
    </div>
    <div class="next" data-block-id="block1" data-parameters="from:1;sort:mr">Next</div>
    """

    monkeypatch.setattr(fyxxr.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(fyxxr.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(fyxxr.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(fyxxr.utils, "eod", lambda: None)
    monkeypatch.setattr(fyxxr, "randint", lambda a, b: 123)

    fyxxr.List("https://fyxxr.to/latest-updates/")

    assert len(recorder.downloads) == 1
    assert recorder.downloads[0]["name"] == "Video 1"
    assert recorder.downloads[0]["duration"] == "10:00"
    assert recorder.downloads[0]["quality"] == "HD"

    assert len(recorder.dirs) == 1
    assert "Next Page" in recorder.dirs[0]["name"]
    assert "block_id=block1" in recorder.dirs[0]["url"]
    assert "from=2" in recorder.dirs[0]["url"]


def test_search_calls_list(monkeypatch):
    list_calls = []
    monkeypatch.setattr(fyxxr, "List", lambda url: list_calls.append(url))

    fyxxr.Search("https://fyxxr.to/search/", keyword="test query")

    assert list_calls == ["https://fyxxr.to/search/test-query/"]


def test_categories_parses_models(monkeypatch):
    recorder = _Recorder()
    html = """
    <a class="item" href="/m1/" title="Model 1">
        <span class="videos">100</span>
    </a>
    <div class="page-current"><span>1</span></div>
    <a class="next" data-block-id="block2" data-parameters="from:1">Next</a>
    """

    monkeypatch.setattr(fyxxr.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(fyxxr.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(fyxxr.utils, "eod", lambda: None)
    monkeypatch.setattr(fyxxr, "randint", lambda a, b: 123)

    fyxxr.Categories("https://fyxxr.to/models/")

    assert len(recorder.dirs) == 2
    assert "Model 1" in recorder.dirs[0]["name"]
    assert "100" in recorder.dirs[0]["name"]
    assert recorder.dirs[0]["mode"] == "fyxxr.List"

    assert "Next Page" in recorder.dirs[1]["name"]
    assert recorder.dirs[1]["mode"] == "fyxxr.Categories"
