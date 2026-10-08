"""Tests for hentai2w site implementation (real-page fixtures)."""

from resources.lib.sites import hentai2w
from tests.utils.site_harness import SiteRecorder

PAGES = {
    "/channels/": "sites/hentai2w/categories.html",
    "/video/": "sites/hentai2w/video.html",
    "hentai2w.com/": "sites/hentai2w/listing.html",
}


def test_hentai2w_main(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentai2w, PAGES)

    hentai2w.Main()

    cats = rec.dirs_for("Categories")
    # /categories/ does not exist on the site; categories live under /channels/.
    assert cats[0]["url"] == "https://hentai2w.com/channels/"
    assert rec.dirs_for("Search")
    assert rec.requests[0][0] == "https://hentai2w.com/videos/"


def test_hentai2w_list(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentai2w, PAGES)

    hentai2w.List("https://hentai2w.com/videos/page2.html")

    assert len(rec.videos) == 4
    first = rec.videos[0]
    assert first["name"] == (
        "Tsuma Netori Rei: Boku no Ayamachi Kanojo no Sentaku - Episode 1"
    )
    assert first["url"] == (
        "https://hentai2w.com/video/"
        "tsuma-netori-rei-boku-no-ayamachi-kanojo-no-sentaku-episode-1-6231.html"
    )
    assert first["icon"].startswith("https://media.hentai2w.com/thumbs/")
    assert first["duration"] == "27:17"
    assert first["quality"] == "HD"
    # "page3.html" is relative to the listing directory, not the site root.
    assert rec.next_page == "https://hentai2w.com/videos/page3.html"


def test_hentai2w_list_keeps_query_when_paginating(monkeypatch):
    rec = SiteRecorder(
        monkeypatch, hentai2w, {"hentai2w.com/": "sites/hentai2w/listing.html"}
    )

    hentai2w.List("https://hentai2w.com/channels/162/adult/?type=videos")

    assert rec.next_page == (
        "https://hentai2w.com/channels/162/adult/page3.html?type=videos"
    )


def test_hentai2w_categories(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentai2w, PAGES)

    hentai2w.Categories("https://hentai2w.com/channels/")

    cats = rec.dirs_for("List")
    assert [c["name"] for c in cats] == [
        "1000giri",
        "3D",
        "Adult",
        "Adult Source Media",
    ]
    assert cats[0]["url"] == "https://hentai2w.com/channels/170/1000giri/?type=videos"


def test_hentai2w_playvid(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentai2w, PAGES)

    hentai2w.Playvid("https://hentai2w.com/video/sample-6352.html", "Sample")

    assert rec.played == [
        (
            "play_from_direct_link",
            "https://media.hentai2w.com/videos/6/8/a/e/6/"
            "68ae69f29f49e-kanochi-x-netorare-kazoku-2-1080p-h1x.mp4"
            "|Referer=https://hentai2w.com/",
        )
    ]
    assert not rec.notifications


def test_hentai2w_playvid_without_source_notifies(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentai2w, {})

    hentai2w.Playvid("https://hentai2w.com/video/sample-1.html", "Sample")

    assert rec.played == []
    assert rec.notifications


def test_hentai2w_search(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentai2w, PAGES)

    hentai2w.Search("https://hentai2w.com/search/{0}/", "teacher")

    assert rec.requests[0][0] == "https://hentai2w.com/search/teacher/"
