"""Comprehensive tests for cambro.tv site implementation."""
from pathlib import Path

from resources.lib.sites import cambro


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "cambro"


def load_fixture(name):
    """Load a fixture file from the cambro fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
            "duration": kwargs.get("duration"),
            "quality": kwargs.get("quality"),
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(cambro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should have 5 videos (excluding private item)
    assert len(downloads) == 5

    # Check first video - using data-original and title attribute
    assert downloads[0]["name"] == "Hot Blonde Teases on Cam"
    assert "/videos/hot-blonde-teases-123/" in downloads[0]["url"]
    assert downloads[0]["icon"] == "https://www.cambro.tv/images/thumbs/thumb1.jpg"
    assert downloads[0]["duration"] == "15:45"
    assert downloads[0]["quality"] == "HD"

    # Check second video - using data-src
    assert downloads[1]["name"] == "Brunette Webcam Show"
    assert "/videos/brunette-webcam-show-456/" in downloads[1]["url"]
    assert downloads[1]["icon"] == "https://www.cambro.tv/images/thumbs/thumb2.jpg"
    assert downloads[1]["duration"] == "22:30"
    assert downloads[1]["quality"] == "HD"

    # Check third video - using direct src and h3 title
    assert downloads[2]["name"] == "Redhead Cam Girl Performance"
    assert "/videos/redhead-cam-girl-789/" in downloads[2]["url"]
    assert downloads[2]["icon"] == "https://www.cambro.tv/images/thumbs/thumb3.jpg"
    assert downloads[2]["duration"] == "18:20"
    assert downloads[2]["quality"] == "HD"

    # Check fourth video - HD in text content
    assert downloads[3]["name"] == "Asian Babe Cam Session HD"
    assert "/videos/asian-babe-cam-321/" in downloads[3]["url"]
    assert downloads[3]["icon"] == "https://cambro.tv/images/thumbs/thumb4.jpg"
    assert downloads[3]["duration"] == "25:10"
    assert downloads[3]["quality"] == "HD"  # Detected from text

    # Check fifth video - minimal info, defaults to 'Video'
    assert downloads[4]["name"] == "Video"
    assert "/videos/hot-webcam-111/" in downloads[4]["url"]
    assert downloads[4]["duration"] == "12:45"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page (3/25)" in dirs[0]["name"]
    assert "/latest-updates/3/" in dirs[0]["url"]


def test_list_skips_private_items(monkeypatch):
    """Test that List correctly skips items with 'private' class."""
    html = """
    <div class="item">
        <a href="/videos/public-123/" title="Public Video">
            <img data-original="https://www.cambro.tv/images/thumbs/thumb1.jpg">
        </a>
    </div>
    <div class="item item-private">
        <a href="/videos/private-456/" title="Private Video">
            <img data-original="https://www.cambro.tv/images/thumbs/thumb2.jpg">
        </a>
    </div>
    <div class="item Private">
        <a href="/videos/private-789/" title="Private Video 2">
            <img data-original="https://www.cambro.tv/images/thumbs/thumb3.jpg">
        </a>
    </div>
    """

    downloads = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"name": name})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(cambro.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should only have 1 video (skipped 2 private items)
    assert len(downloads) == 1
    assert downloads[0]["name"] == "Public Video"


def test_list_handles_protocol_relative_urls(monkeypatch):
    """Test that List correctly handles protocol-relative URLs."""
    html = """
    <div class="item">
        <a href="/videos/test-123/">
            <img data-original="//cambro.tv/images/thumbs/test.jpg">
        </a>
    </div>
    """

    downloads = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"icon": iconimage})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(cambro.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    assert len(downloads) == 1
    assert downloads[0]["icon"] == "https://cambro.tv/images/thumbs/test.jpg"


def test_list_detects_hd_from_text(monkeypatch):
    """Test that List correctly detects HD quality from text content."""
    html = """
    <div class="item">
        <a href="/videos/test-123/" title="Test Video">
            <img data-original="https://www.cambro.tv/images/thumbs/test.jpg">
        </a>
        <div class="title">Test Video HD Quality</div>
    </div>
    """

    downloads = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"quality": kwargs.get("quality")})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(cambro.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    assert len(downloads) == 1
    assert downloads[0]["quality"] == "HD"


def test_list_deduplicates_videos(monkeypatch):
    """Test that List correctly deduplicates videos with same URL."""
    html = """
    <div class="item">
        <a href="/videos/duplicate-123/">
            <img data-original="https://www.cambro.tv/images/thumbs/dup1.jpg">
        </a>
    </div>
    <div class="item">
        <a href="/videos/duplicate-123/">
            <img data-original="https://www.cambro.tv/images/thumbs/dup2.jpg">
        </a>
    </div>
    """

    downloads = []

    def fake_get_html(url):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"url": url})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(cambro.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should only have one video despite duplicate
    assert len(downloads) == 1


def test_list_with_pagination(monkeypatch):
    """Test that List adds pagination correctly."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(cambro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should have next page link
    assert len(dirs) == 1
    assert "Next Page (3/25)" in dirs[0]["name"]
    assert "/latest-updates/3/" in dirs[0]["url"]


