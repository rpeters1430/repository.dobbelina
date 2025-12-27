"""Tests for beemtube site module"""

from resources.lib.sites import beemtube
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-block">
        <a href="/videos/test-video-1/" class="video-link">
            <img src="https://cdn.beemtube.com/thumb1.jpg" alt="Test Video 1" />
            <div class="duration">10:30</div>
        </a>
    </div>
    <div class="video-block">
        <a href="/videos/test-video-2/" class="video-link">
            <img data-original="https://cdn.beemtube.com/thumb2.jpg" alt="Test Video 2" />
            <div class="duration">08:45</div>
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        beemtube.List("https://beemtube.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(beemtube.site, "search_dir") as mock_search:
        beemtube.Search("https://beemtube.com/search/")

        assert mock_search.called


def test_search_with_keyword():
    """Test that Search with keyword calls List"""
    with patch("resources.lib.sites.beemtube.List") as mock_list:
        beemtube.Search("https://beemtube.com/search/", keyword="test query")

        assert mock_list.called


def test_categories_parses_items():
    """Test that Categories function works"""
    html = """
    <div class="categories">
        <a href="/category/anal/" class="category-item">
            <span>Anal</span>
        </a>
        <a href="/category/asian/" class="category-item">
            <span>Asian</span>
        </a>
    </div>
    """

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html

        beemtube.Categories("https://beemtube.com/categories/")

        assert mock_gethtml.called
        assert mock_eod.called
