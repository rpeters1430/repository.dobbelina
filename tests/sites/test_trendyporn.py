"""Tests for trendyporn site module"""

from resources.lib.sites import trendyporn
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-item">
        <a href="/video/test/">
            <img src="https://cdn.trendyporn.com/thumb1.jpg" />
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        trendyporn.List("https://trendyporn.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(trendyporn.site, "search_dir") as mock_search:
        trendyporn.Search("https://trendyporn.com/search/")

        assert mock_search.called
