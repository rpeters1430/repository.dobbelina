"""Tests for xhuzz site implementation (real-page fixtures)."""

from resources.lib.sites import xhuzz
from tests.utils.site_harness import SiteRecorder

PAGES = {
    "/categories": "sites/xhuzz/categories.html",
    "/video/": "sites/xhuzz/video.html",
    "xhuzz.com/": "sites/xhuzz/listing.html",
}


def test_xhuzz_main_lists_home_page(monkeypatch):
    rec = SiteRecorder(monkeypatch, xhuzz, PAGES)

    xhuzz.Main()

    assert rec.dirs_for("Categories")
    assert rec.dirs_for("Search")
    # /videos is a 404 on the live site; the home page is the listing.
    assert rec.requests[0][0] == "https://xhuzz.com/"
    assert rec.videos


def test_xhuzz_list(monkeypatch):
    rec = SiteRecorder(monkeypatch, xhuzz, PAGES)

    xhuzz.List("https://xhuzz.com/")

    assert len(rec.videos) == 6
    urls = [v["url"] for v in rec.videos]
    assert len(set(urls)) == len(urls)
    first = rec.videos[0]
    assert first["name"] == "Christina Khalil Pussy Clit Close Up Video"
    assert first["url"] == (
        "https://xhuzz.com/video/christina-khalil-pussy-clit-close-up-video"
    )
    assert first["icon"].startswith("https://xhuzz.com/thumbnail/")
    assert rec.next_page == "https://xhuzz.com/?page=2"


def test_xhuzz_categories(monkeypatch):
    rec = SiteRecorder(monkeypatch, xhuzz, PAGES)

    xhuzz.Categories("https://xhuzz.com/categories")

    cats = rec.dirs_for("List")
    assert [c["name"] for c in cats] == [
        "Sex Tape",
        "Threesome",
        "Boy Girl",
        "Striptease",
    ]
    assert cats[0]["url"] == "https://xhuzz.com/category/sex-tape"
    assert cats[0]["icon"].startswith("https://xhuzz.com/thumbnail/")


def test_xhuzz_playvid_resolves_hoster_buttons(monkeypatch):
    rec = SiteRecorder(monkeypatch, xhuzz, PAGES)

    xhuzz.Playvid("https://xhuzz.com/video/sample", "Sample")

    assert len(rec.played) == 1
    method, links = rec.played[0]
    assert method == "play_from_link_list"
    assert links[0] == "https://streamtape.com/e/PDGdWaZ11ghL9W"
    assert "https://voe.sx/e/ubx1fcyjd5nd" in links
    assert not rec.notifications


def test_xhuzz_playvid_without_sources_notifies(monkeypatch):
    rec = SiteRecorder(monkeypatch, xhuzz, {})

    xhuzz.Playvid("https://xhuzz.com/video/sample", "Sample")

    assert rec.played == []
    assert rec.notifications


def test_xhuzz_search(monkeypatch):
    rec = SiteRecorder(monkeypatch, xhuzz, PAGES)

    xhuzz.Search("https://xhuzz.com/search?q={0}", "two words")

    assert rec.requests[0][0] == "https://xhuzz.com/search?q=two+words"
    assert rec.videos
