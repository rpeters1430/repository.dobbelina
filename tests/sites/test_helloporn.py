"""Tests for helloporn site implementation."""

from resources.lib.sites import helloporn


SAMPLE_LISTING_HTML = """
<html>
<body>
<div class="videoBoxWrapper">
  <a class="videoBox" href="https://helloporn.com/video-100-sample-video">
    <picture>
      <img src="https://helloporn.com/thumb.jpg" data-src="https://helloporn.com/thumb.jpg" />
    </picture>
  </a>
  <a class="videoBoxTitle" href="https://helloporn.com/video-100-sample-video" title="Sample HelloPorn Video">Sample HelloPorn Video</a>
</div>
<li class="page-item">
  <a class="page-link" href="https://helloporn.com/videos/2">2</a>
</li>
</body>
</html>
"""


def test_helloporn_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(helloporn.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(helloporn, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(helloporn.utils, "eod", lambda: None)

    helloporn.Main()

    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://helloporn.com/videos"]


def test_helloporn_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(helloporn.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        helloporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        helloporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(helloporn.utils, "eod", lambda: None)

    helloporn.List("https://helloporn.com/videos")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample HelloPorn Video"
    assert downloads[0]["url"] == "https://helloporn.com/video-100-sample-video"
    assert downloads[0]["icon"] == "https://helloporn.com/thumb.jpg"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://helloporn.com/videos/2"


def test_helloporn_playvid(monkeypatch):
    resolved = []

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_link(self, url):
            resolved.append(url)
            return True

    html = '<div class="embedPlayerWrapper"><iframe class="embedPlayer" src="https://voe.sx/e/sample123"></iframe></div>'
    monkeypatch.setattr(helloporn.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(helloporn.utils, "getHtml", lambda *a, **k: html)

    helloporn.Playvid("https://helloporn.com/video-100-sample-video", "Sample")
    assert resolved == ["https://voe.sx/e/sample123"]
