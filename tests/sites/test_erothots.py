from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import erothots


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "sites" / "erothots"


def test_site_metadata():
    assert erothots.site.category == "Amateur & Social"
    assert erothots.site.is_new is True
    assert erothots.site.url == "https://erothots.co/"


def test_main_menu(monkeypatch):
    dirs = []
    monkeypatch.setattr(
        erothots.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(erothots, "List", lambda url: None)

    erothots.Main()

    modes = [d["mode"] for d in dirs]
    assert "List" in modes
    assert "Search" in modes


def test_list_parses_fixture(monkeypatch):
    html = (FIXTURES_DIR / "erothots_list.html").read_text(encoding="utf-8")
    downloads = []
    dirs = []

    monkeypatch.setattr(erothots.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        erothots.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        ),
    )
    monkeypatch.setattr(
        erothots.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(erothots.utils, "eod", lambda: None)

    erothots.List("https://erothots.co/videos")

    assert len(downloads) == 34
    assert downloads[0]["name"] == "luiza marquesa"
    assert downloads[0]["url"] == "https://erothots.co/video/eaokabrlgreglq/luiza-marquesa/"
    assert downloads[0]["mode"] == "Playvid"
    assert downloads[0]["duration"] == "00:29"

    assert len(dirs) >= 1
    assert dirs[0]["name"] == "Next Page"
    assert "?p=" in dirs[0]["url"]


def test_search(monkeypatch):
    called_with = []
    monkeypatch.setattr(erothots, "List", lambda url: called_with.append(url))

    erothots.Search("https://erothots.co/search/", keyword="sophie rain")

    assert called_with == ["https://erothots.co/search/?q=sophie+rain&type=videos"]


def test_playvid_direct_video_source(monkeypatch):
    html = (FIXTURES_DIR / "erothots_video.html").read_text(encoding="utf-8")
    mock_vp = MagicMock()
    monkeypatch.setattr(erothots.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erothots.utils, "VideoPlayer", lambda name, download: mock_vp)

    erothots.Playvid("https://erothots.co/video/izifeqtxj/test/", "Test Video")

    mock_vp.play_from_direct_link.assert_called_once()
    args, _ = mock_vp.play_from_direct_link.call_args
    assert "cdn.erocdn.co" in args[0]
    assert args[0].endswith(".mp4")
