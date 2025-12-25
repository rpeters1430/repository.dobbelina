"""Tests for javbangers.com site implementation."""

from pathlib import Path

from resources.lib.sites import javbangers


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "javbangers"


def load_fixture(name):
    """Load a fixture file from the javbangers fixtures directory."""
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
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
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

    def fake_get_cookies():
        return "kt_tcookie=1"

    monkeypatch.setattr(javbangers.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javbangers.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(javbangers.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javbangers.utils, "eod", lambda: None)
    monkeypatch.setattr(javbangers, "get_cookies", fake_get_cookies)
    monkeypatch.setattr(javbangers, "jblogged", False)

    javbangers.List("https://www.javbangers.com/latest-updates/")

    # Should have 2 videos (private video is excluded when not logged in)
    assert len(downloads) == 2

    # Check first video
    assert downloads[0]["name"] == "JAV Bangers Video 1"
    assert downloads[0]["url"] == "/videos/12345/javbangers-video-1/"
    assert downloads[0]["icon"] == "https://www.javbangers.com/thumb1.jpg"
    assert downloads[0]["duration"] == "45:30"
    assert downloads[0]["quality"] == "HD"

    # Check third video (second non-private)
    assert downloads[1]["name"] == "JAV Bangers Video 3"
    assert downloads[1]["url"] == "/videos/24680/javbangers-video-3/"
    assert downloads[1]["duration"] == "38:15"
    assert downloads[1]["quality"] == "HD"


def test_list_private_videos_when_logged_in(monkeypatch):
    """Test that List includes private videos when logged in."""
    html = load_fixture("listing.html")

    downloads = []

    def fake_get_html(url, referer=None, headers=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
            }
        )

    def fake_get_cookies():
        return "kt_tcookie=1; kt_member=user123"

    monkeypatch.setattr(javbangers.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javbangers.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(javbangers.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(javbangers.utils, "eod", lambda: None)
    monkeypatch.setattr(javbangers, "get_cookies", fake_get_cookies)
    monkeypatch.setattr(javbangers, "jblogged", True)

    javbangers.List("https://www.javbangers.com/latest-updates/")

    # Should have 3 videos (including private)
    assert len(downloads) == 3

    # Check private video has [PV] tag
    assert "[PV]" in downloads[1]["name"]
    assert "JAV Bangers Private Video 2" in downloads[1]["name"]


def test_list_pagination(monkeypatch):
    """Test that List correctly parses pagination HTML structure."""
    html = load_fixture("listing.html")

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

    def fake_get_cookies():
        return "kt_tcookie=1"

    # Mock randint to return a consistent value - it's imported at module level
    monkeypatch.setattr(javbangers, "randint", lambda a, b: 123456789012)
    # Mock utils.addon_sys which is needed for context menu
    monkeypatch.setattr(
        javbangers.utils, "addon_sys", "plugin://plugin.video.cumination"
    )

    monkeypatch.setattr(javbangers.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(javbangers.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(javbangers.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(javbangers.utils, "eod", lambda: None)
    monkeypatch.setattr(javbangers, "get_cookies", fake_get_cookies)
    monkeypatch.setattr(javbangers, "jblogged", False)

    javbangers.List("https://www.javbangers.com/latest-updates/")

    # Should have next page
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1, (
        f"Expected 1 next page, got {len(next_pages)}. All dirs: {dirs}"
    )
    assert "2/15" in next_pages[0]["name"] or "(2)" in next_pages[0]["name"]


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search dialog."""
    search_called = []

    def fake_search_dir(url, mode):
        search_called.append((url, mode))

    monkeypatch.setattr(javbangers.site, "search_dir", fake_search_dir)

    javbangers.Search("https://www.javbangers.com/search/{0}/")

    assert len(search_called) == 1
    assert search_called[0][1] == "Search"


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded search."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(javbangers, "List", fake_list)

    javbangers.Search("https://www.javbangers.com/search/{0}/", keyword="test query")

    assert len(list_calls) == 1
    assert "test+query" in list_calls[0]
