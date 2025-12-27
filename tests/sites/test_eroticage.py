"""Tests for eroticage site module"""
from resources.lib.sites import eroticage
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <article class="video">
        <a href="/vid/test-video-1/" class="video-link">
            <img src="https://cdn.eroticage.com/thumb1.jpg" alt="Test Video 1" />
            <time>10:30</time>
        </a>
    </article>
    <article class="video">
        <a href="/vid/test-video-2/" class="video-link">
            <img src="https://cdn.eroticage.com/thumb2.jpg" alt="Test Video 2" />
            <time>15:20</time>
        </a>
    </article>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        eroticage.List("https://eroticage.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(eroticage.site, "search_dir") as mock_search:
        eroticage.Search("https://eroticage.com/search/")

        assert mock_search.called
