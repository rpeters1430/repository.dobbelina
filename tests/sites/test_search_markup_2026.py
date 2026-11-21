"""Regression tests for the Nov 2026 markup changes that broke search (and often
the main listing) on these sites. Fixtures are real pages saved from each site.
"""

import importlib
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "sites"

# site, fixture, expected video count, first title, first url
CASES = [
    ("rule34video", "search_2026.html", 24, "SexEd", "https://rule34video.com/video/3116341/sexed/"),
    ("theyarehuge", "search_2026.html", 80, None, "https://www.theyarehuge.com/v/"),
    ("pornhd3x", "search_2026.html", 40, None, "https://pornhd3x.tv/movies/"),
    ("trannyteca", "search_2026.html", 32, None, "https://www.trannyteca.com/"),
    ("paradisehill", "search_2026.html", 18, "Sex Sex Sex 3", "https://en.paradisehill.cc/66fea1cb24ac6/"),
    ("mangoporn", "search_2026.html", 27, "Sex.", "https://mangoporn.net/movies/sex/"),
    (
        "nonktube",
        "search_2026.html",
        12,
        "Sex Art Babe Emily J fucking pleasures her tight Pussy",
        "https://nonktube.com/video/",
    ),
    ("tube8", "search_2026.html", 32, "Hottest Sex Scene", "https://www.tube8.com/porn-video/31862391/"),
]


def _capture(monkeypatch, mod, html):
    videos = []
    dirs = []
    monkeypatch.setattr(mod.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(mod.utils, "eod", lambda *a, **k: None)
    monkeypatch.setattr(mod.site, "add_download_link", lambda name, url, *a, **k: videos.append((name, url)))
    monkeypatch.setattr(mod.site, "add_dir", lambda name, url, *a, **k: dirs.append((name, url)))
    return videos, dirs


@pytest.mark.parametrize("site_name,fixture,count,first_title,first_url", CASES)
def test_list_parses_2026_markup(monkeypatch, site_name, fixture, count, first_title, first_url):
    mod = importlib.import_module("resources.lib.sites." + site_name)
    html = (FIXTURES / site_name / fixture).read_text(encoding="utf-8")
    videos, _ = _capture(monkeypatch, mod, html)

    mod.List(mod.site.url + "search/x/")

    assert len(videos) == count
    name, url = videos[0]
    if first_title:
        assert name == first_title
    assert url.startswith(first_url)
    assert all(n.strip() for n, _ in videos)


def test_javseen_loads_skeleton_pages_through_ajax(monkeypatch):
    """Pages ship placeholder cards and fill them from `?ajax=browse_videos`."""
    from resources.lib.sites import javseen

    skeleton = (FIXTURES / "javseen" / "skeleton_2026.html").read_text(encoding="utf-8")
    payload = (FIXTURES / "javseen" / "browse_videos_2026.json").read_text(encoding="utf-8")
    requested = []

    def fake_get_html(url, *a, **k):
        requested.append(url)
        return payload if "ajax=browse_videos" in url else skeleton

    videos, _ = _capture(monkeypatch, javseen, "")
    monkeypatch.setattr(javseen.utils, "getHtml", fake_get_html)

    javseen.List("https://javseen.tv/recent/")

    assert requested == ["https://javseen.tv/recent/", "https://javseen.tv/recent/?ajax=browse_videos"]
    assert len(videos) == 30
    assert all(u.startswith("https://javseen.tv/") for _, u in videos)


def test_tabootube_search_uses_search_block(monkeypatch):
    from resources.lib.sites import tabootube

    calls = []
    monkeypatch.setattr(tabootube, "List", lambda url, page=None: calls.append(url))
    tabootube.Search("https://www.tabootube.xxx/search/", "big tits")

    assert calls == [
        "https://www.tabootube.xxx/search/big-tits/?mode=async&function=get_block"
        "&block_id=list_videos_videos_list_search_result&q=big+tits&sort_by=post_date&from_videos=1"
    ]


def test_tube8_search_uses_searches_endpoint(monkeypatch):
    from resources.lib.sites import tube8

    calls = []
    monkeypatch.setattr(tube8, "List", lambda url: calls.append(url))
    tube8.Search("https://www.tube8.com/searches.html?q=", "big tits")

    assert calls == ["https://www.tube8.com/searches.html?q=big+tits"]
