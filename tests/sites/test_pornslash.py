"""Tests for pornslash.com site scraper implementation."""

from resources.lib.sites import pornslash


def test_list_parses_video_items(monkeypatch):
    html = (
        '<div class="video-item" data-title="Awesome Video">'
        '<a href="/watch/12345" title="Awesome Video">'
        '<img src="https://cdn.pornslash.com/thumb1.jpg" alt="thumb">'
        '<span class="quality">1080p</span>'
        '<span class="duration">12:34</span>'
        '</a></div>'
        '<div class="video-item" data-title="Second Video">'
        '<a href="/watch/67890" title="Second Video">'
        '<img src="https://cdn.pornslash.com/thumb2.jpg" alt="thumb">'
        '<span class="quality">720p</span>'
        '<span class="duration">08:20</span>'
        '</a></div>'
        '<a class="next" href="/videos/new?p=2"><span class="nav-btn">Next</span></a>'
    )

    downloads = []
    dirs = []

    monkeypatch.setattr(pornslash.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        pornslash.site,
        "add_download_link",
        lambda name, url, mode, img, desc, **k: downloads.append(
            {"name": name, "url": url, "duration": k.get("duration"), "img": img}
        ),
    )
    monkeypatch.setattr(pornslash.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(pornslash.utils, "eod", lambda: None)

    pornslash.List("https://www.pornslash.com/videos/new?p=1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Awesome Video [COLOR yellow]1080p[/COLOR]"
    assert downloads[0]["url"] == "https://www.pornslash.com/watch/12345"
    assert downloads[0]["duration"] == "12:34"
    assert downloads[1]["url"] == "https://www.pornslash.com/watch/67890"

    assert len(dirs) == 1
    assert "Next Page" in dirs[0][0]
    assert dirs[0][1] == "https://www.pornslash.com/videos/new?p=2"


def test_list_notifies_when_empty(monkeypatch):
    notifications = []

    monkeypatch.setattr(pornslash.utils, "getHtml", lambda *a, **k: "<div></div>")
    monkeypatch.setattr(
        pornslash.utils, "notify", lambda header, msg="": notifications.append((header, msg))
    )

    pornslash.List("https://www.pornslash.com/videos/new?p=1")

    assert notifications == [("PornSlash", "No video found!")]


def test_categories_parses_items(monkeypatch):
    html = (
        '<a class="cat-item" href="/category/amateur">'
        '<img src="https://cdn.pornslash.com/cat1.jpg">'
        '<span class="cat-name">Amateur</span></a>'
        '<a class="cat-item" href="/category/anal">'
        '<img src="https://cdn.pornslash.com/cat2.jpg">'
        '<span class="cat-name">Anal</span></a>'
    )

    dirs = []

    monkeypatch.setattr(pornslash.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornslash.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(pornslash.utils, "eod", lambda: None)

    pornslash.Categories("https://www.pornslash.com/categories")

    assert len(dirs) == 2
    assert dirs[0][0] == "Amateur"
    assert dirs[0][1] == "https://www.pornslash.com/category/amateur?p=1"
    assert dirs[1][0] == "Anal"


def test_stars_parses_items(monkeypatch):
    html = (
        '<a class="poster-wrapper" href="/star/eva-elfie">'
        '<img src="https://cdn.pornslash.com/star1.jpg" alt="Eva Elfie"></a>'
        '<a class="next" href="/pornstars?p=2"><span class="nav-btn">Next</span></a>'
    )

    dirs = []

    monkeypatch.setattr(pornslash.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornslash.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(pornslash.utils, "eod", lambda: None)

    pornslash.Stars("https://www.pornslash.com/pornstars?p=1")

    assert len(dirs) == 2
    assert dirs[0][0] == "Eva Elfie"
    assert dirs[0][1] == "https://www.pornslash.com/star/eva-elfie"
    assert "Next Page" in dirs[1][0]
    assert dirs[1][1] == "https://www.pornslash.com/pornstars?p=2"


def test_playvid_parses_and_selects_stream(monkeypatch):
    embed_html = '<script>fetch("https://stream.trycloudflare.com/master/test1234")</script>'
    m3u8_content = (
        '#EXTM3U\n'
        '#EXT-X-STREAM-INF:BANDWIDTH=1000,RESOLUTION=1280x720\n'
        'https://stream.trycloudflare.com/playlist/test1234/720\n'
        '#EXT-X-STREAM-INF:BANDWIDTH=2000,RESOLUTION=1920x1080\n'
        'https://stream.trycloudflare.com/playlist/test1234/1080\n'
    )

    captured = {}

    def fake_get_html(url, *a, **k):
        if "master" in url:
            return m3u8_content
        return embed_html

    monkeypatch.setattr(pornslash.utils, "getHtml", fake_get_html)

    class FakeProgress:
        def update(self, *a, **k):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = FakeProgress()

        def play_from_direct_link(self, url):
            captured["url"] = url

    monkeypatch.setattr(pornslash.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(pornslash.utils, "selector", lambda title, sources, **k: sources.get("1920x1080"))

    pornslash.Playvid("https://www.pornslash.com/watch/12345", "Test Video")

    assert captured["url"].startswith("https://stream.trycloudflare.com/playlist/test1234/1080")
    assert "User-Agent=" in captured["url"]
