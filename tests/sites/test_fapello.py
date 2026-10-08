"""Tests for fapello site implementation (real-page fixtures)."""

from resources.lib.sites import fapello
from tests.utils.site_harness import SiteRecorder

PAGES = {
    "/search/": "sites/fapello/search.html",
    "/video/": "sites/fapello/video.html",
    "/bobbie-moore-1/82/": "sites/fapello/post.html",
    "/bobbie-moore-1/": "sites/fapello/model.html",
    "fapello.com/": "sites/fapello/listing.html",
}


def test_fapello_main(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.Main()

    assert rec.dirs_for("Popular")
    assert rec.dirs_for("Search")
    assert rec.requests[0][0] == "https://fapello.com/videos/"
    assert rec.videos


def test_fapello_popular_periods(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.Popular("https://fapello.com/popular_videos/")

    urls = [d["url"] for d in rec.dirs_for("List")]
    assert "https://fapello.com/popular_videos/week/" in urls
    assert "https://fapello.com/popular_videos/all_time/" in urls


def test_fapello_list_names_cards_and_skips_ads(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.List("https://fapello.com/videos/")

    # Five cards in the fixture: one sponsored OnlyFans profile, four videos.
    assert len(rec.videos) == 4
    assert all("/video/" in v["url"] for v in rec.videos)
    first = rec.videos[0]
    # Cards carry no title, so the model name and post number are used.
    assert first["name"] == "Dear Chuu #112"
    assert first["url"] == "https://fapello.com/video/new/32551320/"
    assert first["icon"] == (
        "https://fapello.com/content/d/e/dear-chuu-4/1000/dear-chuu-4_0112_300px.jpg"
    )
    assert rec.next_page == "https://fapello.com/videos/page-2/"


def test_fapello_search_lists_models(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.Search("https://fapello.com/search/{0}/", "lea martinez")

    assert rec.requests[0][0] == "https://fapello.com/search/lea-martinez/"
    models = rec.dirs_for("Model")
    assert [m["url"] for m in models] == [
        "https://fapello.com/bobbie-ann/",
        "https://fapello.com/bobbie-sweets/",
        "https://fapello.com/bobby/",
    ]
    assert models[0]["name"] == "Bobbie Ann"


def test_fapello_model_lists_only_video_posts(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.Model("https://fapello.com/bobbie-moore-1/")

    assert [v["url"] for v in rec.videos] == [
        "https://fapello.com/bobbie-moore-1/82/",
        "https://fapello.com/bobbie-moore-1/72/",
        "https://fapello.com/bobbie-moore-1/59/",
    ]
    assert rec.videos[0]["name"] == "Bobbie Moore #82"
    assert rec.next_page == "https://fapello.com/bobbie-moore-1/page-2/"


def test_fapello_playvid_feed_page(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.Playvid("https://fapello.com/video/new/32550822/", "Sample")

    assert rec.played == [
        (
            "play_from_direct_link",
            "https://cdn.fapello.com/content/b/o/bobbie-moore-1/1000/"
            "bobbie-moore-1_0082.mp4|Referer=https://fapello.com/",
        )
    ]


def test_fapello_playvid_post_page(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, PAGES)

    fapello.Playvid("https://fapello.com/bobbie-moore-1/82/", "Sample")

    assert rec.played == [
        (
            "play_from_direct_link",
            "https://cdn.fapello.com/content/b/o/bobbie-moore-1/1000/"
            "bobbie-moore-1_0082.mp4|Referer=https://fapello.com/",
        )
    ]


def test_fapello_playvid_without_source_notifies(monkeypatch):
    rec = SiteRecorder(monkeypatch, fapello, {})

    fapello.Playvid("https://fapello.com/video/new/1/", "Sample")

    assert rec.played == []
    assert rec.notifications
