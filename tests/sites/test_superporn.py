import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add plugin path to sys.path
plugin_path = os.path.join(os.getcwd(), "plugin.video.cumination")
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from resources.lib.sites import superporn


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.superporn.site") as mock:
        mock.url = "https://www.superporn.com/"
        yield mock


def test_list_videos(mock_site):
    with open("tests/fixtures/sites/superporn_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        superporn.List("https://www.superporn.com/")

        # Verify some videos were added
        assert mock_site.add_download_link.called
        # Check details from fixture
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Sensual threesome" in args[0]
        assert "/video/sensual-threesome" in args[1]
        assert "35:00" in kwargs.get("duration", "")


def test_playvid(mock_site):
    html = 'video_url: "https://cdn.superporn.com/video.mp4",'
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        superporn.Playvid("https://www.superporn.com/video/some-video", "Test Video")

        # Verify video URL extraction
        assert mock_vp.play_from_direct_link.called
        call_args = mock_vp.play_from_direct_link.call_args[0][0]
        assert "video.mp4" in call_args


def test_main_uses_distinct_video_routes(mock_site):
    with (
        patch("resources.lib.sites.superporn.List"),
        patch("resources.lib.utils.eod"),
    ):
        superporn.Main()

    menu_urls = [call.args[1] for call in mock_site.add_dir.call_args_list[:3]]
    assert menu_urls == [
        "https://www.superporn.com/videos/latest",
        "https://www.superporn.com/videos/popular",
        "https://www.superporn.com/videos",
    ]
