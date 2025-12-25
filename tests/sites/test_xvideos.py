"""Comprehensive tests for xvideos.com site implementation."""

from pathlib import Path

from resources.lib.sites import xvideos


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "xvideos"


def load_fixture(name):
    """Load a fixture file from the xvideos fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_thumbs(monkeypatch):
    """Test that List correctly parses div.thumb-block video items."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "icon": iconimage,
                "desc": desc,
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(xvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xvideos.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(xvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xvideos.utils, "eod", lambda: None)

    xvideos.List("https://www.xvideos.com/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (with title from p.title a)
    assert downloads[0]["name"] == "Hot Teen Video"
    assert "/video12345/hot_teen_video" in downloads[0]["url"]
    assert (
        downloads[0]["icon"]
        == "https://img-hw.xvideos-cdn.com/videos/thumbs/thumb1.jpg"
    )
    assert downloads[0]["duration"] == "12:34"
    assert downloads[0]["quality"] == "HD"
    # Metadata should not include duration (it's stripped)
    assert "95%" in downloads[0]["desc"]
    assert "1.2M views" in downloads[0]["desc"]

    # Check second video (data-mediumthumb)
    assert downloads[1]["name"] == "MILF Action"
    assert (
        downloads[1]["icon"]
        == "https://img-hw.xvideos-cdn.com/videos/thumbs/thumb2.jpg"
    )
    assert downloads[1]["duration"] == "25:45"
    assert downloads[1]["quality"] == "720P"

    # Check third video (title from a tag, src fallback)
    assert downloads[2]["name"] == "Premium Content"
    assert (
        downloads[2]["icon"]
        == "https://img-hw.xvideos-cdn.com/videos/thumbs/thumb3.jpg"
    )


def test_list_pagination(monkeypatch):
    """Test that List correctly handles pagination."""
    html = load_fixture("listing.html")

    dirs = []

    def fake_get_html(url, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(xvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xvideos.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(xvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xvideos.utils, "eod", lambda: None)

    xvideos.List("https://www.xvideos.com/")

    # Should have Next Page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    # Should show page number and total pages (incremented by 1 from link)
    assert "(3/50)" in next_pages[0]["name"]
    # When on homepage, /2 gets replaced with /1
    assert "/videos/1" in next_pages[0]["url"] or "/videos/2" in next_pages[0]["url"]


def test_list_handles_no_results(monkeypatch):
    """Test that List shows 'Clear filters' when no videos found."""
    html = load_fixture("no_results.html")

    downloads = []
    dirs = []

    def fake_get_html(url, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(xvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        xvideos.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(xvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xvideos.utils, "eod", lambda: None)

    xvideos.List("https://www.xvideos.com/?k=nonexistent")

    # Should have no videos
    assert len(downloads) == 0

    # Should have "Clear filters" option
    no_results = [d for d in dirs if "No videos found" in d["name"]]
    assert len(no_results) == 1
    assert "Clear all filters" in no_results[0]["name"]
    assert no_results[0]["mode"] == "ResetFilters"


def test_categories_parsing(monkeypatch):
    """Test that Categories parses category listings."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(xvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xvideos.utils, "eod", lambda: None)

    xvideos.Categories("https://www.xvideos.com/")

    # Should have 3 categories
    assert len(dirs) == 3

    # Categories are sorted alphabetically
    category_names = [d["name"] for d in dirs]

    # Check all categories are present (sorted: Amateur, MILF, Teen)
    assert any("Amateur" in name for name in category_names)
    assert any("MILF" in name for name in category_names)
    assert any("Teen" in name for name in category_names)

    # Check that it's alphabetically sorted
    assert "Amateur" in dirs[0]["name"]  # A comes first
    assert "MILF" in dirs[1]["name"]  # M comes second
    assert "Teen" in dirs[2]["name"]  # T comes third


def test_pornstars_parsing(monkeypatch):
    """Test that Pornstars parses pornstar listings."""
    html = load_fixture("pornstars.html")

    dirs = []

    def fake_get_html(url, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(xvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xvideos.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xvideos.utils, "eod", lambda: None)

    xvideos.Pornstars("https://www.xvideos.com/pornstars-index/")

    # Should have 3 pornstars
    assert len(dirs) == 3

    # Check pornstar names
    assert "Alexis Texas" in dirs[0]["name"]
    assert "245" in dirs[0]["name"]

    assert "Mia Malkova" in dirs[1]["name"]
    assert "189" in dirs[1]["name"]

    assert "Lisa Ann" in dirs[2]["name"]
    assert "312" in dirs[2]["name"]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(xvideos.site, "search_dir", fake_search_dir)

    xvideos.Search("https://www.xvideos.com/?typef=straight&k=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(xvideos, "List", fake_list)

    xvideos.Search("https://www.xvideos.com/?typef=straight&k=", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]


def test_playvid_initializes_video_player(monkeypatch):
    """Test that Playvid initializes VideoPlayer."""
    vp_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download, regex):
            vp_calls.append(("init", name, download, regex))

        def play_from_site_link(self, url):
            vp_calls.append(("play", url))

    monkeypatch.setattr(xvideos.utils, "VideoPlayer", FakeVideoPlayer)

    xvideos.Playvid("https://www.xvideos.com/video12345/test", "Test Video")

    assert len(vp_calls) == 2
    assert vp_calls[0][0] == "init"
    assert vp_calls[0][1] == "Test Video"
    assert vp_calls[1] == ("play", "https://www.xvideos.com/video12345/test")


def test_list_metadata_parsing(monkeypatch):
    """Test that List correctly extracts and formats metadata."""
    html = """
    <html>
    <div class="thumb-block">
        <a href="/video123/test" title="Test Video">
            <img data-src="test.jpg">
        </a>
        <div class="thumb-under">
            <div class="duration">10:00</div>
            <div class="metadata">10:00 - 98% - 2.5M views - Trending</div>
        </div>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"desc": desc, "duration": kwargs.get("duration", "")})

    monkeypatch.setattr(xvideos.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xvideos.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(xvideos.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(xvideos.utils, "eod", lambda: None)

    xvideos.List("https://www.xvideos.com/")

    assert len(downloads) == 1
    # Duration should be extracted
    assert downloads[0]["duration"] == "10:00"
    # Metadata should have duration trimmed and be formatted with bullets
    assert "98%" in downloads[0]["desc"]
    assert "2.5M views" in downloads[0]["desc"]
    assert "Trending" in downloads[0]["desc"]
    # Duration should NOT appear twice
    assert downloads[0]["desc"].count("10:00") == 0
