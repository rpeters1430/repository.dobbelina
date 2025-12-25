"""Comprehensive tests for heroero site implementation."""

from pathlib import Path

from resources.lib.sites import heroero


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "heroero"


def load_fixture(name):
    """Load a fixture file from the heroero fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List() correctly parses video items using BeautifulSoup."""
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(
        name, url, mode, iconimage, desc="", contextm=None, quality="", **kwargs
    ):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "quality": quality,
                "contextm": contextm,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, contextm=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "contextm": contextm})

    monkeypatch.setattr(heroero.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(heroero.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(heroero.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(heroero.utils, "eod", lambda: None)

    # Call List
    heroero.List("https://heroero.com/latest-updates/")

    # Verify we got 3 videos
    assert len(downloads) == 3

    # Verify first video (HD)
    assert downloads[0]["name"] == "Sample Hentai Episode 1"
    assert downloads[0]["url"] == "https://heroero.com/video/sample-hentai-1/"
    assert downloads[0]["mode"] == "Playvid"
    assert "thumb1.jpg" in downloads[0]["icon"]
    assert downloads[0]["quality"] == "HD"
    assert downloads[0]["contextm"] is not None

    # Verify second video (no HD)
    assert downloads[1]["name"] == "Sample Hentai Episode 2"
    assert downloads[1]["quality"] == ""

    # Verify third video (HD)
    assert downloads[2]["name"] == "Sample Hentai Episode 3"
    assert downloads[2]["quality"] == "HD"


def test_list_handles_pagination(monkeypatch):
    """Test that List() correctly handles pagination."""
    html = load_fixture("list.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, contextm=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "contextm": contextm})

    monkeypatch.setattr(heroero.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(heroero.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(heroero.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(heroero.utils, "eod", lambda: None)

    # Call List
    heroero.List("https://heroero.com/latest-updates/")

    # Verify pagination was added
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert next_pages[0]["url"] == "/latest-updates/2/"
    assert next_pages[0]["mode"] == "List"
    # Should have goto page context menu
    assert next_pages[0]["contextm"] is not None


def test_list_handles_empty_results(monkeypatch):
    """Test that List() handles empty HTML gracefully."""
    empty_html = '<html><body><div class="videos"></div></body></html>'

    downloads = []

    monkeypatch.setattr(heroero.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(
        heroero.site, "add_download_link", lambda *a, **k: downloads.append(a)
    )
    monkeypatch.setattr(heroero.utils, "eod", lambda: None)

    # Should not crash
    heroero.List("https://heroero.com/latest-updates/")

    # Should have no downloads
    assert len(downloads) == 0


def test_categories_parses_category_items(monkeypatch):
    """Test that Categories() correctly parses category items using BeautifulSoup."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(heroero.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(heroero.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(heroero.utils, "eod", lambda: None)
    monkeypatch.setattr(heroero.xbmcplugin, "addSortMethod", lambda *a, **k: None)

    # Call Categories
    heroero.Categories("https://heroero.com/categories/")

    # Should have 3 categories + 1 next page
    categories = [d for d in dirs if d["mode"] == "List"]
    assert len(categories) == 3

    # Verify first category (with image and video count, capitalized)
    assert categories[0]["name"] == "3d [COLOR cyan][250 videos][/COLOR]"
    assert categories[0]["url"] == "https://heroero.com/categories/3d/"
    assert "3d.jpg" in categories[0]["icon"]

    # Verify second category (with image and video count, capitalized)
    assert categories[1]["name"] == "Ahegao [COLOR cyan][125 videos][/COLOR]"
    assert categories[1]["url"] == "https://heroero.com/categories/ahegao/"

    # Verify third category (no image, with video count, capitalized)
    assert categories[2]["name"] == "Anal [COLOR cyan][89 videos][/COLOR]"
    assert categories[2]["url"] == "https://heroero.com/categories/anal/"
    assert categories[2]["icon"] == ""


def test_categories_handles_pagination(monkeypatch):
    """Test that Categories() correctly handles pagination."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(heroero.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(heroero.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(heroero.utils, "eod", lambda: None)
    monkeypatch.setattr(heroero.xbmcplugin, "addSortMethod", lambda *a, **k: None)

    # Call Categories
    heroero.Categories("https://heroero.com/categories/")

    # Verify pagination was added
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert next_pages[0]["url"] == "/categories/2/"
    assert next_pages[0]["mode"] == "Categories"


def test_actress_parses_actress_items(monkeypatch):
    """Test that Categories() correctly parses actress items (actress URL)."""
    html = load_fixture("actress.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(heroero.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(heroero.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(heroero.utils, "eod", lambda: None)

    # Call Categories with actress URL (should NOT capitalize)
    heroero.Categories("https://heroero.com/actress/")

    # Should have 2 actresses + 1 next page
    actresses = [d for d in dirs if d["mode"] == "List"]
    assert len(actresses) == 2

    # Verify first actress (NOT capitalized since it's not /categories/)
    assert actresses[0]["name"] == "Sample Actress 1 [COLOR cyan][45 videos][/COLOR]"
    assert actresses[0]["url"] == "https://heroero.com/actress/sample-actress-1/"
    assert "actress1.jpg" in actresses[0]["icon"]

    # Verify second actress
    assert actresses[1]["name"] == "Sample Actress 2 [COLOR cyan][32 videos][/COLOR]"
    assert actresses[1]["url"] == "https://heroero.com/actress/sample-actress-2/"


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(heroero.site, "search_dir", fake_search_dir)

    heroero.Search(
        "https://heroero.com/see/{}/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q={}&category_ids=&sort_by=&from_videos=1&from_albums=1"
    )

    assert search_dir_called[0]


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search() with keyword calls List()."""
    list_called_with = {}

    def fake_list(url):
        list_called_with["url"] = url

    monkeypatch.setattr(heroero, "List", fake_list)

    heroero.Search(
        "https://heroero.com/see/{}/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q={}&category_ids=&sort_by=&from_videos=1&from_albums=1",
        keyword="sample search",
    )

    # Verify URL contains the search keyword
    assert "url" in list_called_with
    assert "sample-search" in list_called_with["url"]
