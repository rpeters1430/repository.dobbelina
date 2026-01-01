"""Tests for celebsroulette BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import celebsroulette


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "celebsroulette"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(celebsroulette.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(celebsroulette.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url, "icon": iconimage})

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url})

    monkeypatch.setattr(celebsroulette.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(celebsroulette.site, "add_dir", fake_add_dir)

    celebsroulette.List("https://celebsroulette.com/latest-updates/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Clip"
    assert downloads[0]["url"] == "https://celebsroulette.com/videos/first"
    assert downloads[1]["url"].endswith("/videos/second")
    assert any("Next Page" in d["name"] for d in dirs)


def test_listpl_parses_items(monkeypatch):
    html = load_fixture("listpl.html")
    downloads = []

    monkeypatch.setattr(celebsroulette.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(celebsroulette.utils, "eod", lambda: None)
    monkeypatch.setattr(
        celebsroulette.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc, **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(celebsroulette.site, "add_dir", lambda *a, **k: None)

    celebsroulette.ListPL("https://celebsroulette.com/playlists/?from=01")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Playlist One"
    assert downloads[1]["url"].endswith("playlist-2")


def test_playlist_parses_items(monkeypatch):
    html = load_fixture("playlist.html")
    dirs = []

    monkeypatch.setattr(celebsroulette.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(celebsroulette.utils, "eod", lambda: None)
    monkeypatch.setattr(
        celebsroulette.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    celebsroulette.Playlist("https://celebsroulette.com/playlists/")

    assert len(dirs) == 2
    assert "Alpha" in dirs[0]["name"]
    assert dirs[1]["url"].startswith("https://celebsroulette.com/playlist/beta")
