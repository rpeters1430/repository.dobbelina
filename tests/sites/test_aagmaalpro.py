"""Comprehensive tests for aagmaal.delhi.in (aagmaalpro) site implementation."""

from pathlib import Path

from resources.lib.sites import aagmaalpro


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "aagmaalpro"


def load_fixture(name):
    """Load a fixture file from the aagmaalpro fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_article_items(monkeypatch):
    """Test that List correctly parses article items with BeautifulSoup."""
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
                "duration": kwargs.get("duration", ""),
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

    monkeypatch.setattr(aagmaalpro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(aagmaalpro.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(aagmaalpro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(aagmaalpro.utils, "eod", lambda: None)

    aagmaalpro.List("https://aagmaal.delhi.in/")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (name from header span, src attribute)
    assert downloads[0]["name"] == "Hot Desi Girl Strip Show"
    assert (
        downloads[0]["url"]
        == "https://aagmaal.delhi.in/video/hot-desi-girl-strip-show/"
    )
    assert downloads[0]["icon"] == "https://aagmaal.delhi.in/thumbs/thumb1.jpg"
    assert downloads[0]["duration"] == "18:25"

    # Check second video (name from header span, data-src attribute, duration with icon)
    assert downloads[1]["name"] == "Indian Wife Shared"
    assert downloads[1]["url"] == "https://aagmaal.delhi.in/video/indian-wife-shared/"
    assert downloads[1]["icon"] == "https://aagmaal.delhi.in/thumbs/thumb2.jpg"
    assert downloads[1]["duration"] == "25:10"

    # Check third video (name from header text, data-original, time.duration)
    assert downloads[2]["name"] == "Desi College Couple"
    assert downloads[2]["url"] == "https://aagmaal.delhi.in/video/desi-college-couple/"
    assert downloads[2]["icon"] == "https://aagmaal.delhi.in/thumbs/thumb3.jpg"
    assert downloads[2]["duration"] == "12:30"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "Page 1 of 20" in dirs[0]["name"]


def test_list_pagination_without_last_link(monkeypatch):
    """Test that List handles pagination without 'Last' link."""
    html = """
    <html>
    <article>
        <a href="https://aagmaal.delhi.in/video/test/">
            <img src="thumb.jpg">
        </a>
        <header><span>Test Video</span></header>
    </article>
    <div class="pagination">
        <span class="current">5</span>
        <a href="#">Next</a>
    </div>
    </html>
    """

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(aagmaalpro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(aagmaalpro.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(aagmaalpro.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(aagmaalpro.utils, "eod", lambda: None)

    aagmaalpro.List("https://aagmaal.delhi.in/")

    # Should have pagination without total pages
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]
    assert "Currently in 5" in dirs[0]


def test_list_pagination_with_inactive_link(monkeypatch):
    """Test that List handles inactive next links."""
    html = """
    <html>
    <article>
        <a href="https://aagmaal.delhi.in/video/test/">
            <img src="thumb.jpg">
        </a>
        <header>Test Video</header>
    </article>
    <div class="pagination">
        <span class="current">1</span>
        <a href="https://aagmaal.delhi.in/page/2/" class="inactive">2</a>
    </div>
    </html>
    """

    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(aagmaalpro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(aagmaalpro.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(aagmaalpro.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(aagmaalpro.utils, "eod", lambda: None)

    aagmaalpro.List("https://aagmaal.delhi.in/")

    # Should have pagination with inactive link
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]


def test_categories_parses_and_collects_across_pages(monkeypatch):
    """Test that Categories correctly parses categories and handles multi-page collection."""
    html = load_fixture("categories.html")

    dirs = []
    page_count = [0]

    def fake_get_html(url, referer=None, headers=None):
        page_count[0] += 1
        if page_count[0] == 1:
            return html
        else:
            # Second page with no more pagination
            return """
            <html>
            <article>
                <a href="https://aagmaal.delhi.in/category/punjabi/">
                    <img src="punjabi.jpg">
                </a>
                <div class="title">Punjabi</div>
            </article>
            </html>
            """

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(aagmaalpro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(aagmaalpro.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(aagmaalpro.utils, "eod", lambda: None)

    aagmaalpro.Categories("https://aagmaal.delhi.in/categories/")

    # Should have 4 categories (3 from page 1 + 1 from page 2), sorted alphabetically
    assert len(dirs) == 4

    # Check sorting (Bhabhi, Desi Videos, Leaked MMS, Punjabi)
    assert dirs[0]["name"] == "Bhabhi"
    assert dirs[1]["name"] == "Desi Videos"
    assert dirs[2]["name"] == "Leaked MMS"
    assert dirs[3]["name"] == "Punjabi"

    # Verify categories from first page
    assert dirs[1]["url"] == "https://aagmaal.delhi.in/category/desi/"
    assert dirs[0]["url"] == "https://aagmaal.delhi.in/category/bhabhi/"

    # Verify category from second page
    assert dirs[3]["url"] == "https://aagmaal.delhi.in/category/punjabi/"


def test_list2_parses_title_div(monkeypatch):
    """Test that List2 correctly parses items with title div."""
    html = """
    <html>
    <article>
        <div class="title">
            <a href="https://aagmaal.delhi.in/category/test/video1/">Test Video 1</a>
        </div>
        <img src="thumb1.jpg">
    </article>
    <article>
        <h2 class="title">
            <a href="https://aagmaal.delhi.in/category/test/video2/">Test Video 2</a>
        </h2>
        <img data-src="thumb2.jpg">
    </article>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(aagmaalpro.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        aagmaalpro.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(aagmaalpro.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(aagmaalpro.utils, "eod", lambda: None)

    aagmaalpro.List2("https://aagmaal.delhi.in/category/test/")

    # Should have 2 videos
    assert len(downloads) == 2
    assert downloads[0] == "Test Video 1"
    assert downloads[1] == "Test Video 2"


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(aagmaalpro.site, "search_dir", fake_search_dir)

    aagmaalpro.Search("https://aagmaal.delhi.in/?s=")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded search term."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(aagmaalpro, "List", fake_list)

    aagmaalpro.Search("https://aagmaal.delhi.in/?s=", keyword="desi bhabhi")

    assert len(list_calls) == 1
    assert "desi+bhabhi" in list_calls[0]
    assert list_calls[0].startswith("https://aagmaal.delhi.in/?s=")
