import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock kodi-specific imports and others causing issues
sys.modules["xbmc"] = MagicMock()
sys.modules["xbmcgui"] = MagicMock()
sys.modules["xbmcplugin"] = MagicMock()
sys.modules["xbmcvfs"] = MagicMock()
sys.modules["xbmcaddon"] = MagicMock()
sys.modules["StorageServer"] = MagicMock()
sys.modules["kodi_six"] = MagicMock()
sys.modules["resources.lib.brotlidecpy"] = MagicMock()

# Add plugin path to sys.path
plugin_path = os.path.join(os.getcwd(), "plugin.video.cumination")
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from resources.lib.sites import neporn


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.neporn.site") as mock:
        mock.url = "https://neporn.com/"
        yield mock


def test_list_videos(mock_site):
    with open("tests/fixtures/sites/neporn_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        neporn.List("https://neporn.com/")

        # Verify some videos were added
        assert mock_site.add_download_link.called
        # Check details from fixture
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "SWALLOWED" in args[0]
        assert "/video/33353/" in args[1]
        assert "49:24" in kwargs.get("duration", "")


def test_playvid(mock_site):
    html = 'video_url: "https://cdn.neporn.com/video.mp4",'
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        neporn.Playvid("https://neporn.com/video/some-video", "Test Video")

        # Verify video URL extraction
        assert mock_vp.play_from_direct_link.called
        call_args = mock_vp.play_from_direct_link.call_args[0][0]
        assert "video.mp4" in call_args
