"""Tests for xtheatre site implementation."""

from resources.lib.sites import xtheatre


def test_xtmain_and_xtsort(monkeypatch):
    dirs = []
    list_calls = []
    eod_calls = []
    settings_opened = []

    monkeypatch.setattr(xtheatre, "sortlistxt", ["date", "title", "views", "likes"])
    monkeypatch.setattr(xtheatre.addon, "getSetting", lambda key: "0")
    monkeypatch.setattr(
        xtheatre.addon, "openSettings", lambda: settings_opened.append(1), raising=False
    )
    monkeypatch.setattr(
        xtheatre.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, fanart=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(xtheatre, "XTList", lambda url, page=1: list_calls.append(url))
    monkeypatch.setattr(xtheatre.utils, "eod", lambda: eod_calls.append(1))

    xtheatre.XTMain()
    xtheatre.XTSort()

    assert len(dirs) >= 6
    assert any(d["mode"] == "XTCat" for d in dirs)
    assert any(d["mode"] == "XTSort" for d in dirs)
    assert settings_opened == [1]
    assert len(list_calls) == 2
    assert len(eod_calls) == 2


def test_xtcat_loops_pages_and_adds_dirs(monkeypatch):
    page1 = """
    <article><a href="https://pornxtheatre.com/cat-a/" title="Cat A"><img src="a.jpg"></a></article>
    <div class="pagination"><ul><li class="current"><a href="https://pornxtheatre.com/categories/page/2/"></a></li></ul></div>
    """
    page2 = """
    <article><a href="https://pornxtheatre.com/cat-b" title="Cat B"><img src="b.jpg"></a></article>
    <div class="pagination"><ul><li><a href="#"></a></li></ul></div>
    """
    dirs = []
    calls = {"n": 0}

    def _get_html(*_a, **_k):
        calls["n"] += 1
        return page1 if calls["n"] == 1 else page2

    monkeypatch.setattr(xtheatre.utils, "getHtml", _get_html)
    monkeypatch.setattr(xtheatre.utils, "eod", lambda: None)
    monkeypatch.setattr(
        xtheatre.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, page=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    xtheatre.XTCat("https://pornxtheatre.com/categories/")

    assert len(dirs) >= 1
    assert dirs[0]["url"].endswith("page/1/")


def test_xtsearch_and_xtlist_paths(monkeypatch):
    downloads = []
    dirs = []
    search_calls = []

    monkeypatch.setattr(xtheatre.addon, "getSetting", lambda key: "1")
    monkeypatch.setattr(
        xtheatre.site,
        "search_dir",
        lambda url, mode: search_calls.append((url, mode)),
    )
    monkeypatch.setattr(xtheatre.utils, "eod", lambda: None)
    monkeypatch.setattr(
        xtheatre.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(
        xtheatre.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, page=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    html_next = """
    <article href="https://pornxtheatre.com/v/1" title="Video One" src="https://img/1.jpg"></article>
    <a href="https://pornxtheatre.com/page/3/">Next</a>
    """
    html_fallback = """
    <article href="https://pornxtheatre.com/v/2" title="Video Two" src="https://img/2.jpg"></article>
    class="pagination"><ul><li class="current"><a href="https://pornxtheatre.com/page/9/"></a></li></ul>
    """
    calls = {"n": 0}

    def _get_html(*_a, **_k):
        calls["n"] += 1
        return html_next if calls["n"] == 1 else html_fallback

    monkeypatch.setattr(xtheatre.utils, "getHtml", _get_html)

    xtheatre.XTSearch("https://pornxtheatre.com/?s=")
    xtheatre.XTSearch("https://pornxtheatre.com/?s=", keyword="abc def")
    xtheatre.XTList("https://pornxtheatre.com/page/1/")

    assert search_calls == [("https://pornxtheatre.com/?s=", "XTSearch")]
    assert len(downloads) == 2
    assert any(d["name"] == "Next Page ..." for d in dirs)


def test_xtvideo_direct_and_fallback(monkeypatch):
    direct_calls = []
    fallback_calls = []

    class _Player:
        def __init__(self, *_a, **_k):
            pass

        def play_from_direct_link(self, url):
            direct_calls.append(url)

        def play_from_site_link(self, url, referer):
            fallback_calls.append((url, referer))

    monkeypatch.setattr(xtheatre.utils, "VideoPlayer", _Player)

    monkeypatch.setattr(
        xtheatre.utils,
        "getHtml",
        lambda url, *a, **k: (
            '<div class="player"><iframe src="https://streamup.example/embed/abc"></iframe></div>'
            if "watch/ok" in url
            else (
                'streaming_url:"https://cdn.example/hls.m3u8"'
                if "streamup" in url
                else ""
            )
        ),
    )
    xtheatre.XTVideo("https://pornxtheatre.com/watch/ok", "Name")

    monkeypatch.setattr(
        xtheatre.utils,
        "getHtml",
        lambda *_a,
        **_k: '<div class="player"><iframe src="https://other.example/embed/xyz"></iframe></div>',
    )
    xtheatre.XTVideo("https://pornxtheatre.com/watch/fallback", "Name")

    assert direct_calls and "referer=https://streamup.example/" in direct_calls[0]
    assert fallback_calls == [
        (
            "https://pornxtheatre.com/watch/fallback",
            "https://pornxtheatre.com/watch/fallback",
        )
    ]


def test_get_xt_sort_method(monkeypatch):
    monkeypatch.setattr(xtheatre.addon, "getSetting", lambda key: "3")
    assert xtheatre.getXTSortMethod() == "likes"
