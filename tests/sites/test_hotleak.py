
import pytest
from pathlib import Path
from unittest.mock import patch
from resources.lib.sites import hotleak

@pytest.fixture
def site_spec_fixture():
    with patch('resources.lib.adultsite.AdultSite.add_dir') as mock_add_dir, \
         patch('resources.lib.adultsite.AdultSite.add_download_link') as mock_add_download_link, \
         patch('resources.lib.utils.getHtml') as mock_get_html:

        yield hotleak, mock_add_dir, mock_add_download_link, mock_get_html

def test_main_menu(site_spec_fixture):
    """
    Tests if the Main function correctly adds the Videos and Search directories.
    """
    site_spec, mock_add_dir, _, _ = site_spec_fixture
    site_spec.Main("https://hotleak.vip/")
    
    # Check Videos link
    mock_add_dir.assert_any_call("[COLOR hotpink]Videos[/COLOR]", "https://hotleak.vip/videos", "List", "")
    # Check Search link
    mock_add_dir.assert_any_call("[COLOR hotpink]Search[/COLOR]", "https://hotleak.vip/search", "Search", site_spec.site.img_search)

def test_list_videos(site_spec_fixture):
    """
    Tests if the List function correctly parses a video listing page and pagination.
    """
    site_spec, mock_add_dir, mock_add_download_link, mock_get_html = site_spec_fixture
    
    # Load the test fixture
    fixture_path = Path(__file__).parent.parent / 'fixtures/sites/hotleak_videos_live.html'
    with open(fixture_path, 'r', encoding='utf-8') as f:
        mock_get_html.return_value = f.read()

    # Call the function to be tested
    site_spec.List("https://hotleak.vip/videos")

    # Assert that add_download_link was called (should be many videos)
    assert mock_add_download_link.called
    assert mock_add_download_link.call_count > 10

    # Check the first call to add_download_link
    first_call_args = mock_add_download_link.call_args_list[0][0]
    # URL should contain video path
    assert "/video/" in first_call_args[1]

    # Check for "Next Page"
    mock_add_dir.assert_any_call("Next Page (2)", "https://hotleak.vip/videos?page=2", "List", site_spec.site.img_next, page='2')


def test_list_handles_non_text_response(site_spec_fixture):
    site_spec, mock_add_dir, mock_add_download_link, mock_get_html = site_spec_fixture
    ended = []
    mock_get_html.return_value = []

    with patch("resources.lib.utils.eod", lambda: ended.append(True)), \
         patch("resources.lib.utils.kodilog"):
        site_spec.List("https://hotleak.vip/videos")

    mock_add_dir.assert_not_called()
    mock_add_download_link.assert_not_called()
    assert ended == [True]


def test_list_skips_photos_duplicates_and_uses_title_fallback(site_spec_fixture):
    site_spec, mock_add_dir, mock_add_download_link, mock_get_html = site_spec_fixture
    mock_get_html.return_value = """
    <html><body>
      <article class="movie-item">
        <a class="thumbnail-container" href="/creator/video/123456">
          <img class="post-thumbnail" src="/thumb.webp" alt="">
        </a>
      </article>
      <article class="movie-item">
        <a class="thumbnail-container" href="/creator/video/123456">
          <img class="post-thumbnail" src="/thumb-duplicate.webp" alt="Duplicate">
        </a>
      </article>
      <article class="movie-item">
        <a class="thumbnail-container" href="/creator/photo/999999">
          <img class="post-thumbnail" src="/photo.webp" alt="Photo">
        </a>
      </article>
      <article class="movie-item">
        <a class="thumbnail-container" href="https://tantaly.com/ad">
          <img class="post-thumbnail" src="/ad.webp" alt="Ad">
        </a>
      </article>
    </body></html>
    """

    site_spec.List("https://hotleak.vip/videos")

    assert mock_add_download_link.call_count == 1
    args, kwargs = mock_add_download_link.call_args
    assert args[0] == "Hotleak Video 123456"
    assert args[1] == "https://hotleak.vip/creator/video/123456"
    assert args[3].startswith("https://hotleak.vip/thumb.webp|")
    mock_add_dir.assert_not_called()


