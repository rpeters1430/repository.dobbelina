import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add plugin path to sys.path
plugin_path = os.path.join(os.getcwd(), "plugin.video.cumination")
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from resources.lib.sites import pornhd3x


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.pornhd3x.site") as mock:
        mock.url = "https://www9.pornhd3x.tv/"
        yield mock


def test_list_videos(mock_site):
    with open("tests/fixtures/sites/pornhd3x_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        pornhd3x.List("https://www9.pornhd3x.tv/")

        # Verify some videos were added
        assert mock_site.add_download_link.called
        # Check first video details from fixture
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "BangBros 18" in args[0]
        assert "/movies/bangbros-18" in args[1]
        assert "HD" in kwargs.get("quality", "")


def test_playvid(mock_site):
    with open("tests/fixtures/sites/pornhd3x_video.html", "r", encoding="utf-8") as f:
        html = f.read()

    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        pornhd3x.Playvid("https://www9.pornhd3x.tv/movies/some-video", "Test Video")

        # Verify attempt to play
        assert (
            mock_vp.play_from_direct_link.called
            or mock_vp.play_from_link_to_resolve.called
        )
