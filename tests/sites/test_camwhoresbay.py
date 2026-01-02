"""Tests for camwhoresbay.com site implementation."""

from resources.lib.sites import camwhoresbay


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="video-item">
        <a href="/videos/12345/hot-cam-show/" title="Hot Cam Show">
            <img data-original="https://img.cwb.com/thumb1.jpg" />
        </a>
        <div class="duration">15:30</div>
        <div class="ico_hd">HD</div>
    </div>
    <div class="video-item">
        <a href="/videos/67890/private-show/" title="Private Show">
            <img data-src="//img.cwb.com/thumb2.jpg" />
        </a>
        <div class="clock">20:45</div>
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
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        )

    def fake_get_cookies():
        return "kt_tcookie=1"

    monkeypatch.setattr(camwhoresbay.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(camwhoresbay.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(camwhoresbay.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(camwhoresbay.utils, "eod", lambda: None)
    monkeypatch.setattr(camwhoresbay, "get_cookies", fake_get_cookies)

    camwhoresbay.List("https://www.camwhoresbay.com/latest-updates/", 1)

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Cam Show"
    assert "/videos/12345/hot-cam-show/" in downloads[0]["url"]
    assert downloads[0]["duration"] == "15:30"
    assert downloads[0]["quality"] == "HD"


def test_list_handles_private_videos(monkeypatch):
    """Test that List skips private videos when not logged in."""
    html = """
    <html>
    <div class="video-item private">
        <a href="/videos/123/private/" title="Private Video">
            <img src="thumb.jpg" />
        </a>
    </div>
    <div class="video-item">
        <a href="/videos/456/public/" title="Public Video">
            <img src="thumb2.jpg" />
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, *args, **kwargs):
        downloads.append(name)

    monkeypatch.setattr(camwhoresbay.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(camwhoresbay.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(camwhoresbay.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(camwhoresbay.utils, "eod", lambda: None)
    monkeypatch.setattr(camwhoresbay, "get_cookies", lambda: "kt_tcookie=1")
    monkeypatch.setattr(camwhoresbay, "cblogged", False)

    camwhoresbay.List("https://www.camwhoresbay.com/latest-updates/", 1)

    # Only public video should be added
    assert len(downloads) == 1
    assert "Public Video" in downloads[0]


def test_categories_parses_correctly(monkeypatch):
    """Test that Categories function parses categories."""
    html = """
    <html>
    <a class="item" href="/categories/amateur/">
        <img data-original="thumb1.jpg" />
        <div class="title">Amateur</div>
        <div class="videos">1234 videos</div>
    </a>
    <div class="item">
        <a href="/categories/lesbian/">
            <img src="thumb2.jpg" />
            <div class="title">Lesbian</div>
            <div class="count">567</div>
        </a>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage, *args, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(camwhoresbay.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(camwhoresbay.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(camwhoresbay.utils, "eod", lambda: None)

    camwhoresbay.Categories("https://www.camwhoresbay.com/categories/")

    assert len(dirs) >= 2
    # Check that amateur category is found
    amateur = [d for d in dirs if "Amateur" in d["name"]]
    assert len(amateur) >= 1


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with formatted URL."""
    list_calls = []

    def fake_list(url, *args):
        list_calls.append(url)

    monkeypatch.setattr(camwhoresbay, "List", fake_list)

    camwhoresbay.Search("https://www.camwhoresbay.com/search/{0}/", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(camwhoresbay.site, "search_dir", fake_search_dir)

    camwhoresbay.Search("https://www.camwhoresbay.com/search/{0}/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"
