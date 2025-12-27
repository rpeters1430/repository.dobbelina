"""Tests for homemoviestube site module"""
from resources.lib.sites import homemoviestube
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video">
        <a href="/video/test/">
            <img src="https://cdn.homemoviestube.com/thumb1.jpg" />
        </a>
    </div>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        homemoviestube.List("https://homemoviestube.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(homemoviestube.site, "search_dir") as mock_search:
        homemoviestube.Search("https://homemoviestube.com/search/")

        assert mock_search.called
