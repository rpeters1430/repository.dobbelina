"""Tests for freeomovie.to site implementation."""

from resources.lib.sites import freeomovie


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <div class="thumi">
        <a href="/video/hot-video/" title="Hot Video Title">
            <img src="/thumbs/1.jpg" />
        </a>
    </div>
    <a rel="next" href="/page/2/">Next</a>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(freeomovie.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(freeomovie.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(freeomovie.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(freeomovie.utils, "eod", lambda: None)

    freeomovie.List("https://www.freeomovie.to/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"
    
    assert len(dirs) == 1
    assert "Next Page... (2)" in dirs[0]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses categories."""
    html = """
    <html>
    <li class="cat-item">
        <a href="/categories/milf/">MILF</a>
    </li>
    </html>
    """

    dirs = []

    monkeypatch.setattr(freeomovie.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(freeomovie.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(freeomovie.utils, "eod", lambda: None)

    freeomovie.Cat("https://www.freeomovie.to/")

    assert len(dirs) == 1
    assert "MILF" in dirs[0]