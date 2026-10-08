"""Tests for fapello site implementation."""

from resources.lib.sites import fapello


SAMPLE_LISTING_HTML = """
<html>
<body>
<div>
  <a href="https://fapello.com/video/new/100/">
    <img src="https://fapello.com/thumb100.jpg" alt="Sample Fapello Leak Video" />
  </a>
</div>
<div id="pagination">
  <a href="https://fapello.com/videos/page/2/">2</a>
</div>
</body>
</html>
"""


def test_fapello_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(fapello.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(fapello, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(fapello.utils, "eod", lambda: None)

    fapello.Main()

    assert any(d[2] == "Search" for d in dirs)
    assert any("Trending" in d[0] for d in dirs)
    assert list_calls == ["https://fapello.com/videos/"]


def test_fapello_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(fapello.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        fapello.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        fapello.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(fapello.utils, "eod", lambda: None)

    fapello.List("https://fapello.com/videos/")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample Fapello Leak Video"
    assert downloads[0]["url"] == "https://fapello.com/video/new/100/"
    assert downloads[0]["icon"] == "https://fapello.com/thumb100.jpg"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://fapello.com/videos/page/2/"


def test_fapello_playvid(monkeypatch):
    played_url = []

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_url(self, url):
            played_url.append(url)

    html = '<video id="player" src="https://cdn.fapello.com/video100.mp4"></video>'
    monkeypatch.setattr(fapello.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(fapello.utils, "getHtml", lambda *a, **k: html)

    fapello.Playvid("https://fapello.com/video/new/100/", "Sample 100")
    assert played_url == ["https://cdn.fapello.com/video100.mp4"]
