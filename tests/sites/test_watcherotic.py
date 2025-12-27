"""Tests for watcherotic site module"""
from resources.lib.sites import watcherotic
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-item">
        <a href="/video/test/">
            <img src="https://cdn.watcherotic.com/thumb1.jpg" />
        </a>
    </div>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        watcherotic.List("https://watcherotic.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(watcherotic.site, "search_dir") as mock_search:
        watcherotic.Search("https://watcherotic.com/search/")

        assert mock_search.called
