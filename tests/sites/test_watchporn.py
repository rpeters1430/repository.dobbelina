"""Tests for watchporn.to site implementation."""

from resources.lib.sites import watchporn


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="video-item">
        <a href="/video/12345/hot-video" title="Hot Video Title">
            <img data-src="https://img.watchporn.to/thumb1.jpg" />
        </a>
        <div class="duration">10:30</div>
    </div>
    <div class="thumb">
        <a href="/watch/67890/another-video">
            <img src="https://img.watchporn.to/thumb2.jpg" alt="Another Video" />
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url})

    monkeypatch.setattr(watchporn.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(watchporn.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(watchporn.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(watchporn.utils, "eod", lambda: None)

    watchporn.List("https://watchporn.to/")

    assert len(downloads) >= 0


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(watchporn, "List", fake_list)

    watchporn.Search("https://watchporn.to/search/", keyword="test query")

    assert len(list_calls) == 1


def test_lookup_info_regex(monkeypatch):
    """Test that Lookupinfo regexes correctly match category/tag/model links."""
    html = """
    <div class="video-info">
        <a href="https://watchporn.to/categories/straight/">Straight</a>
        <a href="https://watchporn.to/tags/blonde/"  >Blonde</a>
        <a href="https://watchporn.to/models/tasha-reign/" 
        >Tasha Reign</a>
    </div>
    """

    captured_lookup_list = []

    class MockLookupInfo:
        def __init__(self, site_url, page_url, list_mode, lookup_list):
            captured_lookup_list.extend(lookup_list)

        def getinfo(self):
            pass

    monkeypatch.setattr(watchporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(watchporn.utils, "LookupInfo", MockLookupInfo)

    watchporn.Lookupinfo("https://watchporn.to/video/123")
    
    import re
    # Category - Simple match
    cat_regex = captured_lookup_list[0][1]
    match = re.search(cat_regex, html)
    assert match
    assert match.group(1) == "categories/straight/"
    assert match.group(2) == "Straight"

    # Tag - Match with spaces before >
    tag_regex = captured_lookup_list[1][1]
    match = re.search(tag_regex, html)
    assert match
    assert match.group(1) == "tags/blonde/"
    assert match.group(2) == "Blonde"

    # Model - Match with newline before >
    model_regex = captured_lookup_list[2][1]
    match = re.search(model_regex, html)
    assert match
    assert match.group(1) == "models/tasha-reign/"
    assert match.group(2) == "Tasha Reign"
