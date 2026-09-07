"""Tests for homemoviestube site module"""

from resources.lib.sites import homemoviestube
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video">
        <a href="/video/test/">
            <img src="https://cdn.homemoviestube.com/thumb1.jpg" />
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        homemoviestube.List("https://homemoviestube.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_list_parses_media_card_video_items(monkeypatch):
    html = """
    <div class="media-card video-card">
        <a href="/videos/sample-video.html">
            <img src="/thumbs/sample.jpg" title="Sample Video" />
            <span class="duration-badge">12:34</span>
        </a>
    </div>
    """
    downloads = []

    monkeypatch.setattr(homemoviestube.utils, "getHtml", lambda *args, **kwargs: html)
    monkeypatch.setattr(
        homemoviestube.site,
        "add_download_link",
        lambda name, url, mode, icon, desc, **kwargs: downloads.append(
            (name, url, mode, icon, kwargs.get("duration"))
        ),
    )
    monkeypatch.setattr(homemoviestube.utils, "eod", lambda: None)

    homemoviestube.List("https://www.homemoviestube.com/most-recent/")

    assert downloads == [
        (
            "Sample Video",
            "https://www.homemoviestube.com/videos/sample-video.html",
            "Playvid",
            "https://www.homemoviestube.com/thumbs/sample.jpg",
            "12:34",
        )
    ]


def test_playvid_normalizes_relative_media_url(monkeypatch):
    played = []

    class DummyProgress:
        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

    class DummyVideoPlayer:
        def __init__(self, *args, **kwargs):
            self.progress = DummyProgress()

        def play_from_direct_link(self, url):
            played.append(url)

    monkeypatch.setattr(homemoviestube.utils, "VideoPlayer", DummyVideoPlayer)
    monkeypatch.setattr(
        homemoviestube.utils,
        "getHtml",
        lambda *args, **kwargs: '<source src="/media/sample video.mp4">',
    )

    homemoviestube.Playvid(
        "https://www.homemoviestube.com/videos/sample.html", "Sample"
    )

    assert played == [
        "https://www.homemoviestube.com/media/sample%20video.mp4|verifypeer=false"
    ]


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(homemoviestube.site, "search_dir") as mock_search:
        homemoviestube.Search("https://homemoviestube.com/search/")

        assert mock_search.called
