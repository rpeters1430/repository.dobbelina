"""Tests for pornez site implementation."""

from resources.lib.sites import pornez


def test_main_adds_nav_and_calls_list(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(
        pornez.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornez, "List", lambda url: list_calls.append(url))

    pornez.Main()

    assert len(dirs) == 2
    assert dirs[0]["mode"] == "Cat"
    assert dirs[1]["mode"] == "Search"
    assert list_calls == [pornez.site.url]


def test_list_parses_items_skips_livecams_and_adds_next(monkeypatch):
    html = """
    <div data-post-id="111">
      <img data-src="https://img/1.jpg" />
      <a href="https://pornezoo.net/v/1" title="First title"></a>
      <span class="duration">11:11</span>
    </div>
    <div data-post-id="222">
      <img data-src="https://img/2.jpg" />
      <a href="https://pornezoo.net/v/2" title="Live Cams"></a>
      <span class="duration">00:00</span>
    </div>
    <a href="https://pornezoo.net/page/3/">&raquo;</a>
    <a class="page-link" href="https://pornezoo.net/page/9/">9</a>
    """
    downloads = []
    dirs = []

    monkeypatch.setattr(pornez.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornez.utils, "eod", lambda: None)
    monkeypatch.setattr(
        pornez.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(
        pornez.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    pornez.List("https://pornezoo.net")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "First title"
    assert downloads[0]["duration"] == "11:11"
    assert dirs and "(3/9)" in dirs[0]["name"]


def test_cat_search_and_context_related(monkeypatch):
    cat_html = """
    <a class="btn btn-grey" href="https://pornezoo.net/c/a/">Alpha</a>
    <a class="btn btn-grey" href="https://pornezoo.net/c/b/">Beta</a>
    <a class="btn btn-grey" href="https://pornezoo.net/c/last/">Last</a>
    """
    dirs = []
    list_calls = []
    search_calls = []
    builtins = []

    monkeypatch.setattr(pornez.utils, "getHtml", lambda *a, **k: cat_html)
    monkeypatch.setattr(pornez.utils, "eod", lambda: None)
    monkeypatch.setattr(
        pornez.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornez, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(
        pornez.site, "search_dir", lambda url, mode: search_calls.append((url, mode))
    )
    monkeypatch.setattr(pornez.xbmc, "executebuiltin", lambda x: builtins.append(x))

    pornez.Cat("https://pornezoo.net")
    pornez.Search("https://pornezoo.net/?s=")
    pornez.Search("https://pornezoo.net/?s=", keyword="abc def")
    pornez.ContextRelated("https://pornezoo.net/related/list")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Alpha"
    assert search_calls == [("https://pornezoo.net/?s=", "Search")]
    assert list_calls == ["https://pornezoo.net/?s=abc%20def"]
    assert builtins and builtins[0].startswith("Container.Update(")


def test_play_resolve_and_direct_paths(monkeypatch):
    play_resolve = []
    play_direct = []

    class _Resolver:
        def __init__(self, should_resolve):
            self._should_resolve = should_resolve

        def HostedMediaFile(self, _url):
            return self._should_resolve

    class _Player:
        def __init__(self, *_args, **_kwargs):
            self.resolveurl = _Resolver(True)

        def play_from_link_to_resolve(self, url):
            play_resolve.append(url)

        def play_from_direct_link(self, url):
            play_direct.append(url)

    class _PlayerNoResolve(_Player):
        def __init__(self, *_args, **_kwargs):
            self.resolveurl = _Resolver(False)

    monkeypatch.setattr(
        pornez.utils,
        "getHtml",
        lambda url, *a, **k: (
            '<iframe src="https://embed/player"></iframe>'
            if "watch" in url
            else '<source src="https://cdn/video.mp4">'
        ),
    )
    monkeypatch.setattr(pornez.utils, "VideoPlayer", _Player)
    pornez.Play("https://pornezoo.net/watch/1", "Name")

    monkeypatch.setattr(pornez.utils, "VideoPlayer", _PlayerNoResolve)
    pornez.Play("https://pornezoo.net/watch/2", "Name")

    assert play_resolve == ["https://embed/player"]
    assert play_direct == ["https://cdn/video.mp4"]
