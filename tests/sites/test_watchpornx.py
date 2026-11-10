"""Tests for watchpornx site implementation."""

from pathlib import Path
from unittest.mock import Mock

from resources.lib.sites import watchpornx

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "watchpornx"


def load_fixture(name):
    """Load a fixture file from the watchpornx fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
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

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(watchpornx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(watchpornx.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(watchpornx.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(watchpornx.utils, "eod", lambda: None)

    watchpornx.List("https://watchpornx.com/adult")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Sample Movie 1 [COLOR hotpink](2026)[/COLOR]"
    assert downloads[0]["url"] == "https://watchpornx.com/adult/sample-movie-1-watch-xxx-porn-online-free"
    assert downloads[0]["duration"] == "31:00"
    assert downloads[0]["icon"] == "https://i1.wp.com/pandanetwork.club/sample1.jpg"

    assert downloads[1]["name"] == "Sample Movie 2 [COLOR hotpink](HD)[/COLOR]"
    assert downloads[1]["duration"] == "45:10"
    assert downloads[1]["icon"] == "https://i1.wp.com/pandanetwork.club/sample2.jpg"

    assert len(dirs) == 1
    assert "Next Page..." in dirs[0]["name"]
    assert dirs[0]["url"] == "https://watchpornx.com/adult/page/2"


def test_categories_parsing(monkeypatch):
    """Test that Categories parses chip elements."""
    html = """
    <div class="chips">
        <a class="chip" href="https://watchpornx.com/adult/genre/anal">Anal<small>42</small></a>
        <a class="chip" href="https://watchpornx.com/adult/genre/milf">Milf<small>108</small></a>
    </div>
    """
    dirs = []

    def fake_get_html(url, *args):
        if "?pg=" in url:
            return ""
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(watchpornx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(watchpornx.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(watchpornx.utils, "eod", lambda: None)

    watchpornx.Categories("https://watchpornx.com/adult/porn-genres")

    assert len(dirs) == 2
    assert "Anal [COLOR hotpink](42)[/COLOR]" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://watchpornx.com/adult/genre/anal"


def test_studios_parsing(monkeypatch):
    """Test that Studios parses tcard elements."""
    html = """
    <div class="tcards">
        <a class="tcard" href="https://watchpornx.com/adult/studios/brazzers">
            <img src="https://i1.wp.com/pandanetwork.club/brazzers.jpg" alt="Brazzers" />
            <small>500 movies</small>
        </a>
    </div>
    """
    dirs = []

    def fake_get_html(url, *args):
        return html

    def fake_add_dir(name, url, mode, iconimage=None):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(watchpornx.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(watchpornx.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(watchpornx.utils, "next_page", lambda *args, **kwargs: None)
    monkeypatch.setattr(watchpornx.utils, "eod", lambda: None)

    watchpornx.Studios("https://watchpornx.com/adult/studios")

    assert len(dirs) == 1
    assert "Brazzers [COLOR hotpink](500 movies)[/COLOR]" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://watchpornx.com/adult/studios/brazzers"
    assert dirs[0]["icon"] == "https://i1.wp.com/pandanetwork.club/brazzers.jpg"


def test_playvid_direct_server(monkeypatch):
    """Test Playvid parses servers and resolves correctly."""
    html = """
    <section class="hlm" data-post="123" data-rest="https://watchpornx.com/wp-json/hlm/v1/"
             data-servers='[{"u":"https://luluvido.com/e/123","l":"LuluStream"}]'>
    </section>
    """
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = html

    class MockSession:
        def __init__(self):
            self.headers = {}

        def get(self, url, **kwargs):
            return mock_resp

    monkeypatch.setattr(watchpornx.requests, "Session", MockSession)
    monkeypatch.setattr(watchpornx.utils.addon, "getSetting", lambda k: "true" if k == "dontask" else "false")

    resolved = []

    class MockVP:
        def __init__(self, name, download=None):
            self.name = name

        def play_from_link_to_resolve(self, link):
            resolved.append(link)
            return True

    monkeypatch.setattr(watchpornx.utils, "VideoPlayer", MockVP)

    watchpornx.Playvid("https://watchpornx.com/adult/sample-movie", "Sample Movie")

    assert len(resolved) == 1
    assert resolved[0] == "https://luluvido.com/e/123"
