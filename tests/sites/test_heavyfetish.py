from resources.lib.sites import heavyfetish
from unittest.mock import MagicMock, patch


def test_list_videos():
    with open("tests/fixtures/sites/heavyfetish/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = MagicMock()
    mock_site.url = "https://heavyfetish.com/"
    with (
        patch("resources.lib.sites.heavyfetish.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        heavyfetish.List("https://heavyfetish.com/1/?&sort_by=post_date")
        assert mock_site.add_download_link.called
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Whipped Ass" in args[0]
        assert "/videos/124029/" in args[1]
        assert "800x450" in args[3]


def test_list_count():
    with open("tests/fixtures/sites/heavyfetish/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = MagicMock()
    mock_site.url = "https://heavyfetish.com/"
    with (
        patch("resources.lib.sites.heavyfetish.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        heavyfetish.List("https://heavyfetish.com/1/?&sort_by=post_date")
        assert mock_site.add_download_link.call_count >= 20


def test_playvid_direct():
    html = "var flashvars = {license_code: '$656829421669950', video_url: 'https://heavyfetish.com/get_file/27/abc/124000/124029/124029.mp4/',};"
    mock_vp = MagicMock()
    mock_site = MagicMock()
    with (
        patch("resources.lib.sites.heavyfetish.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        heavyfetish.Playvid("https://heavyfetish.com/videos/124029/", "Test")
        assert mock_vp.play_from_direct_link.called
        assert "124029.mp4" in mock_vp.play_from_direct_link.call_args[0][0]


def test_playvid_fallback():
    mock_vp = MagicMock()
    mock_site = MagicMock()
    with (
        patch("resources.lib.sites.heavyfetish.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=""),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        heavyfetish.Playvid("https://heavyfetish.com/videos/124029/", "Test")
        assert mock_vp.play_from_link_to_resolve.called
