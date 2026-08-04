"""Tests for camwhores.tv site implementation.

Note: camwhorestv.py ports upstream's regex-based scraper verbatim (no live
HTML fixture was available to validate BeautifulSoup selectors against), so
these tests use synthetic HTML crafted to match the exact regex groups it
relies on.
"""

from resources.lib.sites import camwhorestv


def test_list_parses_video_items_and_flags_private(monkeypatch):
    html = """
    <div class="item">
    <a href="https://www.camwhores.tv/video/111222/hot-video-1/" title="Hot Video 1">
    <img data-original="https://tn.camwhores.tv/contents/videos_screenshots/111/111222/240x135/1.jpg">
    <span class="duration">12:34</span></a>
    <span class="views">1,234 views</span>
    </div>
    <div class="item">
    <a href="https://www.camwhores.tv/video/333444/private-video/" title="Private Video">
    <img data-original="https://tn.camwhores.tv/contents/videos_screenshots/333/333444/240x135/1.jpg">
    <span class="ico-private"></span>
    <span class="duration">05:00</span></a>
    <span class="views">42 views</span>
    </div>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url, "img": iconimage, "duration": kwargs.get("duration")})

    monkeypatch.setattr(camwhorestv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(camwhorestv.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(camwhorestv.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(camwhorestv.utils, "eod", lambda: None)
    monkeypatch.setattr(camwhorestv.utils, "next_page", lambda *a, **k: None)

    camwhorestv.List("https://www.camwhores.tv/latest-updates/1/")

    assert len(downloads) == 2
    assert "Hot Video 1" in downloads[0]["name"]
    assert "[PV]" not in downloads[0]["name"]
    assert downloads[0]["duration"] == "12:34"
    assert downloads[0]["img"] == "https://tn.camwhores.tv/contents/videos_screenshots/111/111222/preview.jpg"

    assert "[PV]" in downloads[1]["name"]
    assert "Private Video" in downloads[1]["name"]


def test_list_follows_classic_next_page(monkeypatch):
    html = """
    <div class="item">
    <a href="https://www.camwhores.tv/video/1/a/" title="A">
    <img data-original="https://tn.camwhores.tv/contents/videos_screenshots/1/1/240x135/1.jpg">
    <span class="duration">01:00</span></a>
    <span class="views">1 views</span>
    </div>
    <li class="next"><a href="https://www.camwhores.tv/latest-updates/2/">Next</a></li>
    <li class="last"><a href="https://www.camwhores.tv/latest-updates/9/">Last</a></li>
    """

    next_page_calls = []

    def fake_get_html(url, *args, **kwargs):
        return html

    monkeypatch.setattr(camwhorestv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(camwhorestv.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(camwhorestv.utils, "eod", lambda: None)
    monkeypatch.setattr(
        camwhorestv.utils,
        "next_page",
        lambda *a, **k: next_page_calls.append((a, k)),
    )

    camwhorestv.List("https://www.camwhores.tv/latest-updates/1/")

    assert len(next_page_calls) == 1


def test_categories_parses_items(monkeypatch):
    html = """
    <a class="item" href="https://www.camwhores.tv/categories/amateur/" title="Amateur">
    <img src="https://tn.camwhores.tv/cat/amateur.jpg">
    <div class="videos">1,024</div>
    """

    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    monkeypatch.setattr(camwhorestv.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(camwhorestv.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(camwhorestv.utils, "eod", lambda: None)

    camwhorestv.Categories("https://www.camwhores.tv/categories/")

    assert len(dirs) == 1
    assert "Amateur" in dirs[0][0]
    assert dirs[0][1] == "https://www.camwhores.tv/categories/amateur/"


def test_login_requires_credentials_when_no_session(monkeypatch):
    monkeypatch.setattr(camwhorestv.utils.addon, "getSetting", lambda key: "")
    monkeypatch.setattr(camwhorestv, "get_camwhores_session", lambda: "")
    monkeypatch.setattr(camwhorestv.utils, "_get_keyboard", lambda **k: "")

    result = camwhorestv.login_camwhores()

    assert result is False
