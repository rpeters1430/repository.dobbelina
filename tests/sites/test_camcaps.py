from unittest.mock import MagicMock, patch

from resources.lib.sites import camcaps


def _mock_site():
    mock_site = MagicMock()
    mock_site.url = "https://camcaps.tv/"
    mock_site.img_next = "cum-next.png"
    mock_site.img_cat = "cum-cat.png"
    mock_site.img_search = "cum-search.png"
    return mock_site


def test_list_videos():
    with open("tests/fixtures/sites/camcaps/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camcaps.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camcaps.List("https://camcaps.tv/videos")

    assert mock_site.add_download_link.called
    title, url, mode, thumb = mock_site.add_download_link.call_args_list[0][0][:4]
    assert "Ava Amira" in title
    assert url.startswith("https://camcaps.tv/video/")
    assert mode == "Playvid"
    assert "362981" in thumb

    next_page_call = mock_site.add_dir.call_args_list[-1]
    assert "Next Page" in next_page_call[0][0]
    assert "page=2" in next_page_call[0][1]


def test_categories():
    with open("tests/fixtures/sites/camcaps/categories.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camcaps.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camcaps.Categories("https://camcaps.tv/categories")

    assert mock_site.add_dir.called
    labels = [call[0][0] for call in mock_site.add_dir.call_args_list]
    assert any("Onlyfans" in label for label in labels)
    assert any("Manyvids" in label for label in labels)


def test_tags():
    with open("tests/fixtures/sites/camcaps/tags.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camcaps.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camcaps.Tags("https://camcaps.tv/tags")

    assert mock_site.add_dir.called
    labels = [call[0][0] for call in mock_site.add_dir.call_args_list]
    assert any("Onlyfans" in label for label in labels)


def test_playvid():
    with open("tests/fixtures/sites/camcaps/video.html", "r", encoding="utf-8") as f:
        html = f.read()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
    ):
        mock_vp = mock_vp_cls.return_value
        mock_vp._solve_doodstream.return_value = "https://stream.mock/master.m3u8"
        camcaps.Playvid("https://camcaps.tv/video/362648/test", "Test Video")

    assert mock_vp.play_from_direct_link.called
    assert "https://stream.mock/master.m3u8" in mock_vp.play_from_direct_link.call_args[0][0]
