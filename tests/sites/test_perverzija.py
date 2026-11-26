"""Tests for perverzija site implementation."""

from resources.lib.sites import perverzija


def test_main_menu_adds_expected_dirs(monkeypatch):
    captured_dirs = []

    def add_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(perverzija.site, "add_dir", add_dir)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    perverzija.Main()

    assert any("Tags" in d["name"] for d in captured_dirs)
    assert any(d["mode"] == "Studios" for d in captured_dirs)
    assert any(d["mode"] == "Stars" for d in captured_dirs)


def test_list_parsing(monkeypatch):
    html = '<html><div class="item-thumbnail"><a href="/v/123" title="Video Title"><img src="t.jpg"></a></div></html>'
    captured_downloads = []

    def add_download(name, url, mode, icon, *args, **kwargs):
        captured_downloads.append({"name": name, "url": url})

    def fake_get_html_cf(url, *a, **k):
        return html, ""

    monkeypatch.setattr(perverzija.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(perverzija.site, "add_download_link", add_download)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    perverzija.List("https://tube.perverzija.com/")

    assert len(captured_downloads) == 1
    assert captured_downloads[0]["name"] == "Video Title"


def test_studios_parsing(monkeypatch):
    html = """
    <html>
      <div class="item-thumbnail">
        <a href="/studio/studio-one/">
          <img src="studio1.jpg">
          <div class="item-thumbnail-name">Studio One</div>
          <div class="item-thumbnail-count">5</div>
        </a>
      </div>
    </html>
    """
    captured_dirs = []

    def add_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append({"name": name, "url": url})

    def fake_get_html_cf(url, *a, **k):
        return html, ""

    monkeypatch.setattr(perverzija.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(perverzija.site, "add_dir", add_dir)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    perverzija.Studios("https://tube.perverzija.com/studios/")

    assert len(captured_dirs) == 1
    assert "Studio One" in captured_dirs[0]["name"]


def test_stars_parsing(monkeypatch):
    html = """
    <html>
      <div class="item-thumbnail">
        <a href="/stars/star-one/">
          <img src="star1.jpg">
          <div class="item-thumbnail-name">Star One</div>
          <div class="item-thumbnail-count">3</div>
        </a>
      </div>
    </html>
    """
    captured_dirs = []

    def add_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append({"name": name, "url": url})

    def fake_get_html_cf(url, *a, **k):
        return html, ""

    monkeypatch.setattr(perverzija.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(perverzija.site, "add_dir", add_dir)
    monkeypatch.setattr(perverzija.utils, "eod", lambda: None)

    perverzija.Stars("https://tube.perverzija.com/stars/")

    assert len(captured_dirs) == 1
    assert "Star One" in captured_dirs[0]["name"]


def test_play_xtremestream_xsftk_boot(monkeypatch):
    video_html = '<div class="player-embed"><iframe src="https://xtremestream.xyz/embed/123"></iframe></div>'
    iframe_html = """<script>XSFTK.boot('vid123', 'tok456');</script>"""
    master_m3u8 = (
        "#EXTM3U\n"
        "#EXT-X-STREAM-INF:BANDWIDTH=1000,RESOLUTION=1280x720\n"
        "https://cdn.xtremestream.xyz/720.m3u8\n"
    )
    played = []

    class FakeVP:
        def __init__(self, *a, **k):
            self.progress = type("P", (), {"update": lambda *a: None, "close": lambda *a: None})()
            self.IA_check = "skip"
            self.resolveurl = type("R", (), {"HostedMediaFile": lambda *a: type("H", (), {"valid_url": lambda: False})()})()

        def play_from_direct_link(self, link):
            played.append((self.IA_check, link))

    def fake_get_html(url, referer="", headers=None):
        if "embed/123" in url:
            return iframe_html
        if "op=castsign" in url:
            return "ABCDEFGHIJKLMNOP123456"
        if "op=castmaster" in url:
            return master_m3u8
        return ""

    monkeypatch.setattr(perverzija.utils, "VideoPlayer", FakeVP)
    monkeypatch.setattr(perverzija.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (video_html, ""))
    monkeypatch.setattr(perverzija.utils, "_getHtml", fake_get_html)

    perverzija.Play("https://www.perverzija.com/video/123/", "Test")

    assert len(played) == 1
    assert played[0][0] == "IA"
    assert played[0][1].startswith("https://cdn.xtremestream.xyz/720.m3u8|")
