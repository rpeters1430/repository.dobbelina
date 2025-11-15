import pytest

from tests.conftest import read_fixture

from resources.lib.sites import (
    xvideos,
    xnxx,
    spankbang,
    eporner,
    hqporner,
    porntrex,
    xhamster,
    sxyprn,
    whoreshub,
    justporn,
    drtuber,
    tnaflix,
    porngo,
    watchporn,
    pornone,
    pornhat,
)


SITE_FIXTURES = [
    (
        "xvideos",
        xvideos,
        "List",
        ("https://www.xvideos.com/new/",),
        {},
        "sites/xvideos/listing.html",
        True,
    ),
    (
        "xnxx",
        xnxx,
        "List",
        ("https://www.xnxx.com/todays-selection",),
        {},
        "sites/xnxx/listing.html",
        True,
    ),
    (
        "spankbang",
        spankbang,
        "List",
        ("https://spankbang.party/new_videos/1/",),
        {},
        "sites/spankbang/listing.html",
        True,
    ),
    (
        "eporner",
        eporner,
        "List",
        ("https://www.eporner.com/recent/",),
        {},
        "sites/eporner/listing.html",
        True,
    ),
    (
        "hqporner",
        hqporner,
        "HQLIST",
        ("https://hqporner.com/hdporn/1",),
        {},
        "sites/hqporner/listing.html",
        True,
    ),
    (
        "porntrex",
        porntrex,
        "PTList",
        ("https://www.porntrex.com/latest-updates/",),
        {"page": 1},
        "sites/porntrex/listing.html",
        True,
    ),
    (
        "xhamster",
        xhamster,
        "List",
        ("https://xhamster.com/newest",),
        {},
        "sites/xhamster/listing.html",
        True,
    ),
    (
        "sxyprn",
        sxyprn,
        "List",
        ("https://sxyprn.com/blog/all/0.html?fl=all&sm=latest",),
        {},
        "sites/sxyprn/listing.html",
        True,
    ),
    (
        "whoreshub",
        whoreshub,
        "List",
        ("https://www.whoreshub.com/latest-updates/",),
        {},
        "sites/whoreshub/listing.html",
        True,
    ),
    (
        "justporn",
        justporn,
        "List",
        ("https://justporn.xxx/video-list?lang=en&page=1",),
        {},
        "sites/justporn/listing.html",
        True,
    ),
    (
        "drtuber",
        drtuber,
        "List",
        ("https://www.drtuber.com/",),
        {},
        "sites/drtuber/listing.html",
        True,
    ),
    (
        "tnaflix",
        tnaflix,
        "List",
        ("https://www.tnaflix.com/new/1",),
        {},
        "sites/tnaflix/listing.html",
        True,
    ),
    (
        "porngo",
        porngo,
        "List",
        ("https://www.porngo.com/latest-updates/",),
        {},
        "sites/porngo/listing.html",
        True,
    ),
    (
        "watchporn",
        watchporn,
        "List",
        ("https://watchporn.to/latest-updates/",),
        {},
        "sites/watchporn/listing.html",
        True,
    ),
    (
        "pornone",
        pornone,
        "List",
        ("https://pornone.com/newest/",),
        {},
        "sites/pornone/listing.html",
        True,
    ),
    (
        "pornhat",
        pornhat,
        "List",
        ("https://www.pornhat.com/",),
        {},
        "sites/pornhat/listing.html",
        True,
    ),
]


@pytest.mark.parametrize(
    "site_name, module, func_name, func_args, func_kwargs, fixture_path, expect_pagination",
    SITE_FIXTURES,
)
def test_migrated_site_listing_parses_videos(
    monkeypatch,
    site_name,
    module,
    func_name,
    func_args,
    func_kwargs,
    fixture_path,
    expect_pagination,
):
    html = read_fixture(fixture_path)
    captured_videos = []
    captured_dirs = []

    def fake_get_html(*args, **kwargs):
        return html

    def capture_video(name, url, mode, iconimage, desc="", *_, **extra):
        captured_videos.append({"title": name, "url": url, "thumb": iconimage, "extra": extra})

    def capture_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append({"label": name, "url": url, "mode": mode})

    monkeypatch.setattr(module.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(module.utils, "eod", lambda *a, **k: None)
    monkeypatch.setattr(module.site, "add_download_link", capture_video)
    monkeypatch.setattr(module.site, "add_dir", capture_dir)

    getattr(module, func_name)(*func_args, **func_kwargs)

    assert captured_videos, f"{site_name} fixture should yield at least one video"
    assert captured_videos[0]["title"], "Video entries need a populated title"
    assert captured_videos[0]["url"], "Video entries need a populated url"

    if expect_pagination:
        assert captured_dirs, f"{site_name} fixture should expose pagination"
        assert captured_dirs[0]["url"], "Pagination entries require URLs"
