"""Tests for xgirls site implementation."""

from resources.lib.sites import xgirls


SAMPLE_LISTING_HTML = """
<html>
<body>
<div class="card-col">
  <a class="drop-card" href="https://xgirls.webcam/video/100/sample-cam-show/">
    <img alt="Sample Model Show" src="https://xgirls.webcam/thumb1.jpg" data-original="https://xgirls.webcam/orig1.jpg" />
    <span class="card-time">45:10</span>
  </a>
</div>
<ul class="pagination">
  <li><a href="https://xgirls.webcam/latest-updates/2/">2</a></li>
</ul>
</body>
</html>
"""


def test_xgirls_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(xgirls.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(xgirls, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(xgirls.utils, "eod", lambda: None)

    xgirls.Main()

    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://xgirls.webcam/latest-updates/"]


def test_xgirls_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(xgirls.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        xgirls.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        xgirls.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(xgirls.utils, "eod", lambda: None)

    xgirls.List("https://xgirls.webcam/latest-updates/")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample Model Show"
    assert downloads[0]["url"] == "https://xgirls.webcam/video/100/sample-cam-show/"
    assert downloads[0]["icon"] == "https://xgirls.webcam/orig1.jpg"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://xgirls.webcam/latest-updates/2/"


def test_xgirls_playvid(monkeypatch):
    played = {}

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_kt_player(self, html, url=None):
            played["html"] = html
            played["url"] = url

    html = "<script>kt_player('kt_player', ...)</script>"
    monkeypatch.setattr(xgirls.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(xgirls.utils, "getHtml", lambda *a, **k: html)

    xgirls.Playvid("https://xgirls.webcam/video/100/sample-cam-show/", "Sample")
    assert played["url"] == "https://xgirls.webcam/video/100/sample-cam-show/"


def test_xgirls_search(monkeypatch):
    list_called = []
    search_dirs = []

    monkeypatch.setattr(xgirls.site, "search_dir", lambda url, mode: search_dirs.append(url))
    monkeypatch.setattr(xgirls, "List", lambda url: list_called.append(url))

    xgirls.Search("https://xgirls.webcam/search/{0}/")
    assert len(search_dirs) == 1

    xgirls.Search("https://xgirls.webcam/search/{0}/", keyword="latina brunette")
    assert list_called == ["https://xgirls.webcam/search/latina+brunette/"]
