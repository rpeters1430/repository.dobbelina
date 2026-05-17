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
