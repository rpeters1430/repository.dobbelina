"""Tests for xhuzz site implementation."""

from resources.lib.sites import xhuzz


SAMPLE_LISTING_HTML = """
<html>
<body>
<div>
  <a class="group" href="/video/sample-xhuzz-video">
    <img alt="Sample xHuzz Video" src="https://cdn.xhuzz.com/thumb.jpg" />
  </a>
</div>
<div class="pagination">
  <a href="/videos?page=2">2</a>
</div>
</body>
</html>
"""


def test_xhuzz_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(xhuzz.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(xhuzz, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(xhuzz.utils, "eod", lambda: None)

    xhuzz.Main()

    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://xhuzz.com/videos"]


def test_xhuzz_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(xhuzz.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        xhuzz.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        xhuzz.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(xhuzz.utils, "eod", lambda: None)

    xhuzz.List("https://xhuzz.com/videos")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample xHuzz Video"
    assert downloads[0]["url"] == "https://xhuzz.com/video/sample-xhuzz-video"
    assert downloads[0]["icon"] == "https://cdn.xhuzz.com/thumb.jpg"


def test_xhuzz_playvid(monkeypatch):
    resolved = []

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_link(self, url):
            resolved.append(url)
            return True

    html = '<button class="source-btn" data-src="https://streamtape.com/e/12345">Source 1</button>'
    monkeypatch.setattr(xhuzz.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(xhuzz.utils, "getHtml", lambda *a, **k: html)

    xhuzz.Playvid("https://xhuzz.com/video/sample-xhuzz-video", "Sample")
    assert resolved == ["https://streamtape.com/e/12345"]
