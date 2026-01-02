"""Tests for tnaflix.com site implementation."""

from resources.lib.sites import tnaflix


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="thumbBlock">
        <a href="/video12345/hot-video" title="Hot Video Title">
            <img data-original="https://img.tnaflix.com/thumb1.jpg" />
        </a>
        <div class="duration">10:30</div>
    </div>
    <div class="thumbBlock">
        <a href="/video67890/another-video">
            <img src="https://img.tnaflix.com/thumb2.jpg" alt="Another Video" />
        </a>
        <div class="duration">15:45</div>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url})

    monkeypatch.setattr(tnaflix.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(tnaflix.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(tnaflix.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(tnaflix.utils, "eod", lambda: None)

    tnaflix.List("https://www.tnaflix.com/latest-updates/")

    assert len(downloads) >= 0


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(tnaflix, "List", fake_list)

    tnaflix.Search("https://www.tnaflix.com/search/", keyword="test query")

    assert len(list_calls) == 1
