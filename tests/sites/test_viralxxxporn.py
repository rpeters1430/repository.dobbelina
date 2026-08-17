from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import viralxxxporn


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "sites" / "viralxxxporn"


def test_site_metadata():
    assert viralxxxporn.site.category == "Video Tubes"
    assert viralxxxporn.site.is_new is True
    assert viralxxxporn.site.url == "https://viralxxxporn.com/"


def test_main_menu(monkeypatch):
    dirs = []
    monkeypatch.setattr(
        viralxxxporn.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(viralxxxporn, "List", lambda url: None)

    viralxxxporn.Main()

    modes = [d["mode"] for d in dirs]
    assert "List" in modes
    assert "Categories" in modes
    assert "Models" in modes
    assert "Search" in modes


def test_list_parses_fixture(monkeypatch):
    html = (FIXTURES_DIR / "viralxxxporn_list.html").read_text(encoding="utf-8")
    downloads = []
    dirs = []

    monkeypatch.setattr(viralxxxporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        viralxxxporn.site,
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
        viralxxxporn.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(viralxxxporn.utils, "eod", lambda: None)

    viralxxxporn.List("https://viralxxxporn.com/")

    assert len(downloads) == 24
    assert downloads[0]["name"] == "Lena The Plug Full Video Uncut PPV Sex Tape With Gattouz0 Leaked"
    assert downloads[0]["url"].startswith("https://viralxxxporn.com/video/468174/")
    assert downloads[0]["mode"] == "Playvid"
    assert downloads[0]["duration"] == ""

    assert len(dirs) >= 1
    assert dirs[0]["name"] == "Next Page"
    assert "https://viralxxxporn.com/latest-updates/2/" in dirs[0]["url"]


def test_categories_parses_items(monkeypatch):
    html = """
    <ul class="categories-list">
        <li class="vx-item">
            <a class="vx-link" href="https://viralxxxporn.com/categories/gym/">
                <span>Gym</span>
                <span>519</span>
            </a>
        </li>
        <li class="vx-item">
            <a class="vx-link" href="https://viralxxxporn.com/categories/cosplay/">
                <span>Cosplay</span>
                <span>312</span>
            </a>
        </li>
        <li class="vx-item">
            <a class="vx-link" href="https://viralxxxporn.com/de/categories/">
                <span>Deutsch</span>
            </a>
        </li>
    </ul>
    """
    dirs = []
    monkeypatch.setattr(viralxxxporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        viralxxxporn.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(viralxxxporn.utils, "eod", lambda: None)

    viralxxxporn.Categories("https://viralxxxporn.com/categories/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Gym"
    assert dirs[0]["url"] == "https://viralxxxporn.com/categories/gym/"
    assert dirs[0]["mode"] == "List"
    assert dirs[1]["name"] == "Cosplay"


def test_search(monkeypatch):
    called_with = []
    monkeypatch.setattr(viralxxxporn, "List", lambda url: called_with.append(url))

    viralxxxporn.Search("https://viralxxxporn.com/search/", keyword="cosplay leak")

    assert called_with == ["https://viralxxxporn.com/search/cosplay+leak/"]


def test_playvid_calls_kt_player_for_flashvars(monkeypatch):
    html = (FIXTURES_DIR / "viralxxxporn_video.html").read_text(encoding="utf-8")
    mock_vp = MagicMock()
    monkeypatch.setattr(viralxxxporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(viralxxxporn.utils, "VideoPlayer", lambda name, download: mock_vp)

    viralxxxporn.Playvid("https://viralxxxporn.com/video/468174/test/", "Test Video")

    mock_vp.play_from_kt_player.assert_called_once_with(
        html, "https://viralxxxporn.com/video/468174/test/"
    )
