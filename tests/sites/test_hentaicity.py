"""Tests for hentaicity site implementation (real-page fixtures)."""

from resources.lib.sites import hentaicity
from tests.utils.site_harness import SiteRecorder

PAGES = {
    "/categories/": "sites/hentaicity/categories.html",
    "/video/": "sites/hentaicity/video.html",
    "hentaicity.com/": "sites/hentaicity/listing.html",
}


def test_hentaicity_main(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentaicity, PAGES)

    hentaicity.Main()

    assert rec.dirs_for("Categories")
    assert rec.dirs_for("Search")
    assert rec.requests[0][0] == "https://www.hentaicity.com/videos/"


def test_hentaicity_list(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentaicity, PAGES)

    hentaicity.List("https://www.hentaicity.com/videos/")

    assert len(rec.videos) == 6
    first = rec.videos[0]
    assert first["name"] == (
        "Weak Teacher 3 (ecchi anime) - Busty teacher wears bunny outfit"
    )
    # The /click/1-1/ tracking redirect is stripped from listing links.
    assert first["url"] == (
        "https://www.hentaicity.com/video/"
        "weak-teacher-3-ecchi-anime-busty-teacher-wears-bunny-outfit-5MMx2sxWOn2.html"
    )
    assert first["icon"] == (
        "https://cdn1.images.hentaicity.com/videos/0822/38137/main.jpg"
    )
    assert first["duration"] == "23:42"
    assert rec.next_page == "https://www.hentaicity.com/videos/all-recent-2.html"


def test_hentaicity_categories_skip_galleries(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentaicity, PAGES)

    hentaicity.Categories("https://www.hentaicity.com/categories/")

    cats = rec.dirs_for("List")
    assert [c["name"] for c in cats] == ["3D", "Anal", "Babe", "Big Dick"]
    assert all("/videos/" in c["url"] for c in cats)
    assert cats[0]["url"] == (
        "https://www.hentaicity.com/videos/straight/3d-popular.html"
    )


def test_hentaicity_playvid_plays_hls_master(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentaicity, PAGES)

    hentaicity.Playvid("https://www.hentaicity.com/video/sample.html", "Sample")

    assert len(rec.played) == 1
    method, link = rec.played[0]
    assert method == "play_from_direct_link"
    assert link.startswith("https://hls.hentaicity.com/_hls/flv/0822/38137/")
    assert "master.m3u8?validfrom=" in link
    assert "&amp;" not in link
    assert link.endswith("|Referer=https://www.hentaicity.com/")


def test_hentaicity_playvid_without_source_notifies(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentaicity, {})

    hentaicity.Playvid("https://www.hentaicity.com/video/sample.html", "Sample")

    assert rec.played == []
    assert rec.notifications


def test_hentaicity_search(monkeypatch):
    rec = SiteRecorder(monkeypatch, hentaicity, PAGES)

    hentaicity.Search(
        "https://www.hentaicity.com/customsearch.php?search={0}&search_type=video",
        "two words",
    )

    assert rec.requests[0][0] == (
        "https://www.hentaicity.com/customsearch.php"
        "?search=two+words&search_type=video"
    )
    assert rec.videos
