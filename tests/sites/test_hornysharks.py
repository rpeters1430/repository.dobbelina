"""Tests for hornysharks site implementation."""

from resources.lib.sites import hornysharks


SAMPLE_LISTING_HTML = """
<html>
<body>
<div class="item">
  <a href="https://hornysharks.com/video/201/sample-video/" title="Sample Horny Sharks Video">
    <img src="https://hornysharks.com/thumb201.jpg" data-original="https://hornysharks.com/thumb201.jpg" alt="Sample Horny Sharks Video" />
    <span class="duration">18:22</span>
  </a>
</div>
<div class="pagination">
  <a href="https://hornysharks.com/latest-updates/2/">2</a>
</div>
</body>
</html>
"""


def test_hornysharks_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(hornysharks.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(hornysharks, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(hornysharks.utils, "eod", lambda: None)

    hornysharks.Main()

    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://hornysharks.com/latest-updates/"]


def test_hornysharks_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(hornysharks.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        hornysharks.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        hornysharks.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(hornysharks.utils, "eod", lambda: None)

    hornysharks.List("https://hornysharks.com/latest-updates/")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample Horny Sharks Video"
    assert downloads[0]["url"] == "https://hornysharks.com/video/201/sample-video/"
    assert downloads[0]["icon"] == "https://hornysharks.com/thumb201.jpg"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://hornysharks.com/latest-updates/2/"


def test_hornysharks_playvid(monkeypatch):
    played = {}

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_kt_player(self, html, url=None):
            played["html"] = html
            played["url"] = url

    html = "<script>kt_player('kt_player', ...)</script>"
    monkeypatch.setattr(hornysharks.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(hornysharks.utils, "getHtml", lambda *a, **k: html)

    hornysharks.Playvid("https://hornysharks.com/video/201/sample-video/", "Sample")
    assert played["url"] == "https://hornysharks.com/video/201/sample-video/"
