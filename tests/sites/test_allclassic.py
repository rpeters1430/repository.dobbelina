"""Tests for allclassic site implementation."""

from resources.lib.sites import allclassic


def test_main_adds_nav_and_calls_list(monkeypatch):
    dirs = []
    list_calls = []
    eod_calls = []

    monkeypatch.setattr(
        allclassic.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(allclassic, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(allclassic.utils, "eod", lambda: eod_calls.append(1))

    allclassic.Main()

    assert len(dirs) == 2
    assert dirs[0]["mode"] == "Categories"
    assert dirs[1]["mode"] == "Search"
    assert list_calls == [allclassic.site.url + "page/1/"]
    assert eod_calls == [1]


def test_list_success_and_no_videos_and_exception(monkeypatch):
    download_calls = []
    next_calls = []
    notify_calls = []

    monkeypatch.setattr(
        allclassic.utils,
        "next_page",
        lambda *a, **k: next_calls.append({"args": a, "kwargs": k}),
    )
    monkeypatch.setattr(
        allclassic.site,
        "add_download_link",
        lambda *a, **k: download_calls.append({"args": a, "kwargs": k}),
    )
    monkeypatch.setattr(allclassic.utils, "eod", lambda: None)
    monkeypatch.setattr(
        allclassic.utils, "notify", lambda msg=None, **kwargs: notify_calls.append(msg)
    )

    monkeypatch.setattr(
        allclassic.utils,
        "getHtml",
        lambda *a, **k: (
            '<a class="th item" href="https://allclassic.porn/v/1">'
            '<img src="https://img/1.jpg" alt="A"><span class="th-description">Title 1</span>'
            '<span><i class="la-clock-o"></i>12:34</span></a>'
        ),
    )
    allclassic.List("https://allclassic.porn/page/1/")
    assert len(download_calls) == 1
    assert len(next_calls) == 1

    monkeypatch.setattr(
        allclassic.utils, "getHtml", lambda *a, **k: "No videos found here"
    )
    allclassic.List("https://allclassic.porn/page/2/")

    monkeypatch.setattr(
        allclassic.utils,
        "getHtml",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    allclassic.List("https://allclassic.porn/page/3/")

    assert notify_calls == ["No videos found!", "No videos found!"]


def test_gotopage_valid_and_out_of_range(monkeypatch):
    builtins = []
    notify_calls = []

    class _Dialog:
        def __init__(self, value):
            self._value = value

        def numeric(self, *_a, **_k):
            return self._value

    monkeypatch.setattr(allclassic.utils, "notify", lambda msg=None: notify_calls.append(msg))
    monkeypatch.setattr(allclassic.xbmc, "executebuiltin", lambda cmd: builtins.append(cmd))
    monkeypatch.setattr(allclassic.xbmcgui, "Dialog", lambda: _Dialog("2"))
    allclassic.GotoPage("https://allclassic.porn/page/1/", "1", "5")

    monkeypatch.setattr(allclassic.xbmcgui, "Dialog", lambda: _Dialog("8"))
    allclassic.GotoPage("https://allclassic.porn/page/1/", "1", "5")

    assert builtins and builtins[0].startswith("Container.Update(")
    assert notify_calls == ["Out of range!"]


def test_playvid_quality_paths(monkeypatch):
    played = []

    class _Progress:
        def update(self, *_a, **_k):
            return None

    class _Player:
        def __init__(self, *_a, **_k):
            self.progress = _Progress()

        def play_from_direct_link(self, url):
            played.append(url)

    page = """
    flashvars = {
      license_code: "LIC123",
      video_url_text: "MAX",
      video_url: "function/0/encrypted",
      video_alt_url_text: "1080p",
      video_alt_url: "https://cdn/1080.mp4",
      video_alt_url2: "https://cdn/480.mp4"
    };
    """

    monkeypatch.setattr(allclassic.utils, "VideoPlayer", _Player)
    monkeypatch.setattr(allclassic.utils, "getHtml", lambda *a, **k: page)
    monkeypatch.setattr(allclassic.utils, "prefquality", lambda *a, **k: "function/0/encrypted")
    monkeypatch.setattr(allclassic, "kvs_decode", lambda url, license: "https://decoded/video.mp4")

    allclassic.Playvid("https://allclassic.porn/watch/1", "Name")

    monkeypatch.setattr(
        allclassic.utils,
        "prefquality",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("selector path")),
    )
    monkeypatch.setattr(
        allclassic.utils, "selector", lambda *_a, **_k: "https://cdn/fallback.mp4"
    )
    allclassic.Playvid("https://allclassic.porn/watch/2", "Name")

    assert played[0] == "https://decoded/video.mp4|Referer=https://allclassic.porn/watch/1"
    assert played[1] == "https://cdn/fallback.mp4|Referer=https://allclassic.porn/watch/2"


def test_search_categories_lookup_related(monkeypatch):
    list_calls = []
    search_calls = []
    dirs = []
    builtins = []
    lookup_calls = []

    monkeypatch.setattr(allclassic, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(
        allclassic.site, "search_dir", lambda url, mode: search_calls.append((url, mode))
    )
    monkeypatch.setattr(
        allclassic.utils,
        "getHtml",
        lambda *_a, **_k: (
            '<a class="th" href="https://allclassic.porn/cat/a/">'
            '<img src="a.jpg" alt="Alpha"></a>'
        ),
    )
    monkeypatch.setattr(allclassic.utils, "eod", lambda: None)
    monkeypatch.setattr(
        allclassic.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(allclassic.xbmc, "executebuiltin", lambda cmd: builtins.append(cmd))

    class _LookupInfo:
        def __init__(self, site_url, url, mode, lookup_list):
            lookup_calls.append((site_url, url, mode, lookup_list))

        def getinfo(self):
            lookup_calls.append("getinfo")

    monkeypatch.setattr(allclassic.utils, "LookupInfo", _LookupInfo)

    allclassic.Search("https://allclassic.porn/search/{0}/")
    allclassic.Search("https://allclassic.porn/search/{0}/", keyword="abc def")
    allclassic.Categories("https://allclassic.porn/categories/")
    allclassic.Lookupinfo("https://allclassic.porn/watch/xyz")
    allclassic.Related("https://allclassic.porn/tags/retro/")

    assert search_calls == [("https://allclassic.porn/search/{0}/", "Search")]
    assert list_calls == ["https://allclassic.porn/search/abc-def/"]
    assert dirs and dirs[0]["name"] == "Alpha"
    assert lookup_calls and lookup_calls[-1] == "getinfo"
    assert builtins and builtins[0].startswith("Container.Update(")
