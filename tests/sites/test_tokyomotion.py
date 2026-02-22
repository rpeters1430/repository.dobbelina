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

    assert captured_dirs == [
        {
            "name": "[COLOR hotpink]Latest[/COLOR]",
            "url": "https://www.tokyomotion.net/videos?type=public&o=mr&page=1",
            "mode": "tokyomotion.List",
        },
        {
            "name": "[COLOR hotpink]Categories[/COLOR]",
            "url": "https://www.tokyomotion.net/categories",
            "mode": "tokyomotion.Categories",
        },
        {
            "name": "[COLOR hotpink]Search[/COLOR]",
            "url": "https://www.tokyomotion.net/search?search_query={}&search_type=videos",
            "mode": "tokyomotion.Search",
        },
    ]


def test_list_parses_downloads_and_next_page(monkeypatch):
    html = read_fixture("tokyomotion_list.html")
    captured_downloads = []
    captured_dirs = []

    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, ref=None: html)
    monkeypatch.setattr(tokyomotion.utils, "eod", lambda *args, **kwargs: None)

    def add_download(name, url, mode, iconimage, desc="", *args, **kwargs):
        captured_downloads.append(
            {
                "name": name,
                "url": url,
                "mode": tokyomotion.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
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

    assert captured_downloads == [
        {
            "name": "First Video",
            "url": "https://www.tokyomotion.net/video/abc123",
            "mode": "tokyomotion.Playvid",
            "icon": tokyomotion.site.image,
            "duration": "10:01",
            "quality": "HD",
        },
        {
            "name": "Second Clip",
            "url": "https://www.tokyomotion.net/video/def456",
            "mode": "tokyomotion.Playvid",
            "icon": tokyomotion.site.image,
            "duration": "05:59",
            "quality": "",
        },
    ]

    assert captured_dirs == [
        {
            "name": "Next Page (2)",
            "url": "https://www.tokyomotion.net/videos?type=public&o=mr&page=2",
            "mode": "tokyomotion.List",
        },
    ]


def test_playvid_uses_source_tag(monkeypatch):
    html = read_fixture("tokyomotion_video.html")
    played = {}

    monkeypatch.setattr(tokyomotion.utils, "getHtml", lambda url, ref=None: html)

    class DummyVP:
        def __init__(self, name, download):
            self.name = name
            self.download = download

        def play_from_direct_link(self, url):
            played["url"] = url

    monkeypatch.setattr(tokyomotion.utils, "VideoPlayer", DummyVP)

    tokyomotion.Playvid("https://www.tokyomotion.net/video/abc123", "First Video")

    assert (
        played["url"]
        == "https://cdn.tokyo-motion.net/videos/abc123.m3u8|Referer=https://www.tokyomotion.net/"
    )
