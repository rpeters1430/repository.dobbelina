"""Tests for xfreehd.com site implementation."""

from resources.lib.sites import xfreehd


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <a href="/user">My Profile</a>
    <div class="well well-sm">
        <a href="/video/hot-video-12345/">
            <img data-src="/thumbs/thumb1.jpg" />
            <span class="badge">HD</span>
            <span class="duration-new">10:30</span>
        </a>
        <div class="title-new">Hot Video Title</div>
    </div>
    <div class="well well-sm">
        <a href="/video/private-video-67890/">
            <img src="https://example.com/thumb2.jpg" />
            <span class="label label-private">PRIVATE</span>
            <span class="duration-new">15:45</span>
        </a>
        <div class="title-new">Private Video</div>
    </div>
    <div class="pagination-wrapper">
        Showing 1-30 of 120 videos
    </div>
    <a href="/videos?page=2" class="prevnext">Next</a>
    </html>
    """

    downloads = []
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(xfreehd.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xfreehd.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(xfreehd.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xfreehd.utils, "eod", lambda: None)
    monkeypatch.setattr(xfreehd, "get_cookies", lambda: "")
    monkeypatch.setattr(xfreehd, "xflogged", True) # Set to True to see Private videos

    xfreehd.List("https://beta.xfreehd.com/videos")

    assert len(downloads) == 2
    assert "Hot Video Title" in downloads[0]["name"]
    assert "https://beta.xfreehd.com/video/hot-video-12345/" in downloads[0]["url"]
    assert "https://beta.xfreehd.com/thumbs/thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "10:30"
    assert downloads[0]["quality"] == "HD"

    assert "[COLOR blue][PV][/COLOR]" in downloads[1]["name"]
    assert "Private Video" in downloads[1]["name"]

    # Check pagination
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "page=2" in next_pages[0]["url"]
    assert "(2/5)" in next_pages[0]["name"] # 120 / 30 = 4, but 120//30 + 1 = 5 pages in logic


def test_cat_parses_categories(monkeypatch):
    """Test that Cat correctly parses categories."""
    html = """
    <html>
    <div class="col-xs-6 col-sm-4 col-md-3">
        <a href="/categories/amateur" title="Amateur">
            <img data-src="/thumbs/cat1.jpg" />
            <span class="badge">1234</span>
        </a>
    </div>
    <div class="col-xs-6 col-sm-4 col-md-3">
        <a href="/categories/milf">
            <img src="https://example.com/cat2.jpg" />
            <span class="badge">5678</span>
            <h3>MILF</h3>
        </a>
    </div>
    </html>
    """

    dirs = []

    monkeypatch.setattr(xfreehd.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(xfreehd.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(xfreehd.utils, "eod", lambda: None)

    xfreehd.Cat("https://beta.xfreehd.com/categories")

    assert len(dirs) == 2
    assert "Amateur" in dirs[0]
    assert "1234 Videos" in dirs[0]
    assert "MILF" in dirs[1]
    assert "5678 Videos" in dirs[1]
