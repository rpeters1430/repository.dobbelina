from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import pornmd


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites"


def _load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_pornmd_list_parses_videos_and_pagination(monkeypatch):
    html = _load_fixture("pornmd_list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(pornmd.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, False))
    monkeypatch.setattr(
        pornmd.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(
        pornmd.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornmd.utils, "eod", lambda: None)

    pornmd.List("https://www.pornmd.com/new")

    assert downloads == [
        {
            "name": "Lesbian girlfriends explore nature and each other's bodies",
            "url": "https://dykehq.com/video/404431/lesbian-girlfriends-explore-nature-and-each-other-s-bodies/?utm_campaign=tf",
            "icon": "https://c2.ttcache.com/thumbnail/l61muWT5JQI/288x162/1.jpg",
        },
        {
            "name": "Lesbian trio gets kinky at the party",
            "url": "https://dykehq.com/video/404430/lesbian-trio-gets-kinky-at-the-party/?utm_campaign=tf",
            "icon": "https://c3.ttcache.com/thumbnail/lhnoOtt5kS7/288x162/1.jpg",
        },
        {
            "name": "Three hot blondes get it on in a lesbian threesome.",
            "url": "https://dykehq.com/video/404427/three-hot-blondes-get-it-on-in-a-lesbian-threesome/?utm_campaign=tf",
            "icon": "https://c3.ttcache.com/thumbnail/KrSzCJw17bV/288x162/1.jpg",
        },
    ]
    assert dirs == [
        {
            "name": "Next Page",
            "url": "https://www.pornmd.com/new?page=2",
            "mode": "List",
        }
    ]


def test_pornmd_search_uses_live_path(monkeypatch):
    called_urls = []
    monkeypatch.setattr(pornmd, "List", lambda url: called_urls.append(url))

    pornmd.Search("https://www.pornmd.com/searching/", keyword="big tits")

    assert called_urls == ["https://www.pornmd.com/searching/?queryString=big%20tits"]


def test_pornmd_main_uses_videos_url(monkeypatch):
    called_urls = []
    dirs = []

    monkeypatch.setattr(pornmd, "List", lambda url: called_urls.append(url))
    monkeypatch.setattr(pornmd.utils, "eod", lambda: None)
    monkeypatch.setattr(
        pornmd.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    pornmd.Main()

    assert called_urls == ["https://www.pornmd.com/new"]
    assert len(dirs) == 4
    assert dirs[0]["name"] == "[COLOR hotpink]Popular[/COLOR]"
    assert dirs[0]["url"] == "https://www.pornmd.com/popular"
    assert dirs[1]["name"] == "[COLOR hotpink]New[/COLOR]"
    assert dirs[1]["url"] == "https://www.pornmd.com/new"
    assert dirs[2]["name"] == "[COLOR hotpink]Top Rated[/COLOR]"
    assert dirs[2]["url"] == "https://www.pornmd.com/rating"
    assert dirs[3]["name"] == "[COLOR hotpink]Search[/COLOR]"
    assert dirs[3]["url"] == "https://www.pornmd.com/searching/"
