"""Tests for pornroom.com site implementation."""

from resources.lib.sites import pornroom


def test_list_parses_videos(monkeypatch):
    """Test that pornroom_list correctly parses video items."""
    html = """
    <html>
    <div data-post-id="123">
        <a href="/video/hot-video/" title="Hot Video Title">
            <img poster="/thumbs/1.jpg" />
            <span class="duration">10:00</span>
        </a>
    </div>
    <div class="pagination">
        <span class="current">1</span>
        <a href="/videos/page/2/">2</a>
    </div>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(pornroom.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornroom.site, "add_download_link", lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(pornroom.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(pornroom.utils, "eod", lambda: None)

    pornroom.pornroom_list("https://thepornroom.com/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"
    
    assert len(dirs) == 1
    assert "Next Page (2)" in dirs[0]


def test_cat_parses_categories(monkeypatch):
    """Test that pornroom_cat correctly parses categories."""
    html = """
    <html>
    <div>
        <a class="thumb" href="/categories/milf/" title="MILF">
            <img data-src="/thumbs/milf.jpg" />
        </a>
        <div class="video-datas">123</div>
    </div>
    </html>
    """

    dirs = []

    monkeypatch.setattr(pornroom.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornroom.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(pornroom.utils, "eod", lambda: None)

    pornroom.pornroom_cat("https://thepornroom.com/categories/")

    assert len(dirs) == 1
    assert "MILF" in dirs[0]
    assert "(123)" in dirs[0]