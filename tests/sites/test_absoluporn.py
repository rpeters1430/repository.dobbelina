"""Tests for absoluporn site module"""
from resources.lib.sites import absoluporn
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-item">
        <a href="/video/test-video-1/" title="Test Video 1">
            <img src="https://cdn.absoluporn.com/thumb1.jpg" />
            <span class="duration">08:30</span>
        </a>
    </div>
    <div class="video-item">
        <a href="/video/test-video-2/" title="Test Video 2">
            <img data-src="https://cdn.absoluporn.com/thumb2.jpg" />
            <span class="duration">12:15</span>
        </a>
    </div>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        absoluporn.List("https://absoluporn.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword_shows_dialog():
    """Test that Search without keyword shows search dialog"""
    with patch.object(absoluporn.site, "search_dir") as mock_search:
        absoluporn.Search("https://absoluporn.com/search/")

        assert mock_search.called


def test_search_with_keyword_calls_list():
    """Test that Search with keyword calls List function"""
    with patch("resources.lib.sites.absoluporn.List") as mock_list:
        absoluporn.Search("https://absoluporn.com/search/", keyword="test")

        assert mock_list.called


