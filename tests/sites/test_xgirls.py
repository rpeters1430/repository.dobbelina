"""Tests for xgirls site implementation (real-page fixtures)."""

from resources.lib.sites import xgirls
from tests.utils.site_harness import SiteRecorder

PAGES = {
    "/categories/": "sites/xgirls/categories.html",
    "/search/": "sites/xgirls/search.html",
    "/video/": "sites/xgirls/video.html",
    "/latest-updates/": "sites/xgirls/listing.html",
}


def test_xgirls_main(monkeypatch):
    rec = SiteRecorder(monkeypatch, xgirls, PAGES)

    xgirls.Main()

    assert rec.dirs_for("Categories")
    assert rec.dirs_for("Search")
    assert rec.requests[0][0] == "https://xgirls.webcam/latest-updates/"


def test_xgirls_list_uses_main_grid_only(monkeypatch):
    rec = SiteRecorder(monkeypatch, xgirls, PAGES)

    xgirls.List("https://xgirls.webcam/latest-updates/")

    # The fixture also holds three header teaser cards (a.drop-card) whose
    # images are all alt="image"; they must not be listed.
    assert len(rec.videos) == 4
    urls = [v["url"] for v in rec.videos]
    assert len(set(urls)) == 4
    assert all(v["name"] != "image" for v in rec.videos)
    assert not any("/video/50547/" in u for u in urls)

    first = rec.videos[0]
    assert first["name"] == "kathariine webcam video 2026-10-08 0030"
    assert first["url"] == (
        "https://xgirls.webcam/video/50540/kathariine-webcam-video-2026-10-08-0030/"
    )
    assert first["icon"] == (
        "https://xgirls.webcam/contents/videos_screenshots/50000/50540/320x180/3.jpg"
    )
    assert first["duration"] == "8:01"
    assert first["quality"] == "HD"
    assert rec.next_page == "https://xgirls.webcam/latest-updates/2/"


def test_xgirls_search_pagination_uses_async_block(monkeypatch):
    rec = SiteRecorder(monkeypatch, xgirls, PAGES)

    xgirls.Search("https://xgirls.webcam/search/{0}/", "anal")

    assert rec.requests[0][0] == "https://xgirls.webcam/search/anal/"
    assert len(rec.videos) == 3
    # The search "Next" link is href="#search"; the page number only exists
    # in the KVS ajax parameters.
    assert rec.next_page == (
        "https://xgirls.webcam/search/anal/?mode=async&function=get_block"
        "&block_id=list_videos_videos_list_search_result"
        "&q=anal&from_videos=2&from_albums=2"
    )


def test_xgirls_categories(monkeypatch):
    rec = SiteRecorder(monkeypatch, xgirls, PAGES)

    xgirls.Categories("https://xgirls.webcam/categories/")

    cats = rec.dirs_for("List")
    assert len(cats) == 4
    assert cats[0]["name"].startswith("Booty")
    assert cats[0]["url"] == "https://xgirls.webcam/categories/booty/"


def test_xgirls_playvid_uses_kt_player(monkeypatch):
    rec = SiteRecorder(monkeypatch, xgirls, PAGES)
    url = "https://xgirls.webcam/video/50547/yesonee-webcam-video-2026-10-08-0040/"

    xgirls.Playvid(url, "Sample")

    assert len(rec.played) == 1
    assert rec.played[0][0] == "play_from_kt_player"
    html, referer = rec.player.play_from_kt_player.call_args[0]
    assert "video_alt_url" in html
    assert referer == url


def test_xgirls_playvid_direct_source_fallback(monkeypatch):
    rec = SiteRecorder(monkeypatch, xgirls, {})
    monkeypatch.setattr(
        xgirls.utils,
        "getHtml",
        lambda *a, **k: '<video><source src="/media/clip.mp4"></video>',
    )

    xgirls.Playvid("https://xgirls.webcam/video/1/x/", "Sample")

    assert rec.played == [
        (
            "play_from_direct_link",
            "https://xgirls.webcam/media/clip.mp4|Referer=https://xgirls.webcam/",
        )
    ]
