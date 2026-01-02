"""Tests for drtuber.com site implementation."""

from resources.lib.sites import drtuber


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <a class="th" href="/video/12345/hot-video">
        <img src="https://img.drtuber.com/thumb1.jpg" alt="Hot Video Title" />
        <div class="time_thumb"><em>10:30</em></div>
        <div class="ico_hd">HD</div>
    </a>
    <a class="th" href="/video/67890/another-video">
        <img data-src="https://img.drtuber.com/thumb2.jpg" alt="Another Video" />
        <div class="time_thumb"><em>15:45</em></div>
    </a>
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

    monkeypatch.setattr(drtuber.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(drtuber.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(drtuber.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(drtuber.utils, "eod", lambda: None)

    drtuber.List("https://www.drtuber.com/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Video Title"
    assert "https://www.drtuber.com/video/12345/hot-video" in downloads[0]["url"]
    assert downloads[0]["duration"] == "10:30"
    assert downloads[0]["quality"] == "HD"

    assert downloads[1]["name"] == "Another Video"
    assert downloads[1]["duration"] == "15:45"


def test_list_pagination(monkeypatch):
    """Test that List handles pagination correctly."""
    html = """
    <html>
    <a class="th" href="/video/123/test">
        <img alt="Test" /><div class="time_thumb"><em>5:00</em></div>
    </a>
    <a class="next" href="/page/2/">Next</a>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(drtuber.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(drtuber.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(drtuber.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(drtuber.utils, "eod", lambda: None)

    drtuber.List("https://www.drtuber.com/")

    next_pages = [d for d in dirs if "Next" in d["name"]]
    assert len(next_pages) == 1
    assert "https://www.drtuber.com/page/2/" in next_pages[0]["url"]


def test_cat_parses_categories(monkeypatch):
    """Test that Cat function parses category listings."""
    html = """
    <html>
    <li class="item">
        <a href="/categories/amateur">
            <span>Amateur</span>
            <b>1234 videos</b>
        </a>
    </li>
    <li class="item">
        <a href="/categories/milf">
            <span>MILF</span>
            <b>5678 videos</b>
        </a>
    </li>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(drtuber.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(drtuber.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(drtuber.utils, "eod", lambda: None)

    drtuber.Cat("https://www.drtuber.com/categories/")

    assert len(dirs) == 2
    # Sorted alphabetically
    assert "Amateur" in dirs[0]["name"]
    assert "1234 videos" in dirs[0]["name"]
    assert "MILF" in dirs[1]["name"]
    assert "5678 videos" in dirs[1]["name"]


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(drtuber, "List", fake_list)

    drtuber.Search("https://www.drtuber.com/search/videos/", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