def test_playvid(site_spec_fixture):
    """
    Tests if the Playvid function correctly finds and decrypts the video URL.
    """
    site_spec, _, _, mock_get_html = site_spec_fixture
    
    # Load the test fixture
    fixture_path = Path(__file__).parent.parent / 'fixtures/sites/hotleak_video_page_live.html'
    with open(fixture_path, 'r', encoding='utf-8') as f:
        mock_get_html.return_value = f.read()

    with patch('resources.lib.utils.VideoPlayer') as mock_vp_class:
        mock_vp_instance = mock_vp_class.return_value
        site_spec.Playvid("https://hotleak.vip/eth0t.666/video/11939112", "Test Video")
        
        # Assert that play_from_direct_link was called with a decrypted M3U8 URL and headers
        assert mock_vp_instance.play_from_direct_link.called
        call_args = mock_vp_instance.play_from_direct_link.call_args[0][0]
        assert "m3u8" in call_args
        assert "|User-Agent=" in call_args
        assert "Referer=https%3A//hotleak.vip/" in call_args


def _encrypt_hotleak_url(url):
    encoded = hotleak.base64.b64encode(url.encode("utf-8")).decode("ascii")
    return "a" * 16 + encoded[::-1] + "z" * 16


def test_playvid_handles_non_text_response(site_spec_fixture):
    site_spec, _, _, mock_get_html = site_spec_fixture
    mock_get_html.return_value = []

    with patch('resources.lib.utils.VideoPlayer') as mock_vp_class, \
         patch("resources.lib.utils.kodilog"), \
         patch("resources.lib.utils.notify") as mock_notify:
        mock_vp_instance = mock_vp_class.return_value
        site_spec.Playvid("https://hotleak.vip/model/video/123", "Test Video")

    mock_vp_instance.play_from_direct_link.assert_not_called()
    mock_vp_instance.progress.close.assert_called()
    mock_notify.assert_called_with("Error", "Could not load video page")


def test_playvid_skips_bad_sources_and_uses_next_valid_source(site_spec_fixture):
    site_spec, _, _, mock_get_html = site_spec_fixture
    encrypted = _encrypt_hotleak_url("https://video-cdn.hotleak.vip/path/master.m3u8")
    data_video = hotleak.json.dumps(
        {
            "source": [
                {"src": "too-short"},
                {"src": encrypted},
            ]
        }
    ).replace('"', "&quot;")
    mock_get_html.return_value = """
    <html><body>
      <div class="light-gallery-item" data-video="{0}"></div>
    </body></html>
    """.format(data_video)

    with patch('resources.lib.utils.VideoPlayer') as mock_vp_class:
        mock_vp_instance = mock_vp_class.return_value
        site_spec.Playvid("https://hotleak.vip/model/video/123", "Test Video")

    mock_vp_instance.play_from_direct_link.assert_called_once()
    call_args = mock_vp_instance.play_from_direct_link.call_args[0][0]
    assert call_args.startswith("https://video-cdn.hotleak.vip/path/master.m3u8|")


def test_playvid_accepts_source_dict_shape(site_spec_fixture):
    site_spec, _, _, mock_get_html = site_spec_fixture
    encrypted = _encrypt_hotleak_url("https://video-cdn.hotleak.vip/path/master.m3u8")
    data_video = hotleak.json.dumps({"source": {"src": encrypted}}).replace('"', "&quot;")
    mock_get_html.return_value = """
    <html><body>
      <div class="light-gallery-item" data-video="{0}"></div>
    </body></html>
    """.format(data_video)

    with patch('resources.lib.utils.VideoPlayer') as mock_vp_class:
        mock_vp_instance = mock_vp_class.return_value
        site_spec.Playvid("https://hotleak.vip/model/video/123", "Test Video")

    mock_vp_instance.play_from_direct_link.assert_called_once()


def test_search_encodes_keyword_with_plus(site_spec_fixture):
    site_spec, _, _, _ = site_spec_fixture

    with patch.object(site_spec, "List") as mock_list:
        site_spec.Search("https://hotleak.vip/search", keyword="test & query")

    mock_list.assert_called_once_with("https://hotleak.vip/search?search=test+%26+query")

