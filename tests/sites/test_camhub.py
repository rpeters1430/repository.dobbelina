from unittest.mock import MagicMock, patch

from resources.lib.sites import camhub


def _mock_site():
    mock_site = MagicMock()
    mock_site.url = "https://www.camhub.cc/"
    mock_site.img_next = "cum-next.png"
    mock_site.img_cat = "cum-cat.png"
    mock_site.img_search = "cum-search.png"
    return mock_site


def test_list_videos():
    with open("tests/fixtures/sites/camhub/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camhub.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camhub.List("https://www.camhub.cc/latest-updates/")

    assert mock_site.add_download_link.called
    title, url, mode, thumb = mock_site.add_download_link.call_args_list[0][0][:4]
    assert "adrianahayes" in title.lower()
    assert url.startswith("https://www.camhub.cc/videos/")
    assert mode == "Playvid"
    assert "336x189/1.jpg" in thumb

    next_page_call = mock_site.add_dir.call_args_list[-1]
    assert "Next Page" in next_page_call[0][0]
    assert "2" in next_page_call[0][1]


def test_categories():
    with open("tests/fixtures/sites/camhub/categories.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camhub.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camhub.Categories("https://www.camhub.cc/categories/")

    assert mock_site.add_dir.called
    labels = [call[0][0] for call in mock_site.add_dir.call_args_list]
    assert any("onlyfans" in lbl.lower() for lbl in labels)
    assert any("bongacams" in lbl.lower() for lbl in labels)


def test_playvid():
    with open("tests/fixtures/sites/camhub/video.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_embed = """var flashvars = {
        video_url: 'https://www.camhub.cc/get_file/test.mp4'
    };
    kt_player('kt_player', '', '', '', flashvars);"""

    with (
        patch("resources.lib.utils.getHtml", side_effect=[mock_embed, html]),
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
    ):
        mock_vp = mock_vp_cls.return_value
        camhub.Playvid("https://www.camhub.cc/videos/1103103/oooops-chaturbate-pussy-video/", "oooops")

    assert mock_vp.play_from_kt_player.called
