"""Tests for vipporns.com site implementation."""

from resources.lib.sites import vipporns


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <div id="list_videos_common_videos_list">
        <div class="item">
            <a href="/video/hot-video/" title="Hot Video Title">
                <img data-original="/thumbs/1.jpg" />
                <span class="duration">10:00</span>
            </a>
        </div>
    </div>
    <li class="next">
        <a href="#" data-block-id="1" data-parameters="p1:v1;page:2">Next</a>
    </li>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(vipporns.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        vipporns.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(vipporns.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(vipporns.utils, "eod", lambda: None)

    vipporns.List("https://www.vipporns.com/new-porn-video/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"

    assert len(dirs) == 1
    assert "Next Page..." in dirs[0]
    assert "(2)" in dirs[0]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses categories."""
    html = """
    <html>
    <div class="item">
        <a href="/categories/milf/">
            <img src="/thumbs/milf.jpg" />
            <div class="title">MILF</div>
            <div class="videos">123</div>
        </a>
    </div>
    </html>
    """

    dirs = []

    monkeypatch.setattr(vipporns.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(vipporns.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(vipporns.utils, "eod", lambda: None)

    vipporns.Cat("https://www.vipporns.com/categories/")

    assert len(dirs) == 1
    assert "MILF" in dirs[0]
    assert "(123)" in dirs[0]


def test_search_lists_videos_not_photo_albums(monkeypatch):
    """Search pages show a photo-album block above the videos; only videos may be listed."""
    from pathlib import Path

    html = (
        Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "vipporns" / "search_latina.html"
    ).read_text(encoding="utf-8")
    downloads = []
    monkeypatch.setattr(vipporns.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(vipporns.site, "add_download_link", lambda *a, **k: downloads.append(a[1]))
    monkeypatch.setattr(vipporns.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(vipporns.utils, "eod", lambda *a, **k: None)

    vipporns.List("https://www.vipporns.com/vp-search/latina/")

    assert len(downloads) == 24
    assert all("/porn-videos/" in u for u in downloads)
