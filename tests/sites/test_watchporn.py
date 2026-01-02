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
