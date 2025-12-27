"""Tests for eroticmv site module"""
from resources.lib.sites import eroticmv
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-item">
        <a href="/video/12345/" title="Test Video 1">
            <img src="https://img.eroticmv.com/thumb1.jpg" />
            <span class="time">15:30</span>
        </a>
    </div>
    <div class="video-item">
        <a href="/video/67890/" title="Test Video 2">
            <img src="https://img.eroticmv.com/thumb2.jpg" />
            <span class="time">20:45</span>
        </a>
    </div>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        eroticmv.List("https://eroticmv.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(eroticmv.site, "search_dir") as mock_search:
        eroticmv.Search("https://eroticmv.com/search/")

        assert mock_search.called


def test_categories_parses_items():
    """Test that Categories function parses categories"""
    html = """
    <div class="category">
        <a href="/cat/anal/">Anal</a>
        <a href="/cat/asian/">Asian</a>
    </div>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        eroticmv.Categories("https://eroticmv.com/categories/")

        assert mock_gethtml.called
        assert mock_eod.called
