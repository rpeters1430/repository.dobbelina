from unittest.mock import MagicMock, patch

from resources.lib.sites import camgirlfap


def _mock_site():
    mock_site = MagicMock()
    mock_site.url = "https://camgirlfap.com/"
    mock_site.img_next = "cum-next.png"
    mock_site.img_cat = "cum-cat.png"
    mock_site.img_search = "cum-search.png"
    return mock_site


def test_list_videos():
    with open("tests/fixtures/sites/camgirlfap/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camgirlfap.List("https://camgirlfap.com/latest-updates/?from=1")

    assert mock_site.add_download_link.called
    title, url, mode, thumb = mock_site.add_download_link.call_args_list[0][0][:4]
    assert "KawaiiSofey" in title
    assert url.startswith("https://camgirlfap.com/video/")
    assert mode == "Playvid"
    assert "710510" in thumb

    next_page_call = mock_site.add_dir.call_args_list[-1]
    assert "Next Page" in next_page_call[0][0]
    assert "from=2" in next_page_call[0][1]


def test_categories():
    with open("tests/fixtures/sites/camgirlfap/categories.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camgirlfap.Categories("https://camgirlfap.com/categories/?from=1")

    assert mock_site.add_dir.called
    label, url, mode, img = mock_site.add_dir.call_args_list[0][0][:4]
    assert "dreamcam" in label
    assert "/categories/dreamcam/" in url
    assert mode == "List"


def test_models():
    with open("tests/fixtures/sites/camgirlfap/models.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camgirlfap.Models("https://camgirlfap.com/models/?sort_by=total_videos&from=1")

    assert mock_site.add_dir.called
    label, url, mode, img = mock_site.add_dir.call_args_list[0][0][:4]
    assert "Jackplusjill" in label
    assert "/models/jackplusjill/" in url
    assert mode == "List"


def test_playvid_selects_highest_quality():
    with open("tests/fixtures/sites/camgirlfap/video.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    selected = {}

    def fake_selector(dialog_name, sources, **kwargs):
        selected["sources"] = sources
        key = max(sources, key=lambda x: int("".join(filter(str.isdigit, x)) or 0))
        return sources[key]

    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.selector", side_effect=fake_selector),
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
    ):
        mock_vp = mock_vp_cls.return_value
        camgirlfap.Playvid("https://camgirlfap.com/video/710510/kawaiisofey/", "KawaiiSofey")

    assert "1080p" in selected["sources"]
    mock_vp.play_from_direct_link.assert_called_once()
    played_url = mock_vp.play_from_direct_link.call_args[0][0]
    assert "710510_1080p.mp4" in played_url
    assert "Referer=" in played_url
