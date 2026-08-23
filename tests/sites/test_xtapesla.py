"""Comprehensive tests for xtapes.la site implementation."""

from pathlib import Path
from resources.lib.sites import xtapesla

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "xtapesla"


def load_fixture(name):
    """Load a fixture file from the xtapesla fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(xtapesla.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xtapesla.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(xtapesla.site, "add_dir", fake_add_dir)

    xtapesla.List("https://xtapes.la/")

    assert len(downloads) > 0
    first = downloads[0]
    assert first["mode"] == "Playvid"
    assert first["url"].startswith("https://xtapes.la/")
    assert first["name"]
    assert first["icon"].startswith("http")


def test_networks(monkeypatch):
    """Test that Networks parses network list."""
    sample_nav_html = """
    <li class="menu-item-has-children">
        <ul class="sub-menu">
            <li><a href="https://xtapes.la/onlyfans/">OnlyFans</a></li>
            <li><a href="https://xtapes.la/brazzers/">Brazzers</a></li>
        </ul>
    </li>
    """
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return sample_nav_html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(xtapesla.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(xtapesla.site, "add_dir", fake_add_dir)

    xtapesla.Networks("https://xtapes.la/")

    assert len(dirs) == 2
    assert "OnlyFans" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://xtapes.la/onlyfans/"
    assert "Brazzers" in dirs[1]["name"]
    assert dirs[1]["url"] == "https://xtapes.la/brazzers/"


def test_search_with_keyword(monkeypatch):
    """Test that Search calls List with formatted search query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(xtapesla, "List", fake_list)

    xtapesla.Search("https://xtapes.la/?s=", keyword="blonde teen")

    assert len(list_calls) == 1
    assert "blonde+teen" in list_calls[0]


def test_main_menu(monkeypatch):
    """Test Main menu registers expected directory items."""
    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(xtapesla.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(xtapesla, "List", lambda url: None)

    xtapesla.Main()

    modes = [d["mode"] for d in dirs]
    assert "Search" in modes
    assert "Filters" in modes
    assert "Networks" in modes
    assert "List" in modes


def test_filters_sort_selection(monkeypatch):
    """Test Filters sort selection delegates to List."""
    list_calls = []
    dialog_select_calls = []

    def fake_dialog_select(title, options):
        dialog_select_calls.append((title, options))
        return 0

    class FakeDialog:
        def select(self, title, options):
            return fake_dialog_select(title, options)

    monkeypatch.setattr(xtapesla.xbmcgui, "Dialog", FakeDialog)
    monkeypatch.setattr(xtapesla, "List", lambda url: list_calls.append(url))

    xtapesla.Filters("https://xtapes.la/")

    assert len(dialog_select_calls) == 2
    assert len(list_calls) == 1
    assert "filtre=date" in list_calls[0]

