"""Tests for hitprn.com site implementation."""

from resources.lib.sites import hitprn


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items."""
    html = """
    <html>
    <article class="thumb-block">
        <a href="/video/hot-video/" title="Hot Video Title">
            <img class="video-main-thumb" src="/thumbs/1.jpg" />
        </a>
    </article>
    <div class="pagination">
        <ul>
            <li><a class="current">1</a></li>
            <li><a href="/page/2/">Next</a></li>
        </ul>
    </div>
    </html>
    """

    downloads = []
    dirs = []

    monkeypatch.setattr(hitprn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        hitprn.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(hitprn.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(hitprn.utils, "eod", lambda: None)

    hitprn.List("https://www.hitprn.com/")

    assert len(downloads) == 1
    assert downloads[0] == "Hot Video Title"

    assert len(dirs) == 1
    assert "Next Page... (2)" in dirs[0]


def test_sites_parses_options(monkeypatch):
    """Test that Sites correctly parses site options."""
    html = """
    <html>
    <select>
        <option class="level-0" value="123">Site 1</option>
        <option class="level-1" value="456">&nbsp;&nbsp;&nbsp;Site 2</option>
    </select>
    </html>
    """

    dirs = []

    monkeypatch.setattr(hitprn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hitprn.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(hitprn.utils, "eod", lambda: None)

    hitprn.Sites("https://www.hitprn.com/")

    assert len(dirs) == 2
    assert "Site 1" in dirs[0]
    assert "- Site 2" in dirs[1]
