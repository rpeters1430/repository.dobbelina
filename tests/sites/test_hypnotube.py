"""Tests for hypnotube site module."""

from resources.lib.sites import hypnotube
from unittest.mock import patch


def test_main():
    """Test that Main function displays initial directory links and lists videos."""
    dirs = []
    
    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch.object(hypnotube.site, "add_dir") as mock_add_dir,
        patch("resources.lib.sites.hypnotube.List") as mock_list,
    ):
        mock_gethtml.return_value = "<html></html>"
        
        hypnotube.Main()
        
        assert mock_add_dir.call_count >= 2
        assert mock_list.called


def test_list_parses_video_items():
    """Test that List function parses video items and pagination from HTML."""
    html = """
    <html>
        <div class="item-inner-col">
            <a href="https://hypnotube.com/video/123" title="Hypnotic Spiral">
                <img src="https://hypnotube.com/thumb.jpg" />
            </a>
            <span class="time">15:30</span>
        </div>
        <a title="Next" href="page2.html">Next</a>
    </html>
    """
    
    downloads = []
    dirs = []
    
    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch.object(hypnotube.site, "add_download_link") as mock_add_dl,
        patch.object(hypnotube.site, "add_dir") as mock_add_dir,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        mock_gethtml.return_value = html
        mock_add_dl.side_effect = lambda name, url, mode, iconimage, desc="": downloads.append((name, url, iconimage))
        mock_add_dir.side_effect = lambda name, url, mode, iconimage=None: dirs.append((name, url))
        
        hypnotube.List("https://hypnotube.com/videos/page1.html")
        
        assert len(downloads) == 1
        assert "Hypnotic Spiral" in downloads[0][0]
        assert "15:30" in downloads[0][0]
        assert downloads[0][1] == "https://hypnotube.com/video/123"
        assert downloads[0][2] == "https://hypnotube.com/thumb.jpg"
        
        assert len(dirs) == 1
        assert "Next Page... (2)" in dirs[0][0]
        assert "page2.html" in dirs[0][1]
        assert mock_eod.called


def test_search_without_keyword():
    """Test that Search without keyword prompts user for input."""
    with patch.object(hypnotube.site, "search_dir") as mock_search_dir:
        hypnotube.Search("https://hypnotube.com/search/")
        assert mock_search_dir.called


def test_search_with_keyword():
    """Test that Search with keyword calls List with constructed URL."""
    with patch("resources.lib.sites.hypnotube.List") as mock_list:
        hypnotube.Search("https://hypnotube.com/search/", keyword="mind control")
        mock_list.assert_called_once_with("https://hypnotube.com/search/mind+control/")


def test_playvid():
    """Test that Playvid attempts to play the video via direct link player."""
    with patch("resources.lib.utils.VideoPlayer") as mock_player:
        hypnotube.Playvid("https://hypnotube.com/video/123", "Hypnotic Spiral")
        mock_player.assert_called_once()
        mock_player.return_value.play_from_site_link.assert_called_once_with(
            "https://hypnotube.com/video/123", "https://hypnotube.com/video/123"
        )