def test_list_pagination_without_last_page(monkeypatch):
    """Test that List handles pagination without last page link."""
    html = """
    <div class="item">
        <a href="/videos/test-123/" title="Test">
            <img data-original="https://www.cambro.tv/images/thumbs/test.jpg">
        </a>
    </div>
    <div class="pagination">
        <ul>
            <li class="next"><a href="/latest-updates/2/">Next</a></li>
        </ul>
    </div>
    """

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(cambro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should have next page without page number
    assert len(dirs) == 1
    assert "Next Page (2)" in dirs[0]["name"]


def test_list_handles_error_gracefully(monkeypatch):
    """Test that List handles HTTP errors gracefully."""
    notifications = []

    def fake_get_html(url):
        raise Exception("Connection timeout")

    def fake_notify(title, message):
        notifications.append((title, message))

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.utils, "notify", fake_notify)
    monkeypatch.setattr(cambro.utils, "kodilog", lambda x: None)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should notify user of error
    assert len(notifications) == 1
    assert notifications[0][0] == "Error"
    assert "Could not load page" in notifications[0][1]


def test_list_handles_empty_response(monkeypatch):
    """Test that List handles empty HTML response."""
    notifications = []

    def fake_get_html(url):
        return ""

    def fake_notify(title, message):
        notifications.append((title, message))

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.utils, "notify", fake_notify)

    cambro.List("https://www.cambro.tv/latest-updates/")

    # Should notify user of empty response
    assert len(notifications) == 1
    assert notifications[0][0] == "Error"
    assert "Empty response" in notifications[0][1]


def test_categories_parses_items(monkeypatch):
    """Test that Categories correctly parses category items."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
        })

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.Categories("https://www.cambro.tv/categories/")

    # Should have 5 categories
    assert len(dirs) == 5

    # Check first category - a.item style
    assert "Amateur" in dirs[0]["name"]
    assert "1,234" in dirs[0]["name"]
    assert "/categories/amateur/" in dirs[0]["url"]
    assert dirs[0]["icon"] == "https://www.cambro.tv/images/cats/amateur.jpg"

    # Check second category - div.item a style
    assert "Asian" in dirs[1]["name"]
    assert "567" in dirs[1]["name"]
    assert "/categories/asian/" in dirs[1]["url"]

    # Check third category
    assert "Anal" in dirs[2]["name"]
    assert "892" in dirs[2]["name"]

    # Check fourth category - protocol-relative URL
    assert "Bbw" in dirs[3]["name"]  # Title case applied
    assert "345" in dirs[3]["name"]
    assert dirs[3]["icon"] == "https://cambro.tv/images/cats/bbw.jpg"

    # Check fifth category - no video count
    assert "Latina" in dirs[4]["name"]
    assert "1,234" not in dirs[4]["name"]


def test_categories_deduplicates_items(monkeypatch):
    """Test that Categories correctly deduplicates category items."""
    html = """
    <a class="item" href="/categories/amateur/" title="Amateur">
        <img data-original="https://www.cambro.tv/images/cats/amateur.jpg">
        <div class="title">Amateur</div>
    </a>
    <div class="item">
        <a href="/categories/amateur/" title="Amateur">
            <img src="https://www.cambro.tv/images/cats/amateur2.jpg">
            <div class="title">Amateur</div>
        </a>
    </div>
    """

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.Categories("https://www.cambro.tv/categories/")

    # Should only have one category despite duplicate
    assert len(dirs) == 1
    assert "Amateur" in dirs[0]["name"]


def test_models_parses_items(monkeypatch):
    """Test that Models correctly parses model items."""
    html = load_fixture("models.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
        })

    monkeypatch.setattr(cambro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(cambro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(cambro.utils, "eod", lambda: None)

    cambro.Models("https://www.cambro.tv/models/1/")

    # Should have 3 models
    assert len(dirs) == 4  # 3 models + next page

    # Check first model
    assert "Alexis Texas" in dirs[0]["name"]
    assert "48" in dirs[0]["name"]
    assert "/models/alexis-texas/" in dirs[0]["url"]
    assert dirs[0]["icon"] == "https://www.cambro.tv/images/models/alexis.jpg"

    # Check second model
    assert "Mia Khalifa" in dirs[1]["name"]
    assert "62" in dirs[1]["name"]

    # Check third model
    assert "Riley Reid" in dirs[2]["name"]
    assert "135" in dirs[2]["name"]

    # Check pagination
    assert "Next Page" in dirs[3]["name"]
    assert "/models/3/" in dirs[3]["url"]


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(cambro.site, "search_dir", fake_search_dir)

    cambro.Search("https://www.cambro.tv/search/?q=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(cambro, "List", fake_list)

    cambro.Search("https://www.cambro.tv/search/?q=", keyword="test query")

    assert len(list_calls) == 1
    assert "test-query" in list_calls[0]
