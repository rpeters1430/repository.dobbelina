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


def test_search_builds_url_with_post_date():
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.sites.camgirlfap.List") as mock_list,
    ):
        camgirlfap.Search("https://camgirlfap.com/search/", "sweet ary")

    mock_list.assert_called_once()
    search_url = mock_list.call_args[0][0]
    assert "https://camgirlfap.com/search/sweet-ary/" in search_url
    assert "sort_by=post_date" in search_url
    assert "from_videos=1" in search_url
    assert "from_albums=1" in search_url


def test_search_results_next_page():
    with open("tests/fixtures/sites/camgirlfap/search.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    search_url = "https://camgirlfap.com/search/girl/?q=girl&sort_by=post_date&from_videos=1&from_albums=1"
    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        camgirlfap.List(search_url)

    assert mock_site.add_download_link.called
    next_page_call = mock_site.add_dir.call_args_list[-1]
    assert "Next Page (2)" in next_page_call[0][0]
    next_url = next_page_call[0][1]
    assert "from_videos=2" in next_url
    assert "from_albums=2" in next_url
    assert "sort_by=post_date" in next_url


def test_playvid_resolves_doodstream_iframe():
    html = """
    <div class="player video">
      <div class="player-holder">
        <iframe src="https://vidply.com/e/abc123xyz" frameborder="0"></iframe>
      </div>
    </div>
    """
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.camgirlfap.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
    ):
        mock_vp = mock_vp_cls.return_value
        mock_vp._solve_doodstream.return_value = "https://dood.direct/stream.mp4"
        camgirlfap.Playvid("https://camgirlfap.com/video/12345/test-model/", "Test Video")

    mock_vp._solve_doodstream.assert_called_once_with("https://vidply.com/e/abc123xyz")
    mock_vp.play_from_direct_link.assert_called_once_with("https://dood.direct/stream.mp4")
