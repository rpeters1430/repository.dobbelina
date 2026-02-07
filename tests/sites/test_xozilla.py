"""Tests for xozilla.com site implementation."""

from resources.lib.sites import xozilla


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <a href="/video/hot-video/" class="item" thumb="/thumbs/1.jpg">
        <div class="duration">10:00</div>
        <div class="title">Hot Video Title</div>
    </a>
    <li class="next"><a href="/videos/2/" data-block-id="1" data-parameters="p1:v1;p2:v2">Next:2</a></li>
    <li class="last"><a href="/videos/10/">Last:10</a></li>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(xozilla.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        xozilla.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(xozilla.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(xozilla.utils, "eod", lambda: None)

    xozilla.List("https://www.xozilla.com/latest-updates/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"

    assert len(dirs) == 1
    assert "Next Page (2/10)" in dirs[0]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories function parses category data."""
    html = """
    <html>
    <a href="/categories/milf/">MILF<span class="rating">5.0</span></a>
    <a href="/categories/amateur/">Amateur<span class="rating">4.5</span></a>
    </html>
    """

    dirs = []

    monkeypatch.setattr(xozilla.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(xozilla.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(xozilla.utils, "eod", lambda: None)

    xozilla.Categories("https://www.xozilla.com/categories/")

    assert len(dirs) == 2
    assert "Amateur" in dirs[0]
    assert "MILF" in dirs[1]
