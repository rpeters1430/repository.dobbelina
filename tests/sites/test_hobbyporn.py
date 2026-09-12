"""Tests for hobbyporn site module"""

from resources.lib.sites import hobbyporn
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="item">
        <a href="/video/test/">
            <img src="https://cdn.hobbyporn.com/thumb1.jpg" />
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        hobbyporn.List("https://hobbyporn.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(hobbyporn.site, "search_dir") as mock_search:
        hobbyporn.Search("https://hobbyporn.com/search/")

        assert mock_search.called


def test_playvid_pornhub_embed_fallback(monkeypatch):
    played = []

    class DummyProgress:
        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

    class DummyVideoPlayer:
        def __init__(self, *args, **kwargs):
            self.progress = DummyProgress()

            class DummyResolve:
                def HostedMediaFile(self, url):
                    return False

            self.resolveurl = DummyResolve()

        def play_from_direct_link(self, url):
            played.append(url)

    def fake_get_html(url, *args, **kwargs):
        if "embed_player" in url:
            return ',"videoUrl":"https://phncdn.com/video720.mp4","quality":"720"'
        return '<iframe src="https://www.pornhub.com/embed_player?id=123">'

    monkeypatch.setattr(hobbyporn.utils, "VideoPlayer", DummyVideoPlayer)
    monkeypatch.setattr(hobbyporn.utils, "getHtml", fake_get_html)

    hobbyporn.Playvid("https://hobby.porn/video/123", "Test Video")

    assert len(played) == 1
    assert "https://phncdn.com/video720.mp4" in played[0]
    assert "Referer=https://www.pornhub.com/" in played[0]
