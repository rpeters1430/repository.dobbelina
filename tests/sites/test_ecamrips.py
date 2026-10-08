"""Tests for ecamrips site implementation."""

from resources.lib.sites import ecamrips


SAMPLE_LISTING_HTML = """
<html>
<body>
<ul>
  <li id="li1">
    <a class="moiclick1" href="https://www.ecamrips.com/show-cam-sex-movies/101-sample-cam-rip.html" title="Sample Cam Rip 101">
      <img src="https://www.ecamrips.com/thumb1.jpg" data-src="https://www.ecamrips.com/thumb1.jpg" alt="Sample Cam Rip 101" />
    </a>
  </li>
</ul>
<div class="pages">
  <a href="https://www.ecamrips.com/en/page2.html">2</a>
</div>
</body>
</html>
"""


def test_ecamrips_main(monkeypatch):
    dirs = []
    list_calls = []

    monkeypatch.setattr(ecamrips.site, "add_dir", lambda name, url, mode, icon=None: dirs.append((name, url, mode)))
    monkeypatch.setattr(ecamrips, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(ecamrips.utils, "eod", lambda: None)

    ecamrips.Main()

    assert any(d[2] == "Search" for d in dirs)
    assert list_calls == ["https://www.ecamrips.com/en/"]


def test_ecamrips_list(monkeypatch):
    downloads = []
    dirs = []

    monkeypatch.setattr(ecamrips.utils, "getHtml", lambda url, referer=None: SAMPLE_LISTING_HTML)
    monkeypatch.setattr(
        ecamrips.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode, "icon": iconimage}),
    )
    monkeypatch.setattr(
        ecamrips.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(ecamrips.utils, "eod", lambda: None)

    ecamrips.List("https://www.ecamrips.com/en/")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Sample Cam Rip 101"
    assert downloads[0]["url"] == "https://www.ecamrips.com/show-cam-sex-movies/101-sample-cam-rip.html"
    assert len(dirs) == 1
    assert dirs[0]["url"] == "https://www.ecamrips.com/en/page2.html"


def test_ecamrips_playvid(monkeypatch):
    played_url = []

    class _DummyVP:
        def __init__(self, name, download=None):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_url(self, url):
            played_url.append(url)

    html_page = '<iframe src="https://www.ecamrips.com/loading_video.php?idd=101"></iframe>'
    html_frame = '<video><source src="https://cdn.ecamrips.com/video101.mp4" /></video>'

    def fake_gethtml(url, *args, **kwargs):
        if "loading_video.php" in url:
            return html_frame
        return html_page

    monkeypatch.setattr(ecamrips.utils, "VideoPlayer", _DummyVP)
    monkeypatch.setattr(ecamrips.utils, "getHtml", fake_gethtml)

    ecamrips.Playvid("https://www.ecamrips.com/show-cam-sex-movies/101-sample.html", "Sample 101")
    assert played_url == ["https://cdn.ecamrips.com/video101.mp4"]
