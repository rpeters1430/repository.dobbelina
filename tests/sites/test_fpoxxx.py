from resources.lib.sites import fpoxxx
from unittest.mock import MagicMock, patch


def test_list_videos():
    with open("tests/fixtures/sites/fpoxxx/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = MagicMock()
    mock_site.url = "https://www.fpo.xxx/"
    with (
        patch("resources.lib.sites.fpoxxx.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        fpoxxx.List("https://www.fpo.xxx/new-1/")
        assert mock_site.add_download_link.called
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Kiara Mia" in args[0]
        assert "/video/1192506/" in args[1]
        assert "320x180" in args[3]


def test_list_count():
    with open("tests/fixtures/sites/fpoxxx/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = MagicMock()
    mock_site.url = "https://www.fpo.xxx/"
    with (
        patch("resources.lib.sites.fpoxxx.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        fpoxxx.List("https://www.fpo.xxx/new-1/")
        assert mock_site.add_download_link.call_count >= 10


def test_playvid_direct():
    html = "var flashvars = {license_code: '$309969210226426', video_url: 'https://www.fpo.xxx/get_file/25/abc/1192000/1192506/1192506.mp4/',};"
    mock_vp = MagicMock()
    mock_site = MagicMock()
    with (
        patch("resources.lib.sites.fpoxxx.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        fpoxxx.Playvid("https://www.fpo.xxx/video/1192506/", "Test")
        assert mock_vp.play_from_direct_link.called
        assert "1192506.mp4" in mock_vp.play_from_direct_link.call_args[0][0]


def test_playvid_fallback():
    mock_vp = MagicMock()
    mock_site = MagicMock()
    with (
        patch("resources.lib.sites.fpoxxx.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=""),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        fpoxxx.Playvid("https://www.fpo.xxx/video/1192506/", "Test")
        assert mock_vp.play_from_link_to_resolve.called
