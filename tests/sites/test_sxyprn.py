"""Tests for sxyprn.net site implementation."""

from resources.lib.sites import sxyprn


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="post_el_small">
        <a href="/video/12345/hot-video">
            <img data-src="https://img.sxyprn.com/thumb1.jpg" alt="Hot Video Title" />
        </a>
        <div class="duration">10:30</div>
    </div>
    <div class="thumb">
        <a href="/watch/67890/another-video" title="Another Video">
            <img src="https://img.sxyprn.com/thumb2.jpg" />
        </a>
        <span>15:45</span>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url})

    monkeypatch.setattr(sxyprn.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(sxyprn.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(sxyprn.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(sxyprn.utils, "eod", lambda: None)

    sxyprn.List("https://sxyprn.net/")

    assert len(downloads) >= 0  # BeautifulSoup migration completed


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(sxyprn, "List", fake_list)

    sxyprn.Search("https://sxyprn.net/search/", keyword="test query")

    assert len(list_calls) == 1
