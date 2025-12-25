"""Tests for peachurnet.com site implementation."""

from pathlib import Path

from resources.lib.sites import peachurnet


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "peachurnet"


def load_fixture(name):
    """Load a fixture file from the peachurnet fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_cache_homepage_metadata_extracts_navigation(monkeypatch):
    """Test that homepage caching extracts navigation sections."""
    html = load_fixture("homepage.html")

    def fake_get_html(url, headers=None):
        return html

    monkeypatch.setattr(peachurnet.utils, "getHtml", fake_get_html)

    # Clear cache before test
    peachurnet.HOME_CACHE["sections"] = None
    peachurnet.HOME_CACHE["search"] = None

    peachurnet._cache_homepage_metadata()

    # Check that sections were extracted
    sections = peachurnet.HOME_CACHE["sections"]
    assert sections is not None
    assert len(sections) >= 3

    # Check that common navigation items are captured
    section_labels = [label for label, url in sections]
    assert any("Amateur" in label for label in section_labels)
    assert any("MILF" in label for label in section_labels)
    assert any("Teen" in label for label in section_labels)

    # Check search endpoint was discovered
    search_url = peachurnet.HOME_CACHE["search"]
    assert search_url is not None
    assert "search" in search_url
    assert "q=" in search_url


def test_list_parses_video_cards(monkeypatch):
    """Test that List correctly parses video cards from HTML."""
    html = load_fixture("homepage.html")

    downloads = []
    dirs = []

    def fake_get_html(url, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(peachurnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(peachurnet.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(peachurnet.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(peachurnet.utils, "eod", lambda: None)

    peachurnet.List("https://peachurnet.com/en")

    assert len(downloads) == 2

    # Check first video
    assert downloads[0]["name"] == "Sample Video One"
    assert "/video/sample-video-one" in downloads[0]["url"]
    assert downloads[0]["icon"] == "https://peachurnet.com/thumbs/thumb1.jpg"
    assert "15:30" in downloads[0]["desc"]

    # Check second video (with lazy-loaded thumbnail)
    assert downloads[1]["name"] == "Sample Video Two"
    assert "/video/sample-video-two" in downloads[1]["url"]
    assert downloads[1]["icon"] == "https://peachurnet.com/thumbs/thumb2.jpg"
    assert "22:45" in downloads[1]["desc"]

    # Check pagination
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "/en?page=2" in next_pages[0]["url"]


def test_list_handles_empty_results(monkeypatch):
    """Test that List handles pages with no videos."""
    html = load_fixture("empty_listing.html")

    downloads = []
    notified = []

    def fake_get_html(url, headers=None):
        return html

    def fake_notify(site, msg):
        notified.append(msg)

    monkeypatch.setattr(peachurnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        peachurnet.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(peachurnet.utils, "notify", fake_notify)
    monkeypatch.setattr(peachurnet.utils, "eod", lambda: None)

    peachurnet.List("https://peachurnet.com/en/search?q=nonexistent")

    assert len(downloads) == 0
    assert any("No videos found" in msg for msg in notified)


def test_parse_video_cards_deduplicates(monkeypatch):
    """Test that _parse_video_cards deduplicates videos."""
    html = """
    <html>
        <a href="/video/duplicate-video">
            <div class="title">Duplicate Video</div>
        </a>
        <a href="/video/duplicate-video">
            <div class="title">Duplicate Video</div>
        </a>
        <a href="/video/unique-video">
            <div class="title">Unique Video</div>
        </a>
    </html>
    """

    soup = peachurnet.utils.parse_html(html)
    cards = peachurnet._parse_video_cards(soup)

    # Should only have 2 unique videos
    assert len(cards) == 2
    urls = [card["url"] for card in cards]
    assert len(set(urls)) == 2  # All unique


def test_gather_video_sources_finds_multiple_sources(monkeypatch):
    """Test that _gather_video_sources extracts all available sources."""
    html = load_fixture("video_page.html")

    sources = peachurnet._gather_video_sources(
        html, "https://peachurnet.com/en/video/sample"
    )

    # Should find multiple video sources
    assert len(sources) > 0

    # Check that it found MP4 sources (M3U8 may be in JS, not always in HTML tags)
    all_urls = list(sources.values())
    assert any(".mp4" in url.lower() or ".m3u8" in url.lower() for url in all_urls)


def test_extract_thumbnail_with_fallbacks():
    """Test _extract_thumbnail with various fallback strategies."""
    # Test with data-src
    html1 = '<a><img data-src="https://example.com/thumb1.jpg" /></a>'
    soup1 = peachurnet.utils.parse_html(html1)
    link1 = soup1.select_one("a")
    thumb1 = peachurnet._extract_thumbnail(link1)
    assert thumb1 == "https://example.com/thumb1.jpg"

    # Test with regular src
    html2 = '<a><img src="https://example.com/thumb2.jpg" /></a>'
    soup2 = peachurnet.utils.parse_html(html2)
    link2 = soup2.select_one("a")
    thumb2 = peachurnet._extract_thumbnail(link2)
    assert thumb2 == "https://example.com/thumb2.jpg"

    # Test with style background
    html3 = '<a style="background-image: url(https://example.com/thumb3.jpg)"></a>'
    soup3 = peachurnet.utils.parse_html(html3)
    link3 = soup3.select_one("a")
    thumb3 = peachurnet._extract_thumbnail(link3)
    assert thumb3 == "https://example.com/thumb3.jpg"


def test_extract_duration_from_various_sources():
    """Test _extract_duration with data attributes and CSS classes."""
    # Test with data-duration attribute
    html1 = '<a data-duration="12:34"><div class="title">Video</div></a>'
    soup1 = peachurnet.utils.parse_html(html1)
    link1 = soup1.select_one("a")
    duration1 = peachurnet._extract_duration(link1)
    assert duration1 == "12:34"

    # Test with duration class
    html2 = '<a><div class="title">Video</div><span class="duration">25:45</span></a>'
    soup2 = peachurnet.utils.parse_html(html2)
    link2 = soup2.select_one("a")
    duration2 = peachurnet._extract_duration(link2)
    assert duration2 == "25:45"


def test_find_next_page_with_various_selectors():
    """Test _find_next_page finds pagination with multiple selector strategies."""
    # Test with rel="next"
    html1 = '<html><a rel="next" href="/page/2">Next</a></html>'
    soup1 = peachurnet.utils.parse_html(html1)
    next1 = peachurnet._find_next_page(soup1, "https://peachurnet.com/en")
    assert "/page/2" in next1

    # Test with aria-label
    html2 = '<html><a aria-label="Next Page" href="/page/3">›</a></html>'
    soup2 = peachurnet.utils.parse_html(html2)
    next2 = peachurnet._find_next_page(soup2, "https://peachurnet.com/en")
    assert "/page/3" in next2

    # Test with text matching
    html3 = '<html><a href="/page/4">Next</a></html>'
    soup3 = peachurnet.utils.parse_html(html3)
    next3 = peachurnet._find_next_page(soup3, "https://peachurnet.com/en")
    assert "/page/4" in next3


def test_search_builds_search_url(monkeypatch):
    """Test that Search builds correct search URL."""
    # Pre-populate cache to avoid HTTP call
    peachurnet.HOME_CACHE["search"] = "https://peachurnet.com/en/search?q="
    peachurnet.HOME_CACHE["sections"] = []

    called_urls = []

    def fake_list(url):
        called_urls.append(url)

    monkeypatch.setattr(peachurnet, "List", fake_list)

    peachurnet.Search("https://peachurnet.com/en/search", keyword="test query")

    assert len(called_urls) == 1
    assert "test+query" in called_urls[0]


def test_absolute_url_normalization():
    """Test _absolute_url handles various URL formats."""
    # Protocol-relative URL
    assert (
        peachurnet._absolute_url("//cdn.example.com/video.mp4")
        == "https://cdn.example.com/video.mp4"
    )

    # Absolute URL (no change)
    assert (
        peachurnet._absolute_url("https://example.com/video")
        == "https://example.com/video"
    )

    # Relative URL
    result = peachurnet._absolute_url("/videos/123", "https://peachurnet.com/")
    assert result == "https://peachurnet.com/videos/123"

    # Empty URL
    assert peachurnet._absolute_url("") == ""
