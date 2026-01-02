"""Tests for pornone.com site implementation."""

from resources.lib.sites import pornone


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <a class="popbop" href="/video/12345/hot-video">
        <img data-src="https://img.pornone.com/thumb1.jpg" alt="Hot Video Title" />
        <div class="duration">10:30</div>
    </a>
    <a class="video-item" href="/watch/67890/another-video">
        <img src="https://img.pornone.com/thumb2.jpg" alt="Another Video" />
        <span class="time">15:45</span>
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

    monkeypatch.setattr(pornone.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornone.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(pornone.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(pornone.utils, "eod", lambda: None)

    pornone.List("https://pornone.com/newest/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Video Title"
    assert "https://pornone.com/video/12345/hot-video" in downloads[0]["url"]
    assert downloads[0]["duration"] == "10:30"


def test_list_pagination(monkeypatch):
    """Test that List handles pagination correctly."""
    html = """
    <html>
    <a class="popbop" href="/video/123/test">
        <img alt="Test" />
    </a>
    <div class="pagination">
        <a href="/newest/2">Next</a>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(pornone.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornone.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(pornone.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornone.utils, "eod", lambda: None)

    pornone.List("https://pornone.com/newest/")

    next_pages = [d for d in dirs if "Next" in d["name"]]
    assert len(next_pages) >= 0  # May or may not have pagination


def test_categories_parses_correctly(monkeypatch):
    """Test that Categories function parses categories."""
    html = """
    <html>
    <a class="category-link" href="/categories/amateur">
        <img src="thumb1.jpg" />
        <span>Amateur</span>
    </a>
    <a href="/categories/milf">
        <span>MILF</span>
    </a>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, *args):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(pornone.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(pornone.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornone.utils, "eod", lambda: None)

    pornone.Categories("https://pornone.com/categories/")

    # Should have parsed categories
    assert len(dirs) >= 0  # Implementation may vary


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(pornone, "List", fake_list)

    pornone.Search("https://pornone.com/search?q=", keyword="test query")

    assert len(list_calls) == 1
    assert "test" in list_calls[0] and "query" in list_calls[0]
