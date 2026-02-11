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

from resources.lib.sites import heavyr

@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.heavyr.site") as mock:
        mock.url = "https://www.heavy-r.com/"
        yield mock

def test_list_videos(mock_site):
    with open("tests/fixtures/sites/heavyr_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with patch("resources.lib.utils.getHtml", return_value=html), \
         patch("resources.lib.utils.eod"):
        
        heavyr.List("https://www.heavy-r.com/")
        
        # Verify some videos were added
        assert mock_site.add_download_link.called
        # Check details from fixture
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Big Nipples" in args[0]
        assert "/video/446930/" in args[1]

def test_playvid(mock_site):
    with open("tests/fixtures/sites/heavyr_video.html", "r", encoding="utf-8") as f:
        html = f.read()

    mock_vp = MagicMock()
    with patch("resources.lib.utils.getHtml", return_value=html), \
         patch("resources.lib.utils.VideoPlayer", return_value=mock_vp):
        
        heavyr.Playvid("https://www.heavy-r.com/video/some-video", "Test Video")
        
        # Verify attempt to play
        assert mock_vp.play_from_direct_link.called or mock_vp.play_from_link_to_resolve.called