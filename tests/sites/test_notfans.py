from resources.lib.sites import notfans
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_site():
    with patch("resources.lib.sites.notfans.site") as mock:
        mock.url = "https://notfans.com/"
        yield mock


def test_list_videos(mock_site):
    with open("tests/fixtures/sites/notfans/listing.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        notfans.List("https://notfans.com/latest-updates/")

        assert mock_site.add_download_link.called
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Bbystar" in args[0]
        assert "https://notfans.com/videos/204523/bbystar61/" in args[1]
        assert "320x180" in args[3]


def test_list_video_count(mock_site):
    with open("tests/fixtures/sites/notfans/listing.html", "r", encoding="utf-8") as f:
        html = f.read()

    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        notfans.List("https://notfans.com/latest-updates/")
        assert mock_site.add_download_link.call_count >= 20


def test_playvid_kvs(mock_site):
    html = (
        "var flashvars = {"
        "license_code: '$477462815752333',"
        "video_url: 'https://notfans.com/get_file/6/abc123/204000/204523/204523.mp4/',"
        "};"
    )
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        notfans.Playvid("https://notfans.com/videos/204523/bbystar61/", "Bbystar")

        assert mock_vp.play_from_direct_link.called
        call_arg = mock_vp.play_from_direct_link.call_args[0][0]
        assert "204523.mp4" in call_arg


def test_playvid_fallback(mock_site):
    mock_vp = MagicMock()
    with (
        patch("resources.lib.utils.getHtml", return_value=""),
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
    ):
        notfans.Playvid("https://notfans.com/videos/204523/bbystar61/", "Bbystar")
        assert mock_vp.play_from_link_to_resolve.called


def test_list_filters_ads(mock_site):
    html = """
    <html>
    <div class="item">
        <a href="https://notfans.com/videos/123/real-video" title="Real Video">
            <strong class="title">Real Video</strong>
            <img src="thumb.jpg" />
        </a>
    </div>
    <div class="item avd">
        <a href="https://ads.com/ad-link" title="Ad">
            <strong class="title">Ad title</strong>
        </a>
    </div>
    </html>
    """
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        notfans.List("https://notfans.com/latest-updates/")
        assert mock_site.add_download_link.call_count == 1
        args, kwargs = mock_site.add_download_link.call_args_list[0]
        assert "Real Video" in args[0]

