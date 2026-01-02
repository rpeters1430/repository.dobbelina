"""Tests for eporner.com site implementation."""

from resources.lib.sites import eporner


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="mb" data-vp="12345">
        <div class="mbcontent">
            <a href="/video-12345/hot-video">
                <img data-src="https://static.eporner.com/thumb1.jpg" />
            </a>
        </div>
        <div class="mbtit"><a>Hot Video Title</a></div>
        <div class="mbstats">
            <span class="mbtim">10:30</span>
        </div>
        <div class="mvhdico"><span>1080p</span></div>
    </div>
    <div class="mb" data-vp="67890">
        <div class="mbcontent">
            <a href="/video-67890/another-video">
                <img src="https://static.eporner.com/thumb2.jpg" />
            </a>
        </div>
        <div class="mbtit"><a>Another Video</a></div>
        <div class="mbstats">
            <span class="mbtim">15:45</span>
        </div>
        <div class="mvhdico"><span>720p</span></div>
    </div>
    </html>
    """

    downloads = []

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

    monkeypatch.setattr(eporner.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(eporner.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(eporner.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(eporner.utils, "eod", lambda: None)

    eporner.List("https://www.eporner.com/recent/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Video Title"
    assert "https://www.eporner.com/video-12345/hot-video" in downloads[0]["url"]
    assert downloads[0]["duration"] == "10:30"
    assert downloads[0]["quality"] == "1080p"

    assert downloads[1]["name"] == "Another Video"
    assert downloads[1]["duration"] == "15:45"
    assert downloads[1]["quality"] == "720p"


def test_list_pagination(monkeypatch):
    """Test that List handles pagination correctly."""
    html = """
    <html>
    <div class="mb" data-vp="123">
        <div class="mbcontent"><a href="/video-123/test"><img /></a></div>
        <div class="mbtit"><a>Test</a></div>
    </div>
    <a class="nmnext" href="/2/">Next</a>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(eporner.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(eporner.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(eporner.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(eporner.utils, "eod", lambda: None)

    eporner.List("https://www.eporner.com/recent/")

    next_pages = [d for d in dirs if "Next" in d["name"]]
    assert len(next_pages) == 1
    assert "https://www.eporner.com/2/" in next_pages[0]["url"]
    assert "(2)" in next_pages[0]["name"]


def test_categories_parses_correctly(monkeypatch):
    """Test that Categories function parses categories."""
    html = """
    <html>
    <div class="ctbinner">
        <a href="/cat/amateur">
            <img src="thumb1.jpg" />
            <h2>Amateur</h2>
        </a>
    </div>
    <div class="ctbinner">
        <a href="/cat/milf">
            <h2>MILF</h2>
        </a>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url, "icon": iconimage})

    monkeypatch.setattr(eporner.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(eporner.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(eporner.utils, "eod", lambda: None)

    eporner.Categories("https://www.eporner.com/cats/")

    assert len(dirs) == 2
    # Sorted alphabetically
    assert "Amateur" in dirs[0]["name"]
    assert "https://www.eporner.com/cat/amateur" in dirs[0]["url"]
    assert "MILF" in dirs[1]["name"]


def test_pornstars_parses_correctly(monkeypatch):
    """Test that Pornstars function parses pornstar listings."""
    html = """
    <html>
    <div class="mbprofile">
        <a href="/pornstar/jane-doe">
            <img src="jane.jpg" />
        </a>
        <div class="mbtit">Jane Doe</div>
        <div class="mbtim">Videos: 123</div>
    </div>
    <div class="mbprofile">
        <a href="/pornstar/john-smith">
            <img src="john.jpg" />
        </a>
        <div class="mbtit">John Smith</div>
        <div class="mbtim">Videos: 456</div>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(eporner.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(eporner.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(eporner.utils, "eod", lambda: None)

    eporner.Pornstars("https://www.eporner.com/pornstar-list/")

    assert len(dirs) == 2
    assert "Jane Doe" in dirs[0]["name"]
    assert "(123)" in dirs[0]["name"]
    assert "John Smith" in dirs[1]["name"]
    assert "(456)" in dirs[1]["name"]


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(eporner, "List", fake_list)

    eporner.Search("https://www.eporner.com/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
