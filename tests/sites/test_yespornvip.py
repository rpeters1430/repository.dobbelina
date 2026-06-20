"""Tests for yespornvip site module."""

import pytest
from resources.lib.sites import yespornvip
from unittest.mock import patch, MagicMock


def test_main():
    """Test that Main function calls fetch_homepage, cookie detection, and displays directories."""
    with (
        patch("resources.lib.sites.yespornvip.fetch_homepage") as mock_fetch,
        patch("resources.lib.sites.yespornvip.get_cookie_for_domain", return_value="6i3wgc") as mock_get_cookie,
        patch.object(yespornvip.site, "add_dir") as mock_add_dir,
        patch("resources.lib.sites.yespornvip.List") as mock_list,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        yespornvip.Main()
        
        assert mock_fetch.called
        assert mock_get_cookie.called
        assert mock_add_dir.call_count >= 5  # 4 channels + 1 search
        assert mock_list.called
        assert mock_eod.called


def test_list_parses_video_items():
    """Test that List function parses video items and pagination from HTML."""
    html = """
    <html>
        <div class="thumb_rel item">
            <a title="Skeet Video Example" href="/video-url/">
                <img data-webp="https://yesporn.vip/thumb.webp" />
            </a>
            <span class="qualtiy">HD</span>
            <span class="time">10:45</span>
            <span data-fav-video-id="45678"></span>
        </div>
        <a class="next" data-parameters="from:30;sort_by:latest">Next</a>
    </html>
    """
    
    downloads = []
    dirs = []
    
    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch.object(yespornvip.site, "add_download_link") as mock_add_dl,
        patch.object(yespornvip.site, "add_dir") as mock_add_dir,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html
        mock_add_dl.side_effect = lambda name, url, mode, iconimage, desc="": downloads.append((name, url, iconimage))
        mock_add_dir.side_effect = lambda name, url, mode, iconimage=None: dirs.append((name, url))
        
        yespornvip.List("https://yesporn.vip/")
        
        assert len(downloads) == 1
        assert "Skeet Video Example" in downloads[0][0]
        assert "10:45" in downloads[0][0]
        assert "HD" in downloads[0][0]
        assert downloads[0][1] == "https://yesporn.vip/embed/45678"
        assert downloads[0][2] == "https://yesporn.vip/thumb.webp"
        
        assert len(dirs) == 1
        assert "Next Page... (30)" in dirs[0][0]
        assert "?from=30" in dirs[0][1]
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword prompts user for input."""
    with patch.object(yespornvip.site, "search_dir") as mock_search_dir:
        yespornvip.Search("https://yesporn.vip/search/")
        assert mock_search_dir.called


def test_search_with_keyword():
    """Test that Search with keyword calls List with constructed URL."""
    with patch("resources.lib.sites.yespornvip.List") as mock_list:
        yespornvip.Search("https://yesporn.vip/search/", keyword="vixen")
        mock_list.assert_called_once_with("https://yesporn.vip/search/vixen/")


def test_playvid():
    """Test that Playvid parses licensing/video details and plays video."""
    html = """
    license_code: '$1234567890'
    video_url: 'function/0/encoded_url_here'
    video_url_text: '720p'
    """
    
    with (
        patch("resources.lib.utils.VideoPlayer") as mock_player,
        patch("resources.lib.utils.getHtml", return_value=html) as mock_gethtml,
        patch("resources.lib.decrypters.kvsplayer.kvs_decode", return_value="https://yesporn.vip/real_video.mp4") as mock_decode,
    ):
        mock_vp = MagicMock()
        mock_player.return_value = mock_vp
        
        yespornvip.Playvid("https://yesporn.vip/embed/45678", "Vixen Video")
        
        assert mock_gethtml.called
        assert mock_decode.called
        assert mock_vp.play_from_direct_link.called


def test_fetch_homepage():
    """Test fetch_homepage gracefully handles execution/errors."""
    with (
        patch("resources.lib.sites.yespornvip.Request") as mock_req,
        patch("resources.lib.sites.yespornvip.urlopen") as mock_urlopen,
        patch("resources.lib.utils.cj") as mock_cj,
        patch("resources.lib.utils.TRANSLATEPATH", return_value="/tmp/cookie") as mock_translate,
    ):
        yespornvip.fetch_homepage()
        assert mock_req.called
        assert mock_urlopen.called
        assert mock_cj.save.called
