from unittest.mock import MagicMock, patch
import pytest

from resources.lib.sites import porno24


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.porno24.site") as mock:
        mock.url = "https://porno24.to/"
        mock.img_cat = "cat.png"
        mock.img_search = "search.png"
        mock.img_next = "next.png"
        yield mock


def test_main(mock_site):
    with (
        patch("resources.lib.sites.porno24.List") as mock_list,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        porno24.Main()
        assert mock_site.add_dir.call_count >= 4
        assert mock_list.called
        assert mock_eod.called


def test_list_videos(mock_site):
    with open("tests/fixtures/sites/porno24_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        porno24.List("https://porno24.to/latest-updates/")

        assert mock_site.add_download_link.called
        assert mock_site.add_download_link.call_count >= 10
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        # Title, URL, mode, thumb
        assert "https://porno24.to/video/" in args[1]
        assert args[2] == "Playvid"
        assert args[3].startswith("http")

        # Next page check
        assert mock_site.add_dir.called
        next_args = mock_site.add_dir.call_args[0]
        assert "Next Page" in next_args[0]
        assert "https://porno24.to/latest-updates/2/" in next_args[1]


def test_categories(mock_site):
    with open("tests/fixtures/sites/porno24_categories.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        porno24.Categories("https://porno24.to/categories/")

        assert mock_site.add_dir.called
        assert mock_site.add_dir.call_count >= 20
        args, kwargs = mock_site.add_dir.call_args_list[0]
        assert "https://porno24.to/categories/" in args[1]
        assert args[2] == "List"
        assert args[3].startswith("http")


def test_search(mock_site):
    with patch("resources.lib.sites.porno24.List") as mock_list:
        porno24.Search("https://porno24.to/search/", keyword="german amateur")
        mock_list.assert_called_once_with("https://porno24.to/search/german+amateur/")

    porno24.Search("https://porno24.to/search/", keyword=None)
    mock_site.search_dir.assert_called_once_with("https://porno24.to/search/", "Search")


def test_playvid_kvs(mock_site):
    html = """
    var flashvars = {
        license_code: '$395624113052333',
        video_url: 'https://porno24.to/get_file/0/video_720p.mp4/?v-acctoken=123',
        video_url_text: '720p',
        video_alt_url: 'https://porno24.to/get_file/0/video_1080p.mp4/?v-acctoken=456',
        video_alt_url_text: '1080p'
    };
    """
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
        patch("resources.lib.utils.selector", return_value="https://porno24.to/get_file/0/video_1080p.mp4/?v-acctoken=456"),
    ):
        porno24.Playvid("https://porno24.to/video/16386/test/", "Test Video")

        assert mock_vp.play_from_direct_link.called
        call_arg = mock_vp.play_from_direct_link.call_args[0][0]
        assert "video_1080p.mp4" in call_arg
        assert "Referer=" in call_arg


def test_playvid_fallback(mock_site):
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value="<html>no videos here</html>"),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        porno24.Playvid("https://porno24.to/video/16386/test/", "Test Video")
        mock_vp.play_from_link_to_resolve.assert_called_once_with("https://porno24.to/video/16386/test/")
