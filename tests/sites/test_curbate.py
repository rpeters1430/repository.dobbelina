from unittest.mock import MagicMock, patch

from resources.lib.sites import curbate


def _mock_site():
    mock_site = MagicMock()
    mock_site.url = "https://curbate.tv/"
    mock_site.img_next = "cum-next.png"
    mock_site.img_cat = "cum-cat.png"
    mock_site.img_search = "cum-search.png"
    return mock_site


def test_list_videos():
    with open("tests/fixtures/sites/curbate/listing.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.curbate.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        curbate.List("https://curbate.tv/videos")

    assert mock_site.add_download_link.called
    title, url, mode, thumb = mock_site.add_download_link.call_args_list[0][0][:4]
    assert "Rubisweet1" in title
    assert url.startswith("https://curbate.tv/videos/")
    assert mode == "Playvid"
    assert "8agfg3aazts7spmv.jpg" in thumb

    next_page_call = mock_site.add_dir.call_args_list[-1]
    assert "Next Page" in next_page_call[0][0]
    assert "page=2" in next_page_call[0][1]


def test_models():
    with open("tests/fixtures/sites/curbate/models.html", "r", encoding="utf-8") as f:
        html = f.read()
    mock_site = _mock_site()
    with (
        patch("resources.lib.sites.curbate.site", mock_site),
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.eod"),
    ):
        curbate.Models("https://curbate.tv/models?sort=popular")

    assert mock_site.add_dir.called
    labels = [call[0][0] for call in mock_site.add_dir.call_args_list]
    assert any("silksimren" in lbl.lower() for lbl in labels)
    assert any("angelina" in lbl.lower() for lbl in labels)


def test_playvid():
    with open("tests/fixtures/sites/curbate/video.html", "r", encoding="utf-8") as f:
        html = f.read()
    with (
        patch("resources.lib.utils.getHtml", return_value=html),
        patch("resources.lib.utils.logoevent", create=True),
        patch("resources.lib.utils.VideoPlayer") as mock_vp_cls,
    ):
        mock_vp = mock_vp_cls.return_value
        mock_vp._solve_doodstream.return_value = "https://stream.mock/master.m3u8"
        curbate.Playvid("https://curbate.tv/videos/claraboobies-masturbating-335306", "claraboobies")

    assert mock_vp.play_from_direct_link.called
    assert "https://stream.mock/master.m3u8" in mock_vp.play_from_direct_link.call_args[0][0]
