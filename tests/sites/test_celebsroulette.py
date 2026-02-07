"""Tests for celebsroulette.com site implementation."""

from resources.lib.sites import celebsroulette


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <div class="item">
        <a href="/video/hot-video/" title="Hot Video Title">
            <img data-original="/thumbs/1.jpg" />
        </a>
    </div>
    <a href="/videos/2/">Next:2</a>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(celebsroulette.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        celebsroulette.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(
        celebsroulette.site, "add_dir", lambda *a, **k: dirs.append(a[0])
    )
    monkeypatch.setattr(celebsroulette.utils, "eod", lambda: None)

    celebsroulette.List("https://celebsroulette.com/latest-updates/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"

    assert len(dirs) == 1
    assert "Next Page (2)" in dirs[0]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses categories."""
    html = """
    <html>
    <a class="item" href="/categories/milf/" title="MILF">
        <img src="/thumbs/milf.jpg" />
        <div class="videos">123</div>
    </a>
    </html>
    """

    dirs = []

    monkeypatch.setattr(celebsroulette.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        celebsroulette.site, "add_dir", lambda *a, **k: dirs.append(a[0])
    )
    monkeypatch.setattr(celebsroulette.utils, "eod", lambda: None)

    celebsroulette.Categories("https://celebsroulette.com/categories/")

    assert len(dirs) == 1
    assert "MILF" in dirs[0]
    assert "123" in dirs[0]
