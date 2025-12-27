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

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
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

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        familypornhd.Categories("https://familypornhd.com/categories/")

        assert mock_gethtml.called
        assert mock_eod.called
