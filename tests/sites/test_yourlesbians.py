from resources.lib.sites import yourlesbians
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.yourlesbians.site") as mock:
        mock.url = "https://yourlesbians.com/"
        yield mock


def test_main_menu(mock_site):
    with (
        patch("resources.lib.sites.yourlesbians.List") as mock_list,
        patch("resources.lib.utils.eod"),
    ):
        yourlesbians.Main()

    # Check some menu items
    mock_site.add_dir.assert_any_call(
        "[COLOR hotpink]Latest[/COLOR]", "https://yourlesbians.com/", "List", mock_site.img_cat
    )
    mock_site.add_dir.assert_any_call(
        "[COLOR hotpink]Categories[/COLOR]", "https://yourlesbians.com/categories/", "Categories", mock_site.img_cat
    )
    mock_list.assert_called_once_with("https://yourlesbians.com/")


def test_site_category():
    assert yourlesbians.site.category == "Video Tubes"


def test_list_videos(mock_site):
    html = """
    <html><body>
      <div class="thumbs">
        <div class="item">
          <a href="https://yourlesbians.com/video/lene-angelica-plays-with-buttplug/" title="Norwegian Baddie Lene Angelica Plays With Buttplug">
            <img data-original="https://img.example.com/thumb.jpg" />
          </a>
          <span class="time">3:37</span>
          <span class="qualtiy">HD</span>
        </div>
      </div>
      <div class="pagination">
        <a href="https://yourlesbians.com/2/">Next</a>
      </div>
    </body></html>
    """

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        yourlesbians.List("https://yourlesbians.com/")

        # Verify video added
        assert mock_site.add_download_link.called
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Norwegian Baddie" in args[0]
        assert "lene-angelica-plays-with-buttplug" in args[1]
        assert "3:37" in kwargs.get("duration", "")
        assert "HD" in kwargs.get("quality", "")

        # Verify pagination
        assert mock_site.add_dir.called
        # Find next page call
        next_page_call = [c for c in mock_site.add_dir.call_args_list if "Next Page" in c.args[0]]
        assert next_page_call
        assert "https://yourlesbians.com/2/" in next_page_call[0].args[1]


def test_playvid_highest_quality(mock_site):
    html = """
    <script>
    video_url: 'https://cdn.example.com/480p.mp4'
    video_alt_url: 'https://cdn.example.com/720p.mp4'
    video_alt_url2: 'https://cdn.example.com/1080p.mp4'
    </script>
    """

    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        yourlesbians.Playvid("https://yourlesbians.com/video/some-video/", "Test Video")

        mock_vp.play_from_direct_link.assert_called_once()
        playback_url = mock_vp.play_from_direct_link.call_args.args[0]
        # Should pick 1080p from fixture
        assert "1080p.mp4" in playback_url
        assert playback_url.endswith("|Referer=https://yourlesbians.com/video/some-video/")
