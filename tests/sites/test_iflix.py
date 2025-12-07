"""Comprehensive tests for iflix.com site implementation."""
from pathlib import Path

from resources.lib.sites import iflix


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "iflix"


def load_fixture(name):
    """Load a fixture file from the iflix fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, timeout=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "contextm": kwargs.get("contextm"),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(iflix.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(iflix.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(iflix.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(iflix.utils, "eod", lambda: None)

    iflix.List("http://www.incestflix.com/page/1")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (text-heading)
    assert downloads[0]["name"] == "Mom Son Action"
    assert "12345" in downloads[0]["url"]
    assert "thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["contextm"] is not None  # Should have context menu

    # Check second video (text-overlay span)
    assert downloads[1]["name"] == "Sister Brother Fun"
    assert "67890" in downloads[1]["url"]
    assert "thumb2.jpg" in downloads[1]["icon"]

    # Check third video
    assert downloads[2]["name"] == "Family Taboo HD"
    assert "11111" in downloads[2]["url"]
    assert "thumb3.jpg" in downloads[2]["icon"]


def test_list_with_pagination(monkeypatch):
    """Test that List adds pagination when present."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, referer=None, timeout=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(iflix.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(iflix.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(iflix.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(iflix.utils, "eod", lambda: None)

    iflix.List("http://www.incestflix.com/page/1")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "page/2" in next_pages[0]["url"]
    assert "(2)" in next_pages[0]["name"]


def test_list_handles_no_videos(monkeypatch):
    """Test that List handles pages with no videos gracefully."""
    html = "<html><body><div id='incflix-pager'></div></body></html>"

    def fake_get_html(url, referer=None, timeout=None):
        return html

    monkeypatch.setattr(iflix.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(iflix.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(iflix.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(iflix.utils, "eod", lambda: None)

    # Should not raise exception
    iflix.List("http://www.incestflix.com/page/999")


def test_list_handles_network_error(monkeypatch):
    """Test that List handles network errors gracefully."""

    def fake_get_html(url, referer=None, timeout=None):
        raise Exception("Network error")

    monkeypatch.setattr(iflix.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(iflix.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(iflix.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(iflix.utils, "eod", lambda: None)

    # Should not raise exception
    iflix.List("http://www.incestflix.com/page/1")


def test_list_url_normalization(monkeypatch):
    """Test that List normalizes protocol-relative URLs."""
    html = """
    <html>
    <a id="videolink" href="//www.incestflix.com/watch/test/video">
        <div class="img-overflow" style="background: url(//img.incestflix.com/test.jpg);"></div>
        <div class="text-heading">Test Video</div>
    </a>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None, timeout=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"url": url, "icon": iconimage})

    monkeypatch.setattr(iflix.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(iflix.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(iflix.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(iflix.utils, "eod", lambda: None)

    iflix.List("http://www.incestflix.com/page/1")

    assert len(downloads) == 1
    # Protocol-relative URLs should be converted to http:
    assert downloads[0]["url"].startswith("http:")
    assert downloads[0]["icon"].startswith("http:")
