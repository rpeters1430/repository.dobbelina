"""Tests for hentaicity site implementation."""

from resources.lib.sites import hentaicity


SAMPLE_LISTING_HTML = """
<html>
<body>
<div class="item">
  <div class="thumb-ratio">
    <a class="thumb-img" href="https://www.hentaicity.com/video/sample-video-1.html">
      <img alt="Sample Hentai Video 1" src="https://cdn.hentaicity.com/thumb1.jpg" />
      <span class="time">12:34</span>
    </a>
  </div>
</div>
<div class="item">
  <div class="thumb-ratio">
    <a class="thumb-img" href="https://www.hentaicity.com/video/sample-video-2.html">
      <img alt="Sample Hentai Video 2" src="https://cdn.hentaicity.com/thumb2.jpg" />
      <span class="time">20:15</span>
    </a>
  </div>
</div>
<div class="pagination">
  <a href="https://www.hentaicity.com/videos/page-2.html">Next</a>
</div>
</body>
</html>
"""


def test_hentaicity_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(hentaicity.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(hentaicity, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(hentaicity.utils, "eod", lambda: None)

    hentaicity.Main()

    assert any(d[2] == "Categories" for d in dirs)
    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://www.hentaicity.com/videos/"]


def test_hentaicity_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(hentaicity.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        hentaicity.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        hentaicity.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(hentaicity.utils, "eod", lambda: None)

    hentaicity.List("https://www.hentaicity.com/videos/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Sample Hentai Video 1"
    assert downloads[0]["url"] == "https://www.hentaicity.com/video/sample-video-1.html"
    assert downloads[0]["icon"] == "https://cdn.hentaicity.com/thumb1.jpg"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://www.hentaicity.com/videos/page-2.html"


def test_hentaicity_playvid(monkeypatch):
    played_url = []

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_url(self, url):
            played_url.append(url)

    html = '<video><source src="https://hls.hentaicity.com/master.m3u8" /></video>'
    monkeypatch.setattr(hentaicity.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(hentaicity.utils, "getHtml", lambda *a, **k: html)

    hentaicity.Playvid("https://www.hentaicity.com/video/sample-1.html", "Sample 1")
    assert played_url == ["https://hls.hentaicity.com/master.m3u8"]


def test_hentaicity_search(monkeypatch):
    list_called = []
    search_dirs = []

    monkeypatch.setattr(hentaicity.site, "search_dir", lambda url, mode: search_dirs.append(url))
    monkeypatch.setattr(hentaicity, "List", lambda url: list_called.append(url))

    hentaicity.Search("https://www.hentaicity.com/customsearch.php?search={0}&search_type=video")
    assert len(search_dirs) == 1

    hentaicity.Search("https://www.hentaicity.com/customsearch.php?search={0}&search_type=video", keyword="nurse cosplay")
    assert list_called == ["https://www.hentaicity.com/customsearch.php?search=nurse+cosplay&search_type=video"]
