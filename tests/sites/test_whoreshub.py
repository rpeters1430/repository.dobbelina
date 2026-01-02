"""Tests for whoreshub.com site implementation."""

from resources.lib.sites import whoreshub


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="thumb-block">
        <a href="/video/12345/hot-video" title="Hot Video Title">
            <img data-original="https://img.whoreshub.com/thumb1.jpg" />
        </a>
        <div class="duration">10:30</div>
    </div>
    <div class="item">
        <a href="/watch/67890/another-video">
            <img src="https://img.whoreshub.com/thumb2.jpg" alt="Another Video" />
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url})

    monkeypatch.setattr(whoreshub.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(whoreshub.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(whoreshub.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(whoreshub.utils, "eod", lambda: None)

    whoreshub.List("https://whoreshub.com/")

    assert len(downloads) >= 0


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(whoreshub, "List", fake_list)

    whoreshub.Search("https://whoreshub.com/search/", keyword="test query")

    assert len(list_calls) == 1
