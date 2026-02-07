"""Tests for hdporn.com site implementation."""

from resources.lib.sites import hdporn


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <div class="item">
        <a href="/video/hot-video/">
            <img data-original="/thumbs/1.jpg" />
            <div class="le">Hot Video Title</div>
            <div class="on">10:00</div>
            <div class="is-hd">HD</div>
        </a>
    </div>
    <div class="next">
        <a href="/porn-page/2/">Next</a>
    </div>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(hdporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        hdporn.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(hdporn.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(hdporn.utils, "eod", lambda: None)

    hdporn.List("https://www.porn00.org/porn-page/1/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"

    assert len(dirs) == 1
    assert "Next Page (2)" in dirs[0]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses categories."""
    html = """
    <html>
    <div class="box">
        <li><a href="/tags/milf/">MILF</a></li>
        <li><a href="/tags/amateur/">Amateur</a></li>
    </div>
    </html>
    """

    dirs = []

    monkeypatch.setattr(hdporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hdporn.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(hdporn.utils, "eod", lambda: None)

    hdporn.Cat("https://www.porn00.org/tags/")

    assert len(dirs) == 2
    assert "MILF" in dirs[0]
    assert "Amateur" in dirs[1]
