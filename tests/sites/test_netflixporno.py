"""Tests for netflixporno.com site implementation."""
from pathlib import Path

from resources.lib.sites import netflixporno


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "netflixporno"


def load_fixture(name):
    """Load a fixture file from the netflixporno fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc=""):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "icon": iconimage,
        })

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(netflixporno.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(netflixporno.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(netflixporno.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(netflixporno.utils, "eod", lambda: None)

    netflixporno.List("https://netflixporno.net/adult")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (data-lazy-src)
    assert downloads[0]["name"] == "Stepmom Seduction"
    assert "video-one" in downloads[0]["url"]
    assert "thumb1.jpg" in downloads[0]["icon"]

    # Check second video (data-src fallback)
    assert downloads[1]["name"] == "Office Affairs"
    assert "video-two" in downloads[1]["url"]
    assert "thumb2.jpg" in downloads[1]["icon"]

    # Check third video (src fallback)
    assert downloads[2]["name"] == "Passionate Night"
    assert "video-three" in downloads[2]["url"]
    assert "thumb3.jpg" in downloads[2]["icon"]

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "page/2" in dirs[0]["url"]
    assert "(Currently in Page 1 of 5)" in dirs[0]["name"]


def test_list_handles_no_pagination(monkeypatch):
    """Test that List handles pages without pagination."""
    html = """
    <html>
    <body>
    <article>
        <a href="/video-one/">
            <img src="thumb.jpg">
        </a>
        <h2>Video One</h2>
    </article>
    </body>
    </html>
    """

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name})

    monkeypatch.setattr(netflixporno.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(netflixporno.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(netflixporno.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(netflixporno.utils, "eod", lambda: None)

    netflixporno.List("https://netflixporno.net/adult")

    # Should have no pagination
    assert len(dirs) == 0


def test_categories_parses_categories(monkeypatch):
    """Test that Categories correctly parses category links."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({
            "name": name,
            "url": url,
            "mode": mode,
        })

    monkeypatch.setattr(netflixporno.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(netflixporno.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(netflixporno.utils, "eod", lambda: None)

    netflixporno.Categories("https://netflixporno.net/categories/")

    # Should have 3 categories
    assert len(dirs) == 3

    # Check categories (no specific order guaranteed with set)
    cat_names = [d["name"] for d in dirs]
    assert "MILF (234 videos)" in cat_names
    assert "Teen (189 videos)" in cat_names
    assert "Anal (156 videos)" in cat_names

    # Check URLs
    urls = [d["url"] for d in dirs]
    assert any("category/milf" in u for u in urls)
    assert any("category/teen" in u for u in urls)
    assert any("category/anal" in u for u in urls)


def test_search_without_keyword_shows_search_dialog(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(netflixporno.site, "search_dir", fake_search_dir)

    netflixporno.Search("https://netflixporno.net/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword delegates to List."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(netflixporno, "List", fake_list)

    netflixporno.Search("https://netflixporno.net/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
