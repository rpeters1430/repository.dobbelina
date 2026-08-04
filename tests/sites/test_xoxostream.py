"""Tests for xoxostream.com site implementation.

Note: xoxostream.py ports upstream's regex-based scraper verbatim (no live
HTML fixture was available to validate BeautifulSoup selectors against), so
these tests use synthetic HTML crafted to match the exact regex groups it
relies on.
"""

from resources.lib.sites import xoxostream


def test_list_parses_video_items(monkeypatch):
    html = (
        '<li id="video-1"><a href="https://xoxostream.com/video/1/hot-clip/" title="Hot Clip">'
        '<img src="https://cdn.xoxostream.com/thumb1.jpg" alt="t"></a>'
        '<span class="duration">;05:30</span></li>'
        '<li id="video-2"><a href="//xoxostream.com/video/2/second-clip/" title="Second Clip">'
        '<img src="https://cdn.xoxostream.com/thumb2.jpg" alt="t"></a>'
        '<span class="duration">;03:15</span></li>'
    )

    downloads = []

    def fake_get_html(url, *a, **k):
        return html

    monkeypatch.setattr(xoxostream.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        xoxostream.site,
        "add_download_link",
        lambda name, url, mode, img, desc, **k: downloads.append(
            {"name": name, "url": url, "duration": k.get("duration")}
        ),
    )
    monkeypatch.setattr(xoxostream.utils, "eod", lambda: None)

    xoxostream.List("https://xoxostream.com/1/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Clip"
    assert downloads[0]["url"] == "https://xoxostream.com/video/1/hot-clip/"
    assert downloads[0]["duration"] == "05:30"
    assert downloads[1]["url"] == "https://xoxostream.com/video/2/second-clip/"


def test_list_notifies_when_no_videos(monkeypatch):
    notifications = []

    monkeypatch.setattr(xoxostream.utils, "getHtml", lambda *a, **k: "<html></html>")
    monkeypatch.setattr(
        xoxostream.utils, "notify", lambda header, msg="": notifications.append((header, msg))
    )

    xoxostream.List("https://xoxostream.com/1/")

    assert notifications == [("XOXOstream", "No video found!")]


def test_tags_parses_tag_list(monkeypatch):
    html = (
        '<ul class="tags_list">'
        '<li><a href="amateur/" class="tag-item">Amateur</a></li>'
        '<li><a href="teen/" class="tag-item">Teen</a></li>'
        "</ul>"
    )

    dirs = []

    monkeypatch.setattr(xoxostream.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(xoxostream.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(xoxostream.utils, "eod", lambda: None)

    xoxostream.Tags("https://xoxostream.com/tags/")

    assert len(dirs) == 2
    assert "Amateur" in dirs[0][0]
    assert dirs[0][1] == "https://xoxostream.com/tags/amateur/"


def test_playvid_builds_direct_link(monkeypatch):
    html = '<p id="description" class="M1 D2 Q3 tid4 720p secureTok 1690000000"></p>'
    captured = {}

    monkeypatch.setattr(xoxostream.utils, "getHtml", lambda *a, **k: html)

    class FakeProgress:
        def update(self, *a, **k):
            pass

    class FakeVideoPlayer:
        def __init__(self, name, download):
            self.progress = FakeProgress()

        def play_from_direct_link(self, url):
            captured["url"] = url

    monkeypatch.setattr(xoxostream.utils, "VideoPlayer", FakeVideoPlayer)

    xoxostream.Playvid("https://xoxostream.com/video/1/x/", "Some Video")

    assert captured["url"] == (
        "https://vdownload-M1.sb-cd.com/D2/Q3/tid4-720p.mp4"
        "?secure=secureTok,1690000000&m=M1&d=D2&_tid=tid4"
    )
