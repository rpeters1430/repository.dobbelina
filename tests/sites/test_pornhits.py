"""Tests for pornhits site module"""

from resources.lib.sites import pornhits
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="item">
        <a href="/video/test/">
            <img src="https://cdn.pornhits.com/thumb1.jpg" />
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        pornhits.List("https://pornhits.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(pornhits.site, "search_dir") as mock_search:
        pornhits.Search("https://pornhits.com/search/")

        assert mock_search.called
