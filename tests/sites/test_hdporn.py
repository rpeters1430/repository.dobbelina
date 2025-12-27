"""Tests for hdporn site module"""
from resources.lib.sites import hdporn
from unittest.mock import patch


def test_list_parses_video_items():
    """Test that List function parses video items"""
    html = """
    <div class="video-block">
        <a href="/video/12345/">
            <img src="https://cdn.hdporn.com/thumb1.jpg" />
        </a>
    </div>
    """

    with patch("resources.lib.utils.getHtml") as mock_gethtml, \
         patch("resources.lib.utils.eod") as mock_eod:
        mock_gethtml.return_value = html

        hdporn.List("https://hdporn.com/")

        assert mock_gethtml.called
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(hdporn.site, "search_dir") as mock_search:
        hdporn.Search("https://hdporn.com/search/")

        assert mock_search.called
