"""Tests for iceporncasting.net site implementation."""

from pathlib import Path
from resources.lib.sites import iceporncasting


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "iceporncasting"


def load_fixture(name="listing.html"):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_main_registers_core_dirs(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(
        iceporncasting.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append((name, url, mode)),
    )
    monkeypatch.setattr(iceporncasting, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(iceporncasting.utils, "eod", lambda: None)

    iceporncasting.Main()

    assert len(dirs) == 3
    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Pornstars" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://iceporncasting.net/latest-casting-videos/"]


def test_list_parses_video_items(monkeypatch):
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(iceporncasting.utils, "getHtml", lambda url, referer=None: html)
    monkeypatch.setattr(
        iceporncasting.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", duration="", **k: downloads.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage, "duration": duration}
        ),
    )
    monkeypatch.setattr(
        iceporncasting.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(iceporncasting.utils, "eod", lambda: None)

    iceporncasting.List("https://iceporncasting.net/latest-casting-videos/")

    assert len(downloads) == 30
    assert "Public Agent: Valentina Coppola" in downloads[0]["name"]
    assert downloads[0]["url"] == "https://iceporncasting.net/public-agent-valentina-coppola-muscular-woman-liked-big-things-212219/"
    assert downloads[0]["icon"] == "https://iceporncasting.net/wp-content/uploads/2026/10/poster_01-2.jpg"
    assert downloads[0]["duration"] == "31:13"
    assert downloads[0]["mode"] == "Playvid"

    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://iceporncasting.net/latest-casting-videos/page/2/"


def test_categories(monkeypatch):
    cat_html = """
    <article class="thumb-block">
        <a href="https://iceporncasting.net/channel/amateur-auditions/" title="Amateur">
            <span class="cat-title">Amateur Auditions</span>
        </a>
    </article>
    <a rel="next" href="https://iceporncasting.net/1f/channels/page/2/">Next</a>
    """
    dirs = []
    monkeypatch.setattr(iceporncasting.utils, "getHtml", lambda url, referer=None: cat_html)
    monkeypatch.setattr(
        iceporncasting.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(iceporncasting.utils, "eod", lambda: None)

    iceporncasting.Categories("https://iceporncasting.net/1f/channels/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Amateur Auditions"
    assert dirs[0]["url"] == "https://iceporncasting.net/channel/amateur-auditions/"
    assert dirs[1]["name"] == "Next Page..."
    assert dirs[1]["url"] == "https://iceporncasting.net/1f/channels/page/2/"


def test_pornstars(monkeypatch):
    ps_html = """
    <article class="thumb-block">
        <a href="https://iceporncasting.net/kat-squirt-36567/" title="Kat Squirt">
            <img src="https://iceporncasting.net/wp-content/uploads/kat.jpg" />
            <span class="cat-title">Kat Squirt</span>
        </a>
    </article>
    <a rel="next" href="https://iceporncasting.net/pornstars/page/2/">Next</a>
    """
    dirs = []
    monkeypatch.setattr(iceporncasting.utils, "getHtml", lambda url, referer=None: ps_html)
    monkeypatch.setattr(
        iceporncasting.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(iceporncasting.utils, "eod", lambda: None)

    iceporncasting.Pornstars("https://iceporncasting.net/pornstars/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Kat Squirt"
    assert dirs[0]["url"] == "https://iceporncasting.net/kat-squirt-36567/"
    assert dirs[0]["icon"] == "https://iceporncasting.net/wp-content/uploads/kat.jpg"
    assert dirs[1]["name"] == "Next Page..."
    assert dirs[1]["url"] == "https://iceporncasting.net/pornstars/page/2/"


def test_search_without_keyword(monkeypatch):
    search_called = []
    monkeypatch.setattr(
        iceporncasting.site,
        "search_dir",
        lambda url, mode: search_called.append((url, mode)),
    )

    iceporncasting.Search("https://iceporncasting.net/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    list_calls = []
    monkeypatch.setattr(iceporncasting, "List", lambda url: list_calls.append(url))

    iceporncasting.Search("https://iceporncasting.net/?s=", keyword="amateur audition")

    assert list_calls == ["https://iceporncasting.net/?s=amateur+audition"]


def test_playvid_lulustream_unpacked(monkeypatch):
    played = []

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            pass

        def play_from_direct_link(self, stream_url):
            played.append(stream_url)

        def play_from_link_list(self, links):
            pass

    page_html = '<iframe src="https://lulust.com/e/abc123xyz"></iframe>'
    embed_html = """
    <html>
    <script>
    eval(function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\\\b'+c.toString(a)+'\\\\b','g'),k[c]);return p}('0.1({2:[{3:"4://5.6/7.8"}]});',9,9,'jwplayer|setup|sources|file|https|stream|net|playlist|m3u8'.split('|')))
    </script>
    </html>
    """

    def fake_get_html(url, referer=None, **kwargs):
        if "iceporncasting.net" in url:
            return page_html
        if "lulust.com" in url:
            return embed_html
        return ""

    monkeypatch.setattr(iceporncasting.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(iceporncasting.utils, "getHtml", fake_get_html)

    iceporncasting.Playvid("https://iceporncasting.net/video-123/", "Test Video")

    assert len(played) == 1
    assert "https://stream.net/playlist.m3u8" in played[0]
    assert "Referer=https%3A%2F%2Flulust.com%2F" in played[0]


def test_playvid_xvideos(monkeypatch):
    played = []

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            pass

        def play_from_direct_link(self, stream_url):
            played.append(stream_url)

        def play_from_link_list(self, links):
            pass

    page_html = '<iframe src="https://www.xvideos.com/embedframe/12345"></iframe>'
    xvideos_html = "<script>html5player.setVideoHLS('https://cdn.xvideos.com/hls.m3u8');</script>"

    def fake_get_html(url, referer=None, **kwargs):
        if "iceporncasting.net" in url:
            return page_html
        if "xvideos.com" in url:
            return xvideos_html
        return ""

    monkeypatch.setattr(iceporncasting.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(iceporncasting.utils, "getHtml", fake_get_html)

    iceporncasting.Playvid("https://iceporncasting.net/video-456/", "Test Video")

    assert len(played) == 1
    assert "https://cdn.xvideos.com/hls.m3u8|Referer=https://www.xvideos.com/" in played[0]
