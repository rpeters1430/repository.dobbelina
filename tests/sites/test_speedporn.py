"""Tests for speedporn (speedporn.net layout, Oct 2026)."""

from pathlib import Path

import pytest

from resources.lib.sites import speedporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "speedporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture
def captured(monkeypatch):
    data = {"downloads": [], "dirs": []}
    monkeypatch.setattr(speedporn.utils, "eod", lambda *a, **k: None)
    monkeypatch.setattr(
        speedporn.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: data["downloads"].append(
            {"name": name, "url": url, "img": iconimage, "duration": kwargs.get("duration"),
             "contextm": kwargs.get("contextm")}
        ),
    )
    monkeypatch.setattr(
        speedporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: data["dirs"].append(
            {"name": name, "url": url, "mode": mode, "img": iconimage}
        ),
    )
    return data


def test_list_parses_cards(monkeypatch, captured):
    html = load_fixture("listing.html")
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: html)

    speedporn.List("https://speedporn.net/all-movies/")

    downloads = captured["downloads"]
    # 35 cards on the page; 8 live inside a <template> and are skipped
    assert len(downloads) == 27
    assert all(d["name"] for d in downloads)
    first = downloads[0]
    assert first["name"] == "Black & Pink Lingerie On Bed"
    assert first["url"] == "https://speedporn.net/black-pink-lingerie-on-bed/"
    assert first["img"].startswith("https://i1.wp.com/pandanetwork.club/")
    assert first["duration"] == "16:00"
    assert "speedporn.Lookupinfo" in first["contextm"][0][1]
    assert all(d["url"].startswith("https://speedporn.net/") for d in downloads)

    nxt = [d for d in captured["dirs"] if d["name"].startswith("Next Page")]
    assert nxt == [{
        "name": "Next Page (2/3629)",
        "url": "https://speedporn.net/all-movies/page/2/",
        "mode": "List",
        "img": speedporn.site.img_next,
    }]


def test_categories_genres_chips_skip_footer(monkeypatch, captured):
    html = load_fixture("genres.html")
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: html)

    speedporn.Categories("https://speedporn.net/watch-free-moivies-by-genres/")

    dirs = [d for d in captured["dirs"] if not d["name"].startswith("Next Page")]
    assert len(dirs) == 300
    assert dirs[0]["name"] == "'70s [COLOR deeppink](482)[/COLOR]"
    assert dirs[0]["url"] == "https://speedporn.net/genres/70s/"
    assert not any("?s=" in d["url"] for d in dirs)
    assert any(d["url"].endswith("?pg=2") and d["mode"] == "Categories" for d in captured["dirs"])


def test_categories_pornstars_tcards(monkeypatch, captured):
    html = load_fixture("pornstars.html")
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: html)

    speedporn.Categories("https://speedporn.net/watch-free-moivies-by-pornstars/")

    dirs = [d for d in captured["dirs"] if not d["name"].startswith("Next Page")]
    assert len(dirs) == 90
    assert dirs[0]["name"] == "Mick Blue [COLOR deeppink](1,644)[/COLOR]"
    assert dirs[0]["url"] == "https://speedporn.net/pornstars/mick-blue/"
    assert dirs[0]["img"].startswith("https://")


def test_categories_years_without_images(monkeypatch, captured):
    html = load_fixture("years.html")
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: html)

    speedporn.Categories("https://speedporn.net/watch-free-moivies-by-release-years/")

    dirs = captured["dirs"]
    assert dirs[0]["name"] == "2026 [COLOR deeppink](10,235)[/COLOR]"
    assert dirs[0]["url"] == "https://speedporn.net/release-year/2026/"
    assert dirs[0]["img"] == speedporn.site.img_cat


def test_search_quotes_keyword(monkeypatch):
    calls = []
    monkeypatch.setattr(speedporn, "List", lambda url: calls.append(url))
    speedporn.Search("https://speedporn.net/?s=", keyword="bella luna")
    assert calls == ["https://speedporn.net/?s=bella+luna"]


class _FakeVP:
    instances = []
    dood_result = None

    def __init__(self, name, download=None):
        self.links = None
        self.direct = None
        self.solved = []
        self.progress = type("p", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None})()
        _FakeVP.instances.append(self)

    def _solve_doodstream(self, url):
        self.solved.append(url)
        return _FakeVP.dood_result

    def play_from_direct_link(self, url):
        self.direct = url

    def play_from_link_list(self, links):
        self.links = links


def test_playvid_prefers_doodstream_mirror(monkeypatch):
    html = load_fixture("video.html")
    _FakeVP.instances = []
    _FakeVP.dood_result = "https://cdn.example/v.mp4|Referer=x"
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(speedporn.utils, "VideoPlayer", _FakeVP)

    speedporn.Playvid("https://speedporn.net/black-pink-lingerie-on-bed/", "Black & Pink")

    vp = _FakeVP.instances[0]
    assert vp.solved == ["https://playmogo.com/e/ziga8hga9gvn"]
    assert vp.direct == "https://cdn.example/v.mp4|Referer=x"
    assert vp.links is None


def test_playvid_falls_back_to_ordered_link_list(monkeypatch):
    html = load_fixture("video.html")
    _FakeVP.instances = []
    _FakeVP.dood_result = None
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(speedporn.utils, "VideoPlayer", _FakeVP)

    speedporn.Playvid("https://speedporn.net/black-pink-lingerie-on-bed/", "Black & Pink")

    assert _FakeVP.instances[0].links == [
        "https://playmogo.com/e/ziga8hga9gvn",
        "https://luluvido.com/e/zmtlmmky935n",
        "https://vidara.so/e/CLXm6aCKVKtzW",
        "https://playmate.to/embed/kvMaHrjvOR2YD",
        "https://voe.sx/e/h9dmttkpbzm4",
        "https://mixdrop.ag/e/z11g0g11sox8q1",
        "https://vinovo.to/e/eeegog6ku3wowp5",
    ]


def test_playvid_without_servers_notifies(monkeypatch):
    notes = []
    _FakeVP.instances = []
    monkeypatch.setattr(speedporn.utils, "getHtml", lambda *a, **k: "<html></html>")
    monkeypatch.setattr(speedporn.utils, "VideoPlayer", _FakeVP)
    monkeypatch.setattr(speedporn.utils, "notify", lambda *a, **k: notes.append(a))

    speedporn.Playvid("https://speedporn.net/x/", "X")

    assert _FakeVP.instances[0].links is None
    assert notes
