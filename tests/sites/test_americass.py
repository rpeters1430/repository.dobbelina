"""Tests for americass.net site implementation."""

from resources.lib.sites import americass


def test_list_parses_videos(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = """
    <html>
    <div class="wrapper">
        <a href="/interstice-ad?path=/video/12345/hot-video">
            <img data-src="https://img.americass.net/thumb1.jpg" />
            <div class="duration-overlay">10:30</div>
            <div class="mb-0">Hot Video Title</div>
        </a>
    </div>
    <div class="wrapper">
        <a href="/video/67890/another-video">
            <img data-src="//img.americass.net/thumb2.jpg" />
            <div class="duration-overlay">15:45</div>
            <div class="mb-0">Another Video</div>
        </a>
    </div>
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
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        )

    monkeypatch.setattr(americass.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(americass.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(americass.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(americass.utils, "eod", lambda: None)

    americass.List("https://americass.net/video?page=1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Hot Video Title"
    assert "https://americass.net/video/12345/hot-video" in downloads[0]["url"]
    assert downloads[0]["icon"] == "https://img.americass.net/thumb1.jpg"
    assert downloads[0]["duration"] == "10:30"

    assert downloads[1]["name"] == "Another Video"
    assert downloads[1]["icon"] == "https://img.americass.net/thumb2.jpg"
    assert downloads[1]["duration"] == "15:45"


def test_list_pagination(monkeypatch):
    """Test that List handles pagination correctly."""
    html = """
    <html>
    <div class="wrapper">
        <a href="/video/123/test"><div class="mb-0">Test</div></a>
    </div>
    <a rel="next" href="/video?page=2">Next</a>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(americass.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(americass.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(americass.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(americass.utils, "eod", lambda: None)

    americass.List("https://americass.net/video?page=1")

    next_pages = [d for d in dirs if "Next" in d["name"]]
    assert len(next_pages) == 1
    assert "https://americass.net/video?page=2" in next_pages[0]["url"]


def test_tags_parses_correctly(monkeypatch):
    """Test that Tags function extracts tags with BeautifulSoup."""
    html = """
    <html>
    <a href="/tag/asian">Asian</a>
    <a href="/tag/big-boobs">Big Boobs</a>
    <a href="/tag/milf">MILF</a>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(americass.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(americass.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(americass.utils, "eod", lambda: None)

    americass.Tags("https://americass.net/tag/")

    assert len(dirs) == 3
    assert "Asian" in dirs[0]["name"]
    assert "https://americass.net/tag/asian" in dirs[0]["url"]
    assert "Big Boobs" in dirs[1]["name"]
    assert "MILF" in dirs[2]["name"]


def test_actor_parses_models(monkeypatch):
    """Test that Actor function parses model listings."""
    html = """
    <html>
    <a href="/actor/jane-doe">
        <img src="/img/jane.jpg" />
        <div class="label">Jane Doe</div>
    </a>
    <a href="/actor/john-smith">
        <img src="/img/john.jpg" />
        <div class="label">John Smith</div>
    </a>
    </html>
    """

    dirs = []

    def fake_add_dir(name, url, mode, iconimage):
        dirs.append({"name": name, "url": url, "icon": iconimage})

    monkeypatch.setattr(americass.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(americass.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(americass.utils, "eod", lambda: None)

    americass.Actor("https://americass.net/actor/?l=j")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Jane Doe"
    assert "https://americass.net/actor/jane-doe" in dirs[0]["url"]
    assert "https://americass.net/img/jane.jpg" in dirs[0]["icon"]
    assert dirs[1]["name"] == "John Smith"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(americass, "List", fake_list)

    americass.Search("https://americass.net/video/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "test%20query" in list_calls[0]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(americass.site, "search_dir", fake_search_dir)

    americass.Search("https://americass.net/video/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"
