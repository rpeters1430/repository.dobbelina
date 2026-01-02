"""Tests for porngo.com site implementation."""

from resources.lib.sites import porngo


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="thumb item">
        <a class="thumb__top" href="/video/12345/hot-video">
            <div class="thumb__img">
                <img data-src="https://img.porngo.com/thumb1.jpg" alt="Hot Video Title" />
            </div>
        </a>
        <div class="thumb__title"><span>Hot Video Title</span></div>
        <div class="thumb__duration">10:30</div>
        <div class="thumb__badge">1080p</div>
    </div>
    <div class="thumb item">
        <a class="thumb__top" href="/video/67890/another-video" title="Another Video">
            <img src="https://img.porngo.com/thumb2.jpg" />
        </a>
        <div class="thumb__title">Another Video</div>
        <div class="thumb__duration">15:45</div>
        <div class="thumb__bage">720p</div>
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

    monkeypatch.setattr(porngo.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(porngo.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(porngo.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(porngo.utils, "eod", lambda: None)

    porngo.List("https://www.porngo.com/latest-updates/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Video Title"
    assert "https://www.porngo.com/video/12345/hot-video" in downloads[0]["url"]
    assert downloads[0]["duration"] == "10:30"
    assert downloads[0]["quality"] == "FHD "

    assert downloads[1]["name"] == "Another Video"
    assert downloads[1]["duration"] == "15:45"
    assert downloads[1]["quality"] == "HD "


def test_list_pagination(monkeypatch):
    """Test that List handles pagination correctly."""
    html = """
    <html>
    <div class="thumbs-list">
        <div class="thumb item">
            <a class="thumb__top" href="/video/123/test">
                <img alt="Test" />
            </a>
            <div class="thumb__title">Test</div>
        </div>
    </div>
    <div class="pagination">
        <a class="pagination__link" href="/2/">next</a>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(porngo.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(porngo.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(porngo.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(porngo.utils, "eod", lambda: None)

    porngo.List("https://www.porngo.com/latest-updates/")

    next_pages = [d for d in dirs if "Next" in d["name"]]
    assert len(next_pages) == 1
    assert "https://www.porngo.com/2/" in next_pages[0]["url"]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat function parses category listings."""
    html = """
    <html>
    <div class="letter-block__item">
        <a class="letter-block__link" href="/categories/amateur">
            <span>Amateur</span>
        </a>
    </div>
    <div class="letter-block__item">
        <a class="letter-block__link" href="/categories/milf">
            <span>MILF</span>
        </a>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(porngo.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(porngo.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(porngo.utils, "eod", lambda: None)

    porngo.Cat("https://www.porngo.com/categories/")

    assert len(dirs) == 2
    assert "Amateur" in dirs[0]["name"]
    assert "https://www.porngo.com/categories/amateur" in dirs[0]["url"]
    assert "MILF" in dirs[1]["name"]


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(porngo, "List", fake_list)

    porngo.Search("https://www.porngo.com/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
