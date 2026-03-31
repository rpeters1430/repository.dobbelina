from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import anysex


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "anysex"


def _load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_anysex_list_parses_videos_and_pagination(monkeypatch):
    html = _load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(anysex.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, False))
    monkeypatch.setattr(
        anysex.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(
        anysex.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(anysex.utils, "eod", lambda: None)

    anysex.List("https://anysex.com/latest-updates/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Test Video 1"
    assert "12345" in downloads[0]["url"]
    assert "preview.jpg" in downloads[0]["icon"]

    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "/latest-updates/2/" in dirs[0]["url"]


def test_anysex_list_parses_current_site_structure(monkeypatch):
    html = _load_fixture("list_current.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(
        anysex.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, False)
    )
    monkeypatch.setattr(
        anysex.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(
        anysex.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(anysex.utils, "eod", lambda: None)

    anysex.List("https://anysex.com/videos/new/")

    assert len(downloads) == 2
    assert downloads[0]["url"].startswith("https://anysex.com/video/501934/")
    assert downloads[0]["icon"].endswith("640x360/1.jpg")
    assert len(dirs) == 1
    assert dirs[0]["url"].endswith("/videos/new/2/")


def test_anysex_playvid_extracts_video_url(monkeypatch):
    html = _load_fixture("video.html")

    monkeypatch.setattr(anysex.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, False))
    mock_vp_class = MagicMock()
    monkeypatch.setattr("resources.lib.utils.VideoPlayer", mock_vp_class)

    anysex.Playvid(
        "https://anysex.com/videos/12345/test-video-1/",
        "Test Video",
    )

    args, _ = mock_vp_class.return_value.play_from_direct_link.call_args
    assert "12345.mp4" in args[0]
    assert "Referer=https://anysex.com/videos/12345/test-video-1/" in args[0]


def test_anysex_playvid_extracts_video_source_tags(monkeypatch):
    html = _load_fixture("video_current.html")

    monkeypatch.setattr(
        anysex.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, False)
    )
    mock_vp_class = MagicMock()
    monkeypatch.setattr("resources.lib.utils.VideoPlayer", mock_vp_class)

    anysex.Playvid(
        "https://anysex.com/video/501934/ex-girlfriend-returns-after-months-for-wild-makeup-sex-session/",
        "Test Video",
    )

    args, _ = mock_vp_class.return_value.play_from_direct_link.call_args
    assert "501934_720.mp4" in args[0]
    assert "Referer=https://anysex.com/video/501934/ex-girlfriend-returns-after-months-for-wild-makeup-sex-session/" in args[0]


def test_anysex_main_navigation(monkeypatch):
    dirs = []
    monkeypatch.setattr(
        anysex.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(anysex, "List", lambda url: None)
    monkeypatch.setattr(anysex.utils, "eod", lambda: None)

    anysex.Main()

    assert len(dirs) == 3
    assert any("videos/new/" in d["url"] for d in dirs)
    assert any("videos/categories/" in d["url"] for d in dirs)
    assert any("search/?q=" in d["url"] for d in dirs)
