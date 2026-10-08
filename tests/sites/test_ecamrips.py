"""Tests for ecamrips site implementation (real-page fixtures)."""

import os

import pytest

from resources.lib.sites import ecamrips
from tests.utils.site_harness import SiteRecorder

PAGES = {
    "play.php": "sites/ecamrips/play.html",
    "/show-cam-sex-movies/": "sites/ecamrips/video.html",
    "ecamrips.com/": "sites/ecamrips/listing.html",
}
VIDEO_URL = (
    "https://www.ecamrips.com/show-cam-sex-movies/"
    "2177014-lexy-and-mia-chaturbate-webcam-rip-20261008-062326.html"
)


@pytest.fixture(autouse=True)
def _thumb_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(ecamrips, "THUMB_DIR", str(tmp_path / "thumbs"))


def test_ecamrips_main(monkeypatch):
    rec = SiteRecorder(monkeypatch, ecamrips, PAGES)

    ecamrips.Main()

    assert rec.dirs_for("Search")
    assert rec.requests[0][0] == "https://www.ecamrips.com/en/"
    assert rec.videos


def test_ecamrips_list_writes_inline_thumbnails_to_disk(monkeypatch):
    rec = SiteRecorder(monkeypatch, ecamrips, PAGES)

    ecamrips.List("https://www.ecamrips.com/en/")

    assert len(rec.videos) == 2
    first = rec.videos[0]
    assert first["name"] == "maddyheart Chaturbate webcam rip 2026.10.08_07.18.25"
    assert first["url"] == (
        "https://www.ecamrips.com/show-cam-sex-movies/"
        "2177016-maddyheart-chaturbate-webcam-rip-20261008-071825.html"
    )
    assert first["duration"] == "00:40:19"

    # Thumbnails are base64 data URIs in the page; Kodi needs a real file.
    # The payload is WebP even though the page labels it image/png.
    assert os.path.basename(first["icon"]) == "2177016.webp"
    with open(first["icon"], "rb") as fh:
        head = fh.read(12)
    assert head[:4] == b"RIFF" and head[8:12] == b"WEBP"

    assert rec.next_page == "https://www.ecamrips.com/en/2-pg/"


def test_ecamrips_save_thumb_rejects_non_images():
    assert ecamrips._save_thumb("1", "https://example.com/a.jpg") == ""
    assert ecamrips._save_thumb("1", "data:image/png;base64,aGVsbG8=") == ""
    assert ecamrips._save_thumb("", "data:image/png;base64,UklGRg==") == ""


def test_ecamrips_prune_removes_stale_thumbs(tmp_path):
    os.makedirs(ecamrips.THUMB_DIR)
    stale = os.path.join(ecamrips.THUMB_DIR, "old.webp")
    fresh = os.path.join(ecamrips.THUMB_DIR, "new.webp")
    for path in (stale, fresh):
        with open(path, "wb") as fh:
            fh.write(b"x")
    os.utime(stale, (0, 0))

    ecamrips._prune_thumbs()

    assert not os.path.exists(stale)
    assert os.path.exists(fresh)


def test_ecamrips_playvid_follows_player_chain_with_referer(monkeypatch):
    rec = SiteRecorder(monkeypatch, ecamrips, PAGES)

    ecamrips.Playvid(VIDEO_URL, "Sample")

    # One request only: the id comes from the page URL, and play.php answers
    # with an empty body unless a same-site Referer is sent.
    assert rec.requests == [
        ("https://www.ecamrips.com/play.php?idd=2177014", VIDEO_URL)
    ]
    assert rec.played == [
        (
            "play_from_direct_link",
            "https://vidm.beramov.top/videos3/5/"
            "lexy_and_mia_-couple-_2026.10.08_06.23.26.mp4"
            "|Referer=https://www.ecamrips.com/",
        )
    ]
    assert not rec.notifications


def test_ecamrips_playvid_falls_back_to_page_iframe(monkeypatch):
    rec = SiteRecorder(
        monkeypatch,
        ecamrips,
        {
            "play.php": "sites/ecamrips/play.html",
            "ecamrips.com/": "sites/ecamrips/video.html",
        },
    )
    url = "https://www.ecamrips.com/en/some-renamed-video-page.html"

    ecamrips.Playvid(url, "Sample")

    assert [r[0] for r in rec.requests] == [
        url,
        "https://www.ecamrips.com/play.php?idd=2177014&vv=273092459",
    ]
    assert rec.played and rec.played[0][0] == "play_from_direct_link"


def test_ecamrips_playvid_empty_player_notifies(monkeypatch):
    pages = dict(PAGES)
    del pages["play.php"]
    rec = SiteRecorder(monkeypatch, ecamrips, pages)

    ecamrips.Playvid(VIDEO_URL, "Sample")

    assert rec.played == []
    assert rec.notifications


def test_ecamrips_search_opens_model_page(monkeypatch):
    rec = SiteRecorder(monkeypatch, ecamrips, PAGES)

    ecamrips.Search("https://www.ecamrips.com/model/en/{0}/", "lexy and mia")

    assert rec.requests[0][0] == "https://www.ecamrips.com/model/en/lexy_and_mia/"
    assert rec.videos
