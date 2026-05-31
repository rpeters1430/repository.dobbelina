import importlib
from unittest.mock import MagicMock


porna91 = importlib.import_module("resources.lib.sites.91porna")


def test_site_is_marked_new_jav_asian():
    assert porna91.site.category == "JAV & Asian"
    assert porna91.site.is_new is True


def test_list_parses_video_items(monkeypatch):
    html = """
    <div class="video-item">
        <a href="/comic/index/detail?video_key=340987">
            <div class="poster">
                <img
                    alt="Video One"
                    data-src="https://pic.example/one.jpg"
                    src="/static/web/images/poster_loading.svg"
                />
                <div class="text-sm">39:16</div>
            </div>
        </a>
        <div>
            <a href="/comic/index/detail?video_key=340987">
                <div class="line-clamp-2">Video One</div>
            </a>
        </div>
    </div>
    """
    downloads = []

    monkeypatch.setattr(porna91.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(porna91.utils, "eod", lambda: None)
    monkeypatch.setattr(
        porna91.site,
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

    porna91.List("https://91porna.com/")

    assert downloads == [
        {
            "name": "Video One",
            "url": "https://91porna.com/comic/index/detail?video_key=340987",
            "mode": "Playvid",
            "icon": "https://pic.example/one.jpg",
            "duration": "39:16",
        }
    ]


def test_categories_parse_video_category_links(monkeypatch):
    html = """
    <a href="/index/video?category=play">91视频</a>
    <a href="/av/relvideo?model=1&type=theme&order=week">多P群交</a>
    <a href="/novels">色情小说</a>
    """
    dirs = []

    monkeypatch.setattr(porna91.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(porna91.utils, "eod", lambda: None)
    monkeypatch.setattr(
        porna91.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    porna91.Categories("https://91porna.com/")

    assert dirs == [
        {
            "name": "91视频",
            "url": "https://91porna.com/index/video?category=play",
            "mode": "List",
        },
        {
            "name": "多P群交",
            "url": "https://91porna.com/av/relvideo?model=1&type=theme&order=week",
            "mode": "List",
        },
    ]


def test_search_uses_keyword_query(monkeypatch):
    called_urls = []
    monkeypatch.setattr(porna91, "List", lambda url: called_urls.append(url))

    porna91.Search("https://91porna.com/index/search?keyword=", keyword="test video")

    assert called_urls == ["https://91porna.com/index/search?keyword=test+video"]


def test_playvid_extracts_hls_from_embed_script(monkeypatch):
    detail_html = '<meta property="og:video" content="https://91porna.com/comic/index/embed?id=340987" />'
    embed_html = (
        'eval(function(p,a,c,k,e,d){})'
    )
    script_html = "packed"
    first_unpack = (
        'document.write("<script src=\\"/index/embed_play.js?img=%2Flogo.png&u="'
        '+encodeURIComponent("abc123")+"&t="+parseInt((new Date()).getTime()/1000/1800)+"\\"></script>")'
    )
    second_unpack = '<source src="https://cdn.example/video.m3u8?auth=1" type="application/x-mpegURL"/>'
    calls = []

    def fake_get_html(url, *args, **kwargs):
        calls.append(url)
        if "detail" in url:
            return detail_html
        if "embed_play.js" in url:
            return script_html
        return embed_html

    monkeypatch.setattr(porna91.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(porna91, "_unpack_first", MagicMock(side_effect=[first_unpack, second_unpack]))
    mock_vp_class = MagicMock()
    monkeypatch.setattr("resources.lib.utils.VideoPlayer", mock_vp_class)

    porna91.Playvid("https://91porna.com/comic/index/detail?video_key=340987", "Video One")

    assert calls[0] == "https://91porna.com/comic/index/detail?video_key=340987"
    assert calls[1] == "https://91porna.com/comic/index/embed?id=340987"
    assert calls[2].startswith("https://91porna.com/index/embed_play.js?img=%2Flogo.png&u=abc123&t=")
    direct_url = mock_vp_class.return_value.play_from_direct_link.call_args.args[0]
    assert direct_url.startswith("https://cdn.example/video.m3u8?auth=1|User-Agent=")
    assert "&Referer=https://91porna.com/comic/index/embed?id=340987" in direct_url
