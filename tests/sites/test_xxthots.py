"""Tests for xxthots.com site implementation."""

from resources.lib.sites import xxthots


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": xxthots.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, iconimage=None, desc="", **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": xxthots.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )


def test_main_adds_nav_and_calls_list(monkeypatch):
    recorder = _Recorder()
    list_calls = []

    monkeypatch.setattr(xxthots.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xxthots, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(xxthots.utils, "eod", lambda: None)

    xxthots.Main()

    assert len(recorder.dirs) == 1
    assert recorder.dirs[0]["name"] == "[COLOR hotpink]Search[/COLOR]"
    assert list_calls == [xxthots.site.url + "latest-updates/"]


def test_list_parses_videos_and_pagination(monkeypatch):
    recorder = _Recorder()
    # Dummy HTML that matches the regex in xxthots.List and utils.videos_list
    html = """
    <div class="thumb thumb_rel">
        <a href="/v1/" title="Video 1">
            <img data-original="1.jpg">
            <span class="time">10:00</span>
            <span class="quality">HD</span>
        </a>
    </div>
    <div class="pagination">
        <a href="#">9</a> <a class='next' rel="next" data-block-id="block1" data-parameters="from:2">Next</a>
    </div>
    """

    monkeypatch.setattr(xxthots.utils, "getHtml", lambda *a, **k: html)
    # We need to mock videos_list because it's hard to satisfy with dummy HTML
    def fake_videos_list(site, mode, html, *args, **kwargs):
        xxthots.site.add_download_link("Video 1", "/v1/", mode, "1.jpg")

    monkeypatch.setattr(xxthots.utils, "videos_list", fake_videos_list)
    monkeypatch.setattr(xxthots.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(xxthots.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xxthots.utils, "eod", lambda: None)
    monkeypatch.setattr(xxthots.time, "time", lambda: 1234.567)

    xxthots.List("https://xxthots.com/latest-updates/")

    assert len(recorder.downloads) == 1
    assert recorder.downloads[0]["name"] == "Video 1"

    assert len(recorder.dirs) == 1
    assert "Next Page" in recorder.dirs[0]["name"]
    assert "block_id=block1" in recorder.dirs[0]["url"]
    assert "from=2" in recorder.dirs[0]["url"]


def test_search_calls_list(monkeypatch):
    list_calls = []
    monkeypatch.setattr(xxthots, "List", lambda url: list_calls.append(url))

    xxthots.Search("https://xxthots.com/search/{0}/", keyword="test query")

    assert list_calls == ["https://xxthots.com/search/test-query/"]


def test_related_updates_container(monkeypatch):
    builtins = []
    monkeypatch.setattr(xxthots.xbmc, "executebuiltin", lambda cmd: builtins.append(cmd))

    xxthots.Related("https://xxthots.com/v1/")

    assert len(builtins) == 1
    assert "Container.Update" in builtins[0]
    assert "xxthots.List" in builtins[0]
