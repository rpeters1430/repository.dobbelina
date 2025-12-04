from pathlib import Path

from resources.lib.sites import erome


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "erome"


def load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_albums(monkeypatch):
    """Test that List correctly parses album items from HTML."""
    html = load_fixture("explore_new.html")
    monkeypatch.setattr(erome.utils, "getHtml", lambda url, referer=None: html)

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(erome.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(erome.utils, "eod", lambda: None)

    erome.List("https://www.erome.com/explore/new")

    # Filter out pagination entries
    albums = [d for d in dirs if "Next Page" not in d["name"]]

    # Should have 3 albums
    assert len(albums) == 3, f"Expected 3 albums, got {len(albums)}"

    # Check first album (images only)
    assert "VID-20191026-WA0051" in albums[0]["name"]
    assert "54 pics" in albums[0]["name"]
    assert "/a/WZAAP8lE" in albums[0]["url"]
    assert albums[0]["icon"]

    # Check second album (videos only)
    assert "Trans Antonia" in albums[1]["name"]
    assert "7 vids" in albums[1]["name"]
    assert "/a/iiYfBuxx" in albums[1]["url"]

    # Check third album (both pics and vids)
    assert "Lisinha vagabunda" in albums[2]["name"]
    assert "1 pics" in albums[2]["name"]
    assert "3 vids" in albums[2]["name"]
    assert "/a/QdctxWQn" in albums[2]["url"]


def test_list_parses_pagination(monkeypatch):
    """Test that List correctly parses pagination."""
    html = load_fixture("explore_new.html")
    monkeypatch.setattr(erome.utils, "getHtml", lambda url, referer=None: html)

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(erome.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(erome.utils, "eod", lambda: None)

    erome.List("https://www.erome.com/explore/new")

    # Should have pagination
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1, "Expected pagination link"
    assert "page=2" in next_pages[0]["url"]
    assert "Page 1 of 50" in next_pages[0]["name"]


def test_list_handles_empty_html(monkeypatch):
    """Test that List handles empty HTML gracefully."""
    html = "<html><body><div id='albums'></div></body></html>"
    monkeypatch.setattr(erome.utils, "getHtml", lambda url, referer=None: html)

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append(name)

    monkeypatch.setattr(erome.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(erome.utils, "eod", lambda: None)

    erome.List("https://www.erome.com/explore/new")

    assert len(dirs) == 0, "Expected no entries for empty HTML"
