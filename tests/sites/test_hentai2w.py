"""Tests for hentai2w site implementation."""

from resources.lib.sites import hentai2w


SAMPLE_LISTING_HTML = """
<html>
<body>
<div class="item-col col -video">
  <a href="https://hentai2w.com/video/sample-episode-1.html" title="Sample Episode 1">
    <span class="image">
      <img alt="Sample Episode 1" src="https://media.hentai2w.com/thumb1.jpg" />
      <span class="item-time">15:00</span>
    </span>
    <span class="item-info">
      <span class="item-name">Sample Episode 1</span>
    </span>
  </a>
</div>
<div class="pagination">
  <a href="https://hentai2w.com/videos/page2.html">2</a>
</div>
</body>
</html>
"""


def test_hentai2w_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(hentai2w.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(hentai2w, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(hentai2w.utils, "eod", lambda: None)

    hentai2w.Main()

    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://hentai2w.com/videos/"]


def test_hentai2w_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(hentai2w.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        hentai2w.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        hentai2w.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(hentai2w.utils, "eod", lambda: None)

    hentai2w.List("https://hentai2w.com/videos/")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample Episode 1"
    assert downloads[0]["url"] == "https://hentai2w.com/video/sample-episode-1.html"
    assert downloads[0]["icon"] == "https://media.hentai2w.com/thumb1.jpg"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://hentai2w.com/videos/page2.html"


def test_hentai2w_playvid(monkeypatch):
    played_url = []

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_url(self, url):
            played_url.append(url)

    html = '<video><source src="https://media.hentai2w.com/video.mp4" /></video>'
    monkeypatch.setattr(hentai2w.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(hentai2w.utils, "getHtml", lambda *a, **k: html)

    hentai2w.Playvid("https://hentai2w.com/video/sample-1.html", "Sample 1")
    assert played_url == ["https://media.hentai2w.com/video.mp4"]


def test_hentai2w_search(monkeypatch):
    list_called = []
    search_dirs = []

    monkeypatch.setattr(hentai2w.site, "search_dir", lambda url, mode: search_dirs.append(url))
    monkeypatch.setattr(hentai2w, "List", lambda url: list_called.append(url))

    hentai2w.Search("https://hentai2w.com/search/{0}/")
    assert len(search_dirs) == 1

    hentai2w.Search("https://hentai2w.com/search/{0}/", keyword="magic school")
    assert list_called == ["https://hentai2w.com/search/magic+school/"]
