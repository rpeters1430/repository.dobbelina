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


def test_models_parses_items_and_thumbs(monkeypatch):
    html = """
    <div class="vx-th item">
        <div class="vx-card-gallery">
            <div class="vx-top-card">
                <div class="vx-content">
                    <a href="https://viralxxxporn.com/models/sophie-rain/" title="Sophie Rain" class="vx-name">
                        <span class="vx-model-rank">#1</span>Sophie Rain
                    </a>
                </div>
                <a href="https://viralxxxporn.com/models/sophie-rain/" title="Sophie Rain" class="open-btn">Open</a>
            </div>
            <div class="vx-gallery">
                <div class="vx-box">
                    <div class="vx-media">
                        <img class="lazy-load" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" data-original="https://imgcdn.viralxxxporn.com/contents/videos_screenshots/553000/553026/800x450/1.jpg" alt="Sophie Rain">
                    </div>
                </div>
            </div>
        </div>
    </div>
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

    viralxxxporn.Models("https://viralxxxporn.com/models/")

    assert len(dirs) == 1
    assert dirs[0]["name"] == "Sophie Rain"
    assert dirs[0]["url"] == "https://viralxxxporn.com/models/sophie-rain/"
    assert dirs[0]["mode"] == "List"
    assert dirs[0]["icon"] == "https://imgcdn.viralxxxporn.com/contents/videos_screenshots/553000/553026/800x450/1.jpg"


def test_categories_and_models_extract_gallery_card_thumbs(monkeypatch):
    cat_html = """
    <div class="vx-card-gallery">
        <div class="vx-top-card">
            <div class="vx-content">
                <a class="vx-name" href="https://viralxxxporn.com/categories/18-year-old/" title="18 Year Old">18 Year Old</a>
            </div>
            <a class="open-btn" href="https://viralxxxporn.com/categories/18-year-old/" title="18 Year Old">Open</a>
        </div>
        <div class="vx-gallery">
            <div class="vx-box"><div class="vx-media">
                <img class="lazy-load" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                     data-original="https://imgcdn.viralxxxporn.com/contents/videos_screenshots/561000/561106/800x450/1.jpg" />
            </div></div>
        </div>
    </div>
    """
    model_html = """
    <div class="vx-card-gallery">
        <div class="vx-top-card">
            <div class="vx-content">
                <a class="vx-name" href="https://viralxxxporn.com/models/sophie-rain/" title="Sophie Rain"><span class="vx-model-rank">#1</span>Sophie Rain</a>
            </div>
        </div>
        <div class="vx-gallery">
            <div class="vx-box"><div class="vx-media">
                <img class="lazy-load" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                     data-original="https://imgcdn.viralxxxporn.com/contents/videos_screenshots/552000/552362/800x450/1.jpg" />
            </div></div>
        </div>
    </div>
    """
    dirs = []
    monkeypatch.setattr(
        viralxxxporn.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(viralxxxporn.utils, "eod", lambda: None)

    monkeypatch.setattr(viralxxxporn.utils, "getHtml", lambda *a, **k: cat_html)
    viralxxxporn.Categories("https://viralxxxporn.com/categories/")

    monkeypatch.setattr(viralxxxporn.utils, "getHtml", lambda *a, **k: model_html)
    viralxxxporn.Models("https://viralxxxporn.com/models/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "18 Year Old"
    assert dirs[0]["icon"] == "https://imgcdn.viralxxxporn.com/contents/videos_screenshots/561000/561106/800x450/1.jpg"
    assert dirs[1]["name"] == "Sophie Rain"
    assert dirs[1]["icon"] == "https://imgcdn.viralxxxporn.com/contents/videos_screenshots/552000/552362/800x450/1.jpg"


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
        html, "https://viralxxxporn.com/video/468174/test/", follow_redirects=True
    )
