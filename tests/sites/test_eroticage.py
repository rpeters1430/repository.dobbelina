"""Tests for eroticage.net site implementation."""

from resources.lib.sites import eroticage


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <article data-video-id="123">
        <a href="/video/hot-video/" title="Hot Video Title">
            <img data-src="/thumbs/1.jpg" />
        </a>
    </article>
    <div class="pagination">
        <span class="current">1</span>
        <a href="/page/2/" class="next">Next</a>
        <a href="/page/10/" class="last">Last</a>
    </div>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(eroticage.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(eroticage.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(eroticage.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(eroticage.utils, "eod", lambda: None)

    eroticage.List("https://www.eroticage.net/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"
    
    assert len(dirs) == 1
    assert "Next Page (2/10)" in dirs[0]


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses categories."""
    html = """
    <html>
    <article id="post-1">
        <a href="/categories/milf/">
            <img src="/thumbs/milf.jpg" />
            <div class="cat-title">MILF</div>
        </a>
    </article>
    </html>
    """

    dirs = []

    monkeypatch.setattr(eroticage.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(eroticage.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(eroticage.utils, "eod", lambda: None)

    eroticage.Categories("https://www.eroticage.net/categories/")

    assert len(dirs) == 1
    assert "MILF" in dirs[0]