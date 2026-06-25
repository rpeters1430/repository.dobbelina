"""Tests for myporntape site module."""

import pytest
from resources.lib.sites import myporntape
from resources.lib import utils
from unittest.mock import patch, MagicMock


def test_main():
    """Test that Main function displays directory links and calls List."""
    with (
        patch.object(myporntape.site, "add_dir") as mock_add_dir,
        patch("resources.lib.sites.myporntape.List") as mock_list,
    ):
        myporntape.Main()
        
        assert mock_add_dir.call_count >= 5  # Latest, Top Rated, Most Viewed, Categories, Search
        assert mock_list.called


def test_list_parses_video_items_and_pagination():
    """Test that List function parses video details and next page link from HTML."""
    html = """
    <html>
        <div class="item">
            <a href="/videos/123/example-sex-tape/" title="Example Sex Tape" class="link">
                <img class="thumb lazy-load" data-original="https://myporntape.com/thumb.jpg" data-webp="https://myporntape.com/thumb.webp" />
                <span class="type">hd</span>
                <span class="time">12:34</span>
            </a>
            <div class="stat">
                <span><i class="icon-eye"></i>5 000</span>
            </div>
            <span class="atten">95%</span>
        </div>
        <div class="pagination">
            <div class="item pager next">
                <a class="btn" href="https://myporntape.com/latest-updates/2/">Next</a>
            </div>
        </div>
    </html>
    """
    
    downloads = []
    dirs = []
    
    with (
        patch("resources.lib.utils.getHtml", return_value=html) as mock_gethtml,
        patch.object(myporntape.site, "add_download_link") as mock_add_dl,
        patch.object(myporntape.site, "add_dir") as mock_add_dir,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_add_dl.side_effect = lambda name, url, mode, iconimage, desc="": downloads.append((name, url, iconimage))
        mock_add_dir.side_effect = lambda name, url, mode, iconimage=None: dirs.append((name, url))
        
        myporntape.List("https://myporntape.com/latest-updates/")
        
        assert len(downloads) == 1
        assert "Example Sex Tape" in downloads[0][0]
        assert "12:34" in downloads[0][0]
        assert "HD" in downloads[0][0]
        assert "5 000 views" in downloads[0][0]
        assert "95% rating" in downloads[0][0]
        assert downloads[0][1] == "https://myporntape.com/videos/123/example-sex-tape/"
        assert downloads[0][2] == "https://myporntape.com/thumb.jpg"
        
        assert len(dirs) == 1
        assert "Next Page... (2)" in dirs[0][0]
        assert dirs[0][1] == "https://myporntape.com/latest-updates/2/"
        assert mock_eod.called


def test_categories_parses_category_items():
    """Test that Categories function parses category details from HTML."""
    html = """
    <html>
        <div class="block-post">
            <a href="/categories/milf/" title="MILF" class="item item-video">
                <img class="thumb" src="https://myporntape.com/milf.jpg" />
                <div class="info-view">
                    <span class="text">1250</span>
                </div>
            </a>
        </div>
    </html>
    """
    
    dirs = []
    
    with (
        patch("resources.lib.utils.getHtml", return_value=html) as mock_gethtml,
        patch.object(myporntape.site, "add_dir") as mock_add_dir,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_add_dir.side_effect = lambda name, url, mode, iconimage=None: dirs.append((name, url, iconimage))
        
        myporntape.Categories("https://myporntape.com/categories/")
        
        assert len(dirs) == 1
        assert "Milf" in dirs[0][0]
        assert "1250 videos" in dirs[0][0]
        assert dirs[0][1] == "https://myporntape.com/categories/milf/"
        assert dirs[0][2] == "https://myporntape.com/milf.jpg"
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword prompts user for input."""
    with patch.object(myporntape.site, "search_dir") as mock_search_dir:
        myporntape.Search("https://myporntape.com/search/")
        assert mock_search_dir.called


def test_search_with_keyword():
    """Test that Search with keyword calls List with constructed URL."""
    with patch("resources.lib.sites.myporntape.List") as mock_list:
        myporntape.Search("https://myporntape.com/search/", keyword="homemade sex")
        mock_list.assert_called_once_with("https://myporntape.com/search/homemade+sex/")


def test_playvid_kvs_encoded():
    """Test that Playvid decrypts encoded KVS player variables."""
    html = """
    license_code: '$1234567890'
    video_url: 'function/0/encoded_url_here'
    """
    
    with (
        patch("resources.lib.utils.VideoPlayer") as mock_player,
        patch("resources.lib.utils.getHtml", return_value=html) as mock_gethtml,
        patch("resources.lib.sites.myporntape.kvs_decode", return_value="https://myporntape.com/video.mp4") as mock_decode,
    ):
        mock_vp = MagicMock()
        mock_player.return_value = mock_vp
        
        myporntape.Playvid("https://myporntape.com/videos/123/example/", "Example Video")
        
        assert mock_gethtml.called
        assert mock_decode.called
        mock_vp.play_from_direct_link.assert_called_once_with(
            "https://myporntape.com/video.mp4|User-Agent={0}&Referer=https://myporntape.com/videos/123/example/".format(utils.USER_AGENT)
        )


def test_playvid_fallback():
    """Test that Playvid falls back to direct link player if KVS variables are missing."""
    html = "<html></html>"
    
    with (
        patch("resources.lib.utils.VideoPlayer") as mock_player,
        patch("resources.lib.utils.getHtml", return_value=html) as mock_gethtml,
    ):
        mock_vp = MagicMock()
        mock_player.return_value = mock_vp
        
        myporntape.Playvid("https://myporntape.com/videos/123/example/", "Example Video")
        
        assert mock_gethtml.called
        mock_vp.play_from_site_link.assert_called_once_with("https://myporntape.com/videos/123/example/")
