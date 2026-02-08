import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock kodi-specific imports and others causing issues
sys.modules['xbmc'] = MagicMock()
sys.modules['xbmcgui'] = MagicMock()
sys.modules['xbmcplugin'] = MagicMock()
sys.modules['xbmcvfs'] = MagicMock()
sys.modules['xbmcaddon'] = MagicMock()
sys.modules['StorageServer'] = MagicMock()
sys.modules['kodi_six'] = MagicMock()
sys.modules['resources.lib.brotlidecpy'] = MagicMock()

# Add plugin path to sys.path
plugin_path = os.path.join(os.getcwd(), "plugin.video.cumination")
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from resources.lib.sites import playhdporn

@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.playhdporn.site") as mock:
        mock.url = "https://playhdporn.com/"
        yield mock

def test_list_videos(mock_site):
    with open("tests/fixtures/sites/playhdporn_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with patch("resources.lib.utils.getHtml", return_value=html), \
         patch("resources.lib.utils.eod"):
        
        playhdporn.List("https://playhdporn.com/")
        
        # Verify some videos were added
        assert mock_site.add_download_link.called
        # Check first video details from fixture
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "DEBT4k" in args[0]
        assert "https://playhdporn.com/video/7252/" in args[1]
        assert "10:11" in kwargs.get("duration", "")

def test_categories(mock_site):
    html = """
    <div class="list-categories">
        <div class="item">
            <a href="/categories/anal/" title="Anal">
                <img src="/thumb.jpg" />
                <strong class="title">Anal</strong>
            </a>
        </div>
    </div>
    """
    with patch("resources.lib.utils.getHtml", return_value=html), \
         patch("resources.lib.utils.eod"):
        
        playhdporn.Categories("https://playhdporn.com/categories/")
        
        # Verify categories were added
        assert mock_site.add_dir.called
        args = mock_site.add_dir.call_args[0]
        assert "Anal" in args[0]
        assert "categories/anal/" in args[1]

def test_playvid(mock_site):
    with open("tests/fixtures/sites/playhdporn_video.html", "r", encoding="utf-8") as f:
        html = f.read()

    mock_vp = MagicMock()
    with patch("resources.lib.utils.getHtml", return_value=html), \
         patch("resources.lib.utils.VideoPlayer", return_value=mock_vp):
        
        playhdporn.Playvid("https://playhdporn.com/video/7252/", "Test Video")
        
        # Verify video URL extraction
        assert mock_vp.play_from_direct_link.called
        call_args = mock_vp.play_from_direct_link.call_args[0][0]
        assert "7252_720p.mp4" in call_args
        assert "Referer=" in call_args