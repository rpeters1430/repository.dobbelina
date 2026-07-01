"""Tests for familypornhd site module"""

from resources.lib.sites import familypornhd
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-item">
        <a href="/video/test-video-1/">
            <img src="https://cdn.familypornhd.com/thumb1.jpg" alt="Test Video 1" />
            <span class="duration">10:30</span>
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        familypornhd.List("https://familypornhd.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(familypornhd.site, "search_dir") as mock_search:
        familypornhd.Search("https://familypornhd.com/search/")

        assert mock_search.called


def test_categories_parses_items():
    """Test that Categories function works"""
    html = """
    <div class="categories">
        <a href="/category/anal/">Anal</a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        familypornhd.Categories("https://familypornhd.com/categories/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_playvid_handles_invalid_json():
    """Test that Playvid handles invalid JSON output from hosters gracefully without crashing"""
    html_page = '<div class="embed-container"><iframe src="https://bestwish.lol/e/test-hash"></iframe></div>'

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.kodilog") as mock_kodilog,
        patch("resources.lib.utils.VideoPlayer") as mock_videoplayer,
    ):
        # First call gets the video html, second gets ajax/stream (invalid JSON)
        mock_gethtml.side_effect = [html_page, "invalid-json"]

        # This should execute and not raise JSONDecodeError
        familypornhd.Playvid("https://familypornhd.com/video/test", "Test Video")

        assert mock_gethtml.call_count == 2
        assert mock_kodilog.called
        mock_vp_instance = mock_videoplayer.return_value
        assert not mock_vp_instance.play_from_direct_link.called
