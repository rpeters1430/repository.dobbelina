"""Tests for hqporner.com site implementation."""

from resources.lib.sites import hqporner


def test_hqlist_parses_videos(monkeypatch):
    """Test that HQLIST correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <section class="box feature">
        <a class="image featured" href="/hdporn/hot-video-12345/">
            <img src="//thumb.hqporner.com/thumb1.jpg" />
        </a>
        <div class="meta-data-title"><a>Hot Video Title</a></div>
        <span class="icon fa-clock-o">10:30</span>
    </section>
    <section class="box feature">
        <a class="image featured" href="/hdporn/another-video-67890/">
            <img src="https://thumb.hqporner.com/thumb2.jpg" />
        </a>
        <div class="meta-data-title"><a>Another Video</a></div>
        <span class="icon fa-clock-o">15:45</span>
    </section>
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
            }
        )

    monkeypatch.setattr(hqporner.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hqporner.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hqporner.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(hqporner.utils, "eod", lambda: None)

    hqporner.HQLIST("https://hqporner.com/hdporn/1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Video Title"
    assert "https://hqporner.com/hdporn/hot-video-12345/" in downloads[0]["url"]
    assert "https:" in downloads[0]["icon"]
    assert downloads[0]["duration"] == "10:30"

    assert downloads[1]["name"] == "Another Video"
    assert downloads[1]["duration"] == "15:45"


def test_hqlist_pagination(monkeypatch):
    """Test that HQLIST handles pagination correctly."""
    html = """
    <html>
    <section class="box feature">
        <a class="image featured" href="/hdporn/test-123/">
            <img src="thumb.jpg" />
        </a>
        <div class="meta-data-title"><a>Test</a></div>
    </section>
    <ul class="actions pagination">
        <a class="button mobile-pagi" href="/hdporn/2">Next</a>
    </ul>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(hqporner.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hqporner.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(hqporner.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hqporner.utils, "eod", lambda: None)

    hqporner.HQLIST("https://hqporner.com/hdporn/1")

    next_pages = [d for d in dirs if "Next" in d["name"]]
    assert len(next_pages) == 1
    assert "https://hqporner.com/hdporn/2" in next_pages[0]["url"]


def test_hqcat_parses_categories(monkeypatch):
    """Test that HQCAT function parses category listings."""
    html = """
    <html>
    <h3><a href="/category/amateur">Amateur</a></h3>
    <h2><a href="/actress/jane-doe">Jane Doe</a></h2>
    <div class="content">
        <a href="/studio/brazzers">Brazzers</a>
    </div>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(hqporner.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hqporner.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hqporner.utils, "eod", lambda: None)

    hqporner.HQCAT("https://hqporner.com/categories")

    assert len(dirs) == 3
    # Sorted alphabetically
    assert "Amateur" in dirs[0]["name"]
    assert "Brazzers" in dirs[1]["name"]
    assert "Jane Doe" in dirs[2]["name"]


def test_hqsearch_with_keyword(monkeypatch):
    """Test that HQSEARCH with keyword calls HQLIST with encoded query."""
    hqlist_calls = []

    def fake_hqlist(url):
        hqlist_calls.append(url)

    monkeypatch.setattr(hqporner, "HQLIST", fake_hqlist)

    hqporner.HQSEARCH("https://hqporner.com/?q=", keyword="test query")

    assert len(hqlist_calls) == 1
    assert "test%20query" in hqlist_calls[0]


def test_hqsearch_without_keyword(monkeypatch):
    """Test that HQSEARCH without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(hqporner.site, "search_dir", fake_search_dir)

    hqporner.HQSEARCH("https://hqporner.com/?q=")

    assert len(search_called) == 1
    assert search_called[0][1] == "HQSEARCH"
