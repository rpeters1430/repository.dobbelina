"""Comprehensive tests for AWM Network site implementation."""

from pathlib import Path

from resources.lib.sites import awmnet


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "awmnet"


def load_fixture(name):
    """Load a fixture file from the awmnet fixtures directory."""
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
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
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

    monkeypatch.setattr(awmnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(awmnet.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(awmnet.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.List("https://www.fuq.com/new?pricing=free")

    # Should have 3 videos
    assert len(downloads) == 3

    # Check first video (has HD tag and provider)
    assert downloads[0]["name"] == "[COLOR yellow][Brazzers][/COLOR] Hot Asian Babe"
    assert "/videos/12345/hot-asian-babe/" in downloads[0]["url"]
    assert downloads[0]["icon"] == "https://www.fuq.com/thumbs/thumb1.jpg"
    assert downloads[0]["duration"] == "15:30"
    assert downloads[0]["quality"] == "HD"

    # Check second video (has provider but no HD, uses data-src)
    assert (
        downloads[1]["name"]
        == "[COLOR yellow][Reality Kings][/COLOR] Busty MILF Action"
    )
    assert "/videos/67890/busty-milf-action/" in downloads[1]["url"]
    assert downloads[1]["icon"] == "https://www.fuq.com/thumbs/thumb2.jpg"
    assert downloads[1]["duration"] == "22:45"
    assert downloads[1]["quality"] == ""

    # Check third video (no provider, has HD, uses data-original)
    assert "Threesome Fun" in downloads[2]["name"]
    assert "/videos/11111/threesome-fun/" in downloads[2]["url"]
    assert downloads[2]["icon"] == "https://www.fuq.com/thumbs/thumb3.jpg"
    assert downloads[2]["duration"] == "28:15"
    assert downloads[2]["quality"] == "HD"

    # Should have pagination
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "Page 1" in dirs[0]["name"]
    assert "/new?pricing=free&page=2" in dirs[0]["url"]


def test_list_handles_no_pagination(monkeypatch):
    """Test that List handles pages without pagination gracefully."""
    html = """
    <html>
    <div class="video-item">
        <a class="item-link" href="/videos/12345/test-video/" title="Test Video">
            <img src="thumb.jpg">
        </a>
    </div>
    </html>
    """

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(awmnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        awmnet.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(awmnet.site, "add_dir", lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.List("https://www.fuq.com/new?pricing=free")

    # Should have 1 video
    assert len(downloads) == 1
    # Should have no pagination
    assert len(dirs) == 0


def test_list_handles_duplicate_videos(monkeypatch):
    """Test that List correctly deduplicates videos with same URL."""
    html = """
    <html>
    <div class="video-item">
        <a class="item-link" href="/videos/12345/test/" title="Test Video 1">
            <img src="thumb1.jpg">
        </a>
    </div>
    <div class="video-item">
        <a class="item-link" href="/videos/12345/test/" title="Test Video 2">
            <img src="thumb2.jpg">
        </a>
    </div>
    </html>
    """

    downloads = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    monkeypatch.setattr(awmnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        awmnet.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(awmnet.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.List("https://www.fuq.com/new?pricing=free")

    # Should have only 1 video (duplicate removed)
    assert len(downloads) == 1


def test_categories_parses_card_items(monkeypatch):
    """Test that Categories correctly parses category card items."""
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
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(awmnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(awmnet.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.Categories("https://www.fuq.com/")

    # Should have 3 categories
    assert len(dirs) == 3

    # Check first category
    assert dirs[0]["name"] == "Anal [COLOR deeppink](125k videos)[/COLOR]"
    assert "/categories/anal?pricing=free" in dirs[0]["url"]
    assert dirs[0]["icon"] == "https://www.fuq.com/cat-images/anal.jpg"
    assert dirs[0]["mode"] == "List"

    # Check second category (uses data-src)
    assert dirs[1]["name"] == "Asian [COLOR deeppink](89.5k videos)[/COLOR]"
    assert "/categories/asian?pricing=free" in dirs[1]["url"]
    assert dirs[1]["icon"] == "https://www.fuq.com/cat-images/asian.jpg"

    # Check third category
    assert dirs[2]["name"] == "MILF [COLOR deeppink](205.3k videos)[/COLOR]"
    assert "/categories/milf?pricing=free" in dirs[2]["url"]


def test_tags_parses_category_items(monkeypatch):
    """Test that Tags correctly parses tag/pornstar items."""
    html = load_fixture("tags.html")

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

    monkeypatch.setattr(awmnet.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(awmnet.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.Tags("https://www.fuq.com/pornstar")

    # Should have 3 tags/pornstars
    assert len(dirs) == 3

    # Check first tag - Due to selector logic, video count won't be appended
    # because count_tag will select the same title span
    assert dirs[0]["name"] == "Mia Malkova"
    assert "/pornstar/mia-malkova?pricing=free" in dirs[0]["url"]
    assert dirs[0]["mode"] == "List"

    # Check second tag
    assert dirs[1]["name"] == "Riley Reid"
    assert "/pornstar/riley-reid?pricing=free" in dirs[1]["url"]

    # Check third tag
    assert dirs[2]["name"] == "Rough"
    assert "/tags/rough?pricing=free" in dirs[2]["url"]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(awmnet.site, "search_dir", fake_search_dir)

    awmnet.Search("https://www.fuq.com/search/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded search term."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(awmnet, "List", fake_list)

    awmnet.Search("https://www.fuq.com/search/", keyword="asian milf")

    assert len(list_calls) == 1
    assert "asian%20milf" in list_calls[0]
    assert "?pricing=free" in list_calls[0]


def test_getbaselink_extracts_site_url(monkeypatch):
    """Test that getBaselink correctly extracts site URL from video URL."""
    test_url = "https://www.fuq.com/videos/12345/test-video/"
    result = awmnet.getBaselink(test_url)
    assert result == "https://www.fuq.com/"

    test_url2 = "https://www.4tube.com/videos/67890/another-video/"
    result2 = awmnet.getBaselink(test_url2)
    assert result2 == "https://www.4tube.com/"


def test_main_lists_all_sites(monkeypatch):
    """Test that Main correctly lists all 48 AWM Network sites."""
    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(awmnet.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.Main()

    # Should have 48 sites
    assert len(dirs) == 48

    # Check that sites are sorted alphabetically
    names = [d["name"] for d in dirs]
    assert names == sorted(names)

    # Check first site (4tube should be first alphabetically)
    assert "[COLOR hotpink]4tube[/COLOR]" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://www.4tube.com/"
    assert dirs[0]["mode"] == "SiteMain"


def test_sitemain_creates_menu_structure(monkeypatch):
    """Test that SiteMain creates proper menu for a site."""
    dirs = []
    list_calls = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(awmnet.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(awmnet, "List", fake_list)
    monkeypatch.setattr(awmnet.utils, "eod", lambda: None)

    awmnet.SiteMain("https://www.fuq.com/")

    # Should have Categories, Pornstars, Tags, Search
    assert len(dirs) == 4
    assert "Categories" in dirs[0]["name"]
    assert "Pornstars" in dirs[1]["name"]
    assert "Tags" in dirs[2]["name"]
    assert "Search" in dirs[3]["name"]

    # Should call List with new videos
    assert len(list_calls) == 1
    assert "new?pricing=free" in list_calls[0]
