"""Comprehensive tests for hentaistream site implementation."""

from pathlib import Path

from resources.lib.sites import hentaistream


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "hentaistream"


def load_fixture(name):
    """Load a fixture file from the hentaistream fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List() correctly parses video items using BeautifulSoup."""
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(
        name, url, mode, iconimage, desc="", fanart=None, quality="", **kwargs
    ):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "fanart": fanart,
                "quality": quality,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hentaistream.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hentaistream.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Call List
    hentaistream.List("https://tube.hentaistream.com/")

    # Verify we got 3 videos
    assert len(downloads) == 3

    # Verify first video
    assert downloads[0]["name"] == "Sample Anime Episode 1"
    assert "sample-anime-1" in downloads[0]["url"]
    assert "cover-ep-1" in downloads[0]["icon"]


def test_list_handles_pagination(monkeypatch):
    """Test that List() correctly handles pagination."""
    html = load_fixture("list.html")

    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hentaistream.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hentaistream.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Call List
    hentaistream.List("https://tube.hentaistream.com/")

    # Verify pagination was added
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "page/2" in next_pages[0]["url"]


def test_genres_parses_links(monkeypatch):
    """Test that Genres() correctly parses tag labels using BeautifulSoup."""
    html = '<html><ul class="genres"><li><a href="/list/ahegao">Ahegao</a></li><li><a href="/list/milf">MILF</a></li></ul></html>'

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Call Genres
    hentaistream.Genres("https://tube.hentaistream.com/genres")

    # Verify we got 2 genres
    assert len(dirs) == 2
    assert dirs[0]["name"] == "Ahegao"
    assert "ahegao" in dirs[0]["url"]


def test_playvid_handles_iframe(monkeypatch):
    """Test that Playvid() correctly finds iframe."""
    html = '<html><iframe src="https://player.com/embed/123"></iframe></html>'

    played = {}

    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type("obj", (object,), {"update": lambda *a: None, "close": lambda: None})()
        def play_from_link_to_resolve(self, url):
            played["url"] = url

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaistream.utils, "VideoPlayer", MockVideoPlayer)

    # Call Playvid
    hentaistream.Playvid("https://tube.hentaistream.com/video", "Test Video")

    assert played["url"] == "https://player.com/embed/123"
