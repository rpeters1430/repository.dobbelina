from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import webpussi


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "sites" / "webpussi"


def test_site_metadata():
    assert webpussi.site.category == "Cams & Live"
    assert webpussi.site.is_new is True
    assert webpussi.site.url == "https://www.webpussi.com/"


def test_main_menu(monkeypatch):
    dirs = []
    monkeypatch.setattr(
        webpussi.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(webpussi, "List", lambda url: None)

    webpussi.Main()

    modes = [d["mode"] for d in dirs]
    assert "List" in modes
    assert "Categories" in modes
    assert "Models" in modes
    assert "Search" in modes


def test_list_parses_fixture(monkeypatch):
    html = (FIXTURES_DIR / "webpussi_list.html").read_text(encoding="utf-8")
    downloads = []
    dirs = []

    monkeypatch.setattr(webpussi.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        webpussi.site,
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
        webpussi.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(webpussi.utils, "eod", lambda: None)

    webpussi.List("https://www.webpussi.com/")

    assert len(downloads) == 48
    assert downloads[0]["name"] == "Chaturbate avamonroee  recording video show with sexy babe August-2026"
    assert downloads[0]["url"].startswith("https://www.webpussi.com/videos/123322/")
    assert downloads[0]["mode"] == "Playvid"
    assert downloads[0]["duration"] == "10:53"

    assert len(dirs) >= 1
    assert dirs[0]["name"] == "Next Page"
    assert "https://www.webpussi.com/latest-updates/2/" in dirs[0]["url"]


def test_categories_parses_items(monkeypatch):
    html = """
    <nav><a href="/categories/">Categories</a></nav>
    <div class="list-categories">
        <a class="item" href="/categories/brunette/" title="Brunette">
            <img src="/contents/categories/1.jpg" alt="Brunette">
            <strong class="title">Brunette</strong>
        </a>
        <a class="item" href="/categories/blonde/" title="Blonde">
            <img src="/contents/categories/2.jpg" alt="Blonde">
            <strong class="title">Blonde</strong>
        </a>
    </div>
    <div class="pagination"><li class="next"><a href="/categories/2/">Next</a></li></div>
    """
    dirs = []
    monkeypatch.setattr(webpussi.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        webpussi.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(webpussi.utils, "eod", lambda: None)

    webpussi.Categories("https://www.webpussi.com/categories/")

    assert len(dirs) == 3
    assert dirs[0]["name"] == "Brunette"
    assert dirs[0]["url"] == "https://www.webpussi.com/categories/brunette/"
    assert dirs[0]["mode"] == "List"
    assert dirs[1]["name"] == "Blonde"
    assert dirs[2]["name"] == "Next Page"


def test_models_skips_models_root_link(monkeypatch):
    html = """
    <nav><a href="/models/">Models</a></nav>
    <div class="list-models">
        <a class="item" href="/models/test-model/" title="Test Model">
            <img src="/contents/models/1.jpg" alt="Test Model">
        </a>
    </div>
    """
    dirs = []
    monkeypatch.setattr(webpussi.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        webpussi.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(webpussi.utils, "eod", lambda: None)

    webpussi.Models("https://www.webpussi.com/models/")

    assert dirs == [
        {
            "name": "Test Model",
            "url": "https://www.webpussi.com/models/test-model/",
            "mode": "List",
        }
    ]


def test_search(monkeypatch):
    called_with = []
    monkeypatch.setattr(webpussi, "List", lambda url: called_with.append(url))

    webpussi.Search("https://www.webpussi.com/search/", keyword="cam girl")

    assert called_with == ["https://www.webpussi.com/search/cam+girl/"]


def test_playvid_calls_kt_player_for_flashvars(monkeypatch):
    html = (FIXTURES_DIR / "webpussi_video.html").read_text(encoding="utf-8")
    mock_vp = MagicMock()
    monkeypatch.setattr(webpussi.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(webpussi.utils, "VideoPlayer", lambda name, download: mock_vp)

    webpussi.Playvid("https://www.webpussi.com/videos/123322/test/", "Test Video")

    mock_vp.play_from_kt_player.assert_called_once_with(
        html, "https://www.webpussi.com/videos/123322/test/"
    )
