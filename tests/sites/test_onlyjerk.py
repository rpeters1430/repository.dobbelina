from unittest.mock import MagicMock, patch
import pytest

from resources.lib.sites import onlyjerk


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.onlyjerk.site") as mock:
        mock.url = "https://onlyjerk.net/"
        mock.img_cat = "cat.png"
        mock.img_search = "search.png"
        mock.img_next = "next.png"
        yield mock


def test_main(mock_site):
    with (
        patch("resources.lib.sites.onlyjerk.List") as mock_list,
        patch("resources.lib.utils.eod") as mock_eod,
    ):
        onlyjerk.Main()
        assert mock_site.add_dir.call_count >= 10
        assert mock_list.called
        assert mock_eod.called


def test_list_videos(mock_site):
    with open("tests/fixtures/sites/onlyjerk_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        onlyjerk.List("https://onlyjerk.net/latest-videos/")

        assert mock_site.add_download_link.called
        assert mock_site.add_download_link.call_count >= 10
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        # Title, URL, mode, thumb
        assert len(args[0]) > 0
        assert "https://onlyjerk.net/" in args[1]
        assert args[2] == "Playvid"
        assert args[3].startswith("http")

        # Next page check
        assert mock_site.add_dir.called
        next_args = mock_site.add_dir.call_args[0]
        assert "Next Page" in next_args[0]
        assert "https://onlyjerk.net/latest-videos/page/2/" in next_args[1]


def test_search(mock_site):
    with patch("resources.lib.sites.onlyjerk.List") as mock_list:
        onlyjerk.Search("https://onlyjerk.net/?s=", keyword="asian babes")
        mock_list.assert_called_once_with("https://onlyjerk.net/?s=asian+babes")

    onlyjerk.Search("https://onlyjerk.net/?s=", keyword=None)
    mock_site.search_dir.assert_called_once_with("https://onlyjerk.net/?s=", "Search")


def test_playvid_decoded_iframes(mock_site):
    with open("tests/fixtures/sites/onlyjerk_video.html", "r", encoding="utf-8") as f:
        html = f.read()

    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        onlyjerk.Playvid("https://onlyjerk.net/miss-teela/", "Miss Teela")

        assert mock_vp.play_from_link_list.called
        sources = mock_vp.play_from_link_list.call_args[0][0]
        assert any("vidara.to" in s for s in sources)
        assert any("luluvdo.com" in s for s in sources)
        assert any("voe.sx" in s for s in sources)


def test_playvid_fallback(mock_site):
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value="<html>empty</html>"),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        onlyjerk.Playvid("https://onlyjerk.net/test/", "Test")
        mock_vp.play_from_link_to_resolve.assert_called_once_with("https://onlyjerk.net/test/")
