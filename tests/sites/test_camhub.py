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
    titles = [c[0][0] for c in mock_site.add_download_link.call_args_list]
    # 5 of the 20 fixture items are login-only private videos and are hidden.
    assert len(titles) == 15
    assert not any("adrianahayes" in t.lower() for t in titles)
    title, url, mode, thumb = mock_site.add_download_link.call_args_list[0][0][:4]
    assert title == "Bbrontte onlyfans latest nudes"
    assert url.startswith("https://www.camhub.cc/videos/")
    assert mode == "Playvid"
    # Sized screenshots are WebP mislabelled as JPEG; Kodi needs preview.jpg.
    assert thumb.startswith("https://www.camhub.cc/contents/videos_screenshots/")
    assert thumb.endswith("/preview.jpg")

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
    url = "https://www.camhub.cc/videos/1103103/oooops-chaturbate-pussy-video/"

    with (
        patch("resources.lib.utils.getHtml", return_value=html) as mock_get,
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
        patch("resources.lib.utils.notify") as mock_notify,
    ):
        mock_vp = mock_vp_cls.return_value
        camhub.Playvid(url, "oooops")

    # The video page carries the player config: play it once and stop, with
    # no embed fetch, link-resolver fallbacks or error notification after.
    mock_vp.play_from_kt_player.assert_called_once_with(html, url)
    assert mock_get.call_count == 1
    assert not mock_vp.play_from_link_to_resolve.called
    assert not mock_vp.play_from_link_list.called
    assert not mock_notify.called


def test_playvid_private_video_reports_login_required():
    private_html = (
        "<div class='player'>This video is a private video uploaded by x. "
        "Only active members can watch private videos.</div>"
        "<a href='#'>more</a>"
    )

    with (
        patch("resources.lib.utils.getHtml", return_value=private_html),
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
        patch("resources.lib.utils.notify") as mock_notify,
    ):
        mock_vp = mock_vp_cls.return_value
        camhub.Playvid("https://www.camhub.cc/videos/1116055/private/", "private")

    assert not mock_vp.play_from_kt_player.called
    assert not mock_vp.play_from_link_to_resolve.called
    assert not mock_vp.play_from_link_list.called
    assert "Private video" in mock_notify.call_args[0][0]
