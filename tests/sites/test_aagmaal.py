"""Comprehensive tests for aagmaal.gay site implementation."""

from pathlib import Path

from resources.lib.sites import aagmaal


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "aagmaal"


def load_fixture(name):
    """Load a fixture file from the aagmaal fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
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

    monkeypatch.setattr(aagmaal.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(aagmaal.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(aagmaal.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.List("https://aagmaal.gay/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (uses title attribute)
    assert downloads[0]["name"] == "Desi Bhabhi Hot Romance"
    assert downloads[0]["url"] == "https://aagmaal.gay/video/desi-bhabhi-hot-romance/"
    assert downloads[0]["icon"] == "https://aagmaal.gay/wp-content/uploads/thumb1.jpg"

    # Check second video (uses data-src and title from h3)
    assert downloads[1]["name"] == "Indian Couple Leaked MMS"
    assert downloads[1]["url"] == "https://aagmaal.gay/video/indian-couple-leaked-mms/"
    assert downloads[1]["icon"] == "https://aagmaal.gay/wp-content/uploads/thumb2.jpg"

    # Check third video (uses data-original and post-title)
    assert downloads[2]["name"] == "Punjabi Girl Bathroom Video"
    assert (
        downloads[2]["url"] == "https://aagmaal.gay/video/punjabi-girl-bathroom-video/"
    )
    assert downloads[2]["icon"] == "https://aagmaal.gay/wp-content/uploads/thumb3.jpg"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "Page 1 of 15" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://aagmaal.gay/page/2/"


def test_list_handles_no_pagination(monkeypatch):
    """Test that List handles pages without pagination gracefully."""
    html = """
    <html>
    <div class="recent-item">
        <a href="https://aagmaal.gay/video/test/" title="Test Video">
            <img src="thumb.jpg">
        </a>
    </div>
    </html>
    """

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(aagmaal.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        aagmaal.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(aagmaal.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.List("https://aagmaal.gay/")

    # Should have 1 video
    assert len(downloads) == 1
    # Should have no pagination
    assert len(dirs) == 0


def test_categories_parses_tag_links(monkeypatch):
    """Test that Categories correctly parses category/tag links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(aagmaal.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(aagmaal.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.Categories("https://aagmaal.gay/")

    # Should have 4 categories
    assert len(dirs) == 4

    # Check first category (uses aria-label)
    assert dirs[0]["name"] == "Desi Videos"
    assert dirs[0]["url"] == "https://aagmaal.gay/category/desi/"
    assert dirs[0]["mode"] == "List2"

    # Check second category (uses title attribute)
    assert dirs[1]["name"] == "MMS Leaked Videos"
    assert dirs[1]["url"] == "https://aagmaal.gay/category/mms/"

    # Check third category (uses text content)
    assert dirs[2]["name"] == "Bhabhi"
    assert dirs[2]["url"] == "https://aagmaal.gay/category/bhabhi/"

    # Check fourth category (uses text content)
    assert dirs[3]["name"] == "Bengali"
    assert dirs[3]["url"] == "https://aagmaal.gay/category/bengali/"


def test_list2_parses_article_items(monkeypatch):
    """Test that List2 correctly parses article items."""
    html = """
    <html>
    <article>
        <div class="title">
            <a href="https://aagmaal.gay/category/desi/video1/">Desi Video 1</a>
        </div>
        <img src="thumb1.jpg">
    </article>
    <article>
        <h2 class="title">
            <a href="https://aagmaal.gay/category/desi/video2/">Desi Video 2</a>
        </h2>
        <img data-src="thumb2.jpg">
    </article>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(aagmaal.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        aagmaal.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(aagmaal.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.List2("https://aagmaal.gay/category/desi/")

    # Should have 2 videos
    assert len(downloads) == 2
    assert downloads[0] == "Desi Video 1"
    assert downloads[1] == "Desi Video 2"


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(aagmaal.site, "search_dir", fake_search_dir)

    aagmaal.Search("https://aagmaal.gay/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List2 with encoded search term."""
    list2_calls = []

    def fake_list2(url):
        list2_calls.append(url)

    monkeypatch.setattr(aagmaal, "List2", fake_list2)

    aagmaal.Search("https://aagmaal.gay/?s=", keyword="desi bhabhi")

    assert len(list2_calls) == 1
    assert "desi+bhabhi" in list2_calls[0]
    assert list2_calls[0].startswith("https://aagmaal.gay/?s=")
