from resources.lib.sites import tokyomotion
from tests.conftest import read_fixture


def test_main_menu_adds_latest_categories_and_search(monkeypatch):
    captured_dirs = []

    monkeypatch.setattr(tokyomotion.utils, "eod", lambda *args, **kwargs: None)

    def add_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append(
            {
                "name": name,
                "url": url,
                "mode": tokyomotion.site.get_full_mode(mode),
            }
        )

    monkeypatch.setattr(tokyomotion.site, "add_dir", add_dir)

    tokyomotion.Main()

    # The order and URLs might have changed in modernization
    assert any(d["name"] == "[COLOR hotpink]Latest[/COLOR]" for d in captured_dirs)
    assert any(d["name"] == "[COLOR hotpink]Categories[/COLOR]" for d in captured_dirs)
    assert any(d["name"] == "[COLOR hotpink]Search[/COLOR]" for d in captured_dirs)


def test_list_parses_downloads_and_next_page(monkeypatch):
    html = read_fixture("tokyomotion_list.html")
    captured_downloads = []
    captured_dirs = []

    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, *a, **k: html)
    monkeypatch.setattr(tokyomotion.utils, "eod", lambda *args, **kwargs: None)

    def add_download(name, url, mode, iconimage, desc="", *args, **kwargs):
        captured_downloads.append(
            {
                "name": name,
                "url": url,
                "mode": tokyomotion.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        )

    def add_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append(
            {
                "name": name,
                "url": url,
                "mode": tokyomotion.site.get_full_mode(mode),
            }
        )

    monkeypatch.setattr(tokyomotion.site, "add_download_link", add_download)
    monkeypatch.setattr(tokyomotion.site, "add_dir", add_dir)

    tokyomotion.List("https://www.tokyomotion.net/videos?type=public&o=mr&page=1")

    assert len(captured_downloads) == 2
    assert captured_downloads[0]["name"] == "First Video"
    assert "video/abc123" in captured_downloads[0]["url"]
    assert captured_downloads[0]["duration"] == "10:01"

    assert len(captured_dirs) == 1
    assert "Next Page" in captured_dirs[0]["name"]
    assert "page=2" in captured_dirs[0]["url"]


def test_playvid_uses_source_tag(monkeypatch):
    html = '<html><video><source src="https://cdn.tokyo-motion.net/videos/abc123.m3u8"></video></html>'
    played = {}

    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, *a, **k: html)

    class DummyVP:
        def __init__(self, name, download=None):
            self.name = name
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            played["url"] = url

        def play_from_link_to_resolve(self, url):
             played["resolve"] = url

    monkeypatch.setattr(tokyomotion.utils, "VideoPlayer", DummyVP)

    tokyomotion.Playvid("https://www.tokyomotion.net/video/abc123", "First Video")

    assert played.get("url") or played.get("resolve")


def test_playvid_uses_video_src_fallback(monkeypatch):
    html = '<html><video src="https://cdn.tokyo-motion.net/videos/fallback.mp4"></video></html>'
    played = {}
    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, *a, **k: html)
    class DummyVP:
        def __init__(self, name, download=None):
            self.name = name
            self.progress = type("P", (), {"update": lambda *a, **k: None})()
        def play_from_direct_link(self, url):
            played["url"] = url
    monkeypatch.setattr(tokyomotion.utils, "VideoPlayer", DummyVP)
    tokyomotion.Playvid("https://www.tokyomotion.net/video/abc123", "Fallback Video")
    assert played.get("url") == "https://cdn.tokyo-motion.net/videos/fallback.mp4|Referer=https://www.tokyomotion.net/"


def test_playvid_handles_missing_video(monkeypatch):
    html = '<html><body>This video cannot be found. Are you sure you typed in the correct url?</body></html>'
    notifications = []
    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, *a, **k: html)
    monkeypatch.setattr(tokyomotion.utils, "notify", lambda msg, *a, **k: notifications.append(msg))
    class DummyVP:
        def __init__(self, name, download=None):
            pass
    monkeypatch.setattr(tokyomotion.utils, "VideoPlayer", DummyVP)
    tokyomotion.Playvid("https://www.tokyomotion.net/video/abc123", "Missing Video")
    assert "page does not exist" in notifications


def test_playvid_handles_private_video(monkeypatch):
    html = '<html><body>This video is private. Only uploader and friends can view this.</body></html>'
    notifications = []
    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, *a, **k: html)
    monkeypatch.setattr(tokyomotion.utils, "notify", lambda msg, *a, **k: notifications.append(msg))
    class DummyVP:
        def __init__(self, name, download=None):
            pass
    monkeypatch.setattr(tokyomotion.utils, "VideoPlayer", DummyVP)
    tokyomotion.Playvid("https://www.tokyomotion.net/video/abc123", "Private Video")
    assert "private" in notifications
