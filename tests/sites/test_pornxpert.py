from unittest.mock import MagicMock

from resources.lib.sites import pornxpert


def test_site_is_marked_new_video_tube():
    assert pornxpert.site.category == "Video Tubes"
    assert pornxpert.site.is_new is True


def test_list_parses_video_cards_and_pagination(monkeypatch):
    html = """
    <div class="list-videos">
        <div class="item">
            <a href="/video/14462/sample-video/" title="Sample Video">
                <div class="img">
                    <img data-original="https://www.pornxpert.com/thumbs/1.jpg" alt="Sample Video">
                    <span class="duration">10:05</span>
                </div>
            </a>
        </div>
    </div>
    <div class="load-more">
        <a href="/latest-updates/2/" data-parameters="sort_by:post_date;from:2">Load more...</a>
    </div>
    """
    downloads = []
    dirs = []

    monkeypatch.setattr(pornxpert.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        pornxpert.site,
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
        pornxpert.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornxpert.utils, "eod", lambda: None)

    pornxpert.List("https://www.pornxpert.com/latest-updates/")

    assert downloads == [
        {
            "name": "Sample Video",
            "url": "https://www.pornxpert.com/video/14462/sample-video/",
            "mode": "Playvid",
            "icon": "https://www.pornxpert.com/thumbs/1.jpg",
            "duration": "10:05",
        }
    ]
    assert dirs == [
        {
            "name": "Next Page",
            "url": "https://www.pornxpert.com/latest-updates/2/",
            "mode": "List",
        }
    ]


def test_categories_and_search(monkeypatch):
    cat_html = """
    <div class="list-categories">
        <a class="item" href="/categories/french/" title="French">
            <strong class="title">French</strong>
        </a>
    </div>
    """
    dirs = []
    called_urls = []

    monkeypatch.setattr(pornxpert.utils, "getHtml", lambda *a, **k: cat_html)
    monkeypatch.setattr(
        pornxpert.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornxpert.utils, "eod", lambda: None)

    pornxpert.Categories("https://www.pornxpert.com/categories/")
    assert dirs == [
        {
            "name": "French",
            "url": "https://www.pornxpert.com/categories/french/",
            "mode": "List",
        }
    ]

    monkeypatch.setattr(pornxpert, "List", lambda url: called_urls.append(url))
    pornxpert.Search("https://www.pornxpert.com/search/", "latina mom")
    assert called_urls == ["https://www.pornxpert.com/search/?q=latina+mom"]


def test_playvid_decodes_kvs_flashvars_and_falls_back_to_kt_player(monkeypatch):
    vp = MagicMock()
    monkeypatch.setattr(pornxpert.utils, "VideoPlayer", lambda *a, **k: vp)
    monkeypatch.setattr(
        pornxpert,
        "kvs_decode",
        lambda vu, lc: "https://www.pornxpert.com/get_file/1/abc/17711_720p.mp4/",
    )
    kvs_html = (
        "license_code: '$583047419235753'; "
        "video_alt_url: 'function/0/https://www.pornxpert.com/get_file/1/enc/17711_720p.mp4/';"
    )
    monkeypatch.setattr(pornxpert.utils, "getHtml", lambda *a, **k: kvs_html)

    pornxpert.Playvid("https://www.pornxpert.com/video/17711/test/", "Test Video")
    vp.play_from_direct_link.assert_called_once_with(
        "https://www.pornxpert.com/get_file/1/abc/17711_720p.mp4/|Referer=https://www.pornxpert.com/"
    )

    fallback_html = "<html>flashvars</html>"
    monkeypatch.setattr(pornxpert.utils, "getHtml", lambda *a, **k: fallback_html)
    pornxpert.Playvid("https://www.pornxpert.com/video/9949/test/", "Test Video")
    vp.play_from_kt_player.assert_called_once_with(
        fallback_html, "https://www.pornxpert.com/video/9949/test/"
    )
