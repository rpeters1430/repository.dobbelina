"""Tests for aagmaal.bz site implementation."""

from pathlib import Path

from resources.lib.sites import aagmaal


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "aagmaal"


def load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_main_includes_ott(monkeypatch):
    """Test that Main registers Categories, OTT, Search and calls List."""
    dirs = []
    list_calls = []

    monkeypatch.setattr(
        aagmaal.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(aagmaal, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.Main()

    modes = [d["mode"] for d in dirs]
    assert "Categories" in modes
    assert "OTT" in modes
    assert "Search" in modes
    assert any("ott/" in d["url"] for d in dirs if d["mode"] == "OTT")
    assert len(list_calls) == 1


def test_list_parses_vp_card_articles(monkeypatch):
    """Test that List correctly parses article.vp-card items."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(aagmaal.site, "add_download_link",
                        lambda name, url, mode, icon, desc="", **k: downloads.append({"name": name, "url": url, "icon": icon}))
    monkeypatch.setattr(aagmaal.site, "add_dir",
                        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url}))
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.List("https://aagmaal.bz/")

    assert len(downloads) == 3
    assert downloads[0]["name"] == "Desi Bhabhi Hot Romance"
    assert downloads[0]["url"] == "https://aagmaal.bz/desi-bhabhi-hot-romance/"
    assert downloads[0]["icon"] == "https://i.ibb.co/thumb1.jpg"
    assert downloads[1]["name"] == "Indian Couple Leaked MMS"
    assert downloads[2]["name"] == "Punjabi Girl Bathroom Video"

    # Pagination: next page with current=1, last=15
    assert len(dirs) == 1
    assert "Next Page" in dirs[0]["name"]
    assert "Page 1 of 15" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://aagmaal.bz/page/2/"


def test_list_handles_no_pagination(monkeypatch):
    """Test that List handles pages without pagination gracefully."""
    html = """<html><body>
    <article class="vp-card">
        <a class="vp-card__thumb" href="https://aagmaal.bz/test-video/">
            <img alt="Test Video" src="thumb.jpg"/>
        </a>
    </article>
    </body></html>"""

    downloads = []
    dirs = []

    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(aagmaal.site, "add_download_link",
                        lambda *a, **k: downloads.append(a[0]))
    monkeypatch.setattr(aagmaal.site, "add_dir",
                        lambda *a, **k: dirs.append(a[0]))
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.List("https://aagmaal.bz/")

    assert len(downloads) == 1
    assert len(dirs) == 0


def test_list_handles_new_pagination_wrapper(monkeypatch):
    """Test that List supports the current vp-pagi-wrap pagination markup."""
    html = """<html><body>
    <article class="vp-card">
        <a class="vp-card__thumb" href="https://aagmaal.bz/test-video/">
            <img alt="Test Video" src="thumb.jpg"/>
        </a>
    </article>
    <nav class="vp-pagi-wrap">
        <span class="page-numbers current">4</span>
        <span class="page-numbers dots">...</span>
        <a class="page-numbers" href="https://aagmaal.bz/page/12/">12</a>
        <a class="next page-numbers" href="https://aagmaal.bz/page/5/">Next</a>
    </nav>
    </body></html>"""

    dirs = []

    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(aagmaal.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(
        aagmaal.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url}),
    )
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.List("https://aagmaal.bz/")

    assert len(dirs) == 1
    assert "Page 4 of 12" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://aagmaal.bz/page/5/"


def test_ott_parses_category_cards_and_pagination(monkeypatch):
    """Test that OTT parses index cards with video counts and pagination."""
    html = """<html><body>
    <div class="vp-tax-index-cards">
        <div class="vp-tax-index-card">
            <a class="vp-tax-index-card__thumb" href="https://aagmaal.bz/ott/ullu/">
                <img src="https://i.ibb.co/ullu.jpg" alt="Ullu Originals"/>
            </a>
            <span class="count">42</span>
        </div>
        <div class="vp-tax-index-card">
            <a class="vp-tax-index-card__thumb" href="https://aagmaal.bz/ott/primeplay/">
                <img src="https://i.ibb.co/primeplay.jpg" alt="PrimePlay"/>
            </a>
            <span class="count">18</span>
        </div>
    </div>
    <div class="vp-pagination">
        <span class="page-numbers current">1</span>
        <a class="page-numbers" href="https://aagmaal.bz/ott/page/3/">3</a>
        <a class="next page-numbers" href="https://aagmaal.bz/ott/page/2/">Next</a>
    </div>
    </body></html>"""

    dirs = []
    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        aagmaal.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url, "mode": mode, "icon": icon}),
    )
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.OTT("https://aagmaal.bz/ott/")

    # 2 category items + 1 next page
    assert len(dirs) == 3
    assert dirs[0]["mode"] == "ListOTT"
    assert "Ullu Originals" in dirs[0]["name"]
    assert "[42 video(s)]" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://aagmaal.bz/ott/ullu/"
    assert dirs[0]["icon"] == "https://i.ibb.co/ullu.jpg"

    assert dirs[1]["mode"] == "ListOTT"
    assert "PrimePlay" in dirs[1]["name"]
    assert "[18 video(s)]" in dirs[1]["name"]

    assert dirs[2]["mode"] == "OTT"
    assert "Next Page" in dirs[2]["name"]
    assert "Page 1 of 3" in dirs[2]["name"]
    assert dirs[2]["url"] == "https://aagmaal.bz/ott/page/2/"


def test_list_ott_parses_articles(monkeypatch):
    """Test that ListOTT parses articles and links to Playvid."""
    html = """<html><body>
    <article class="vp-card">
        <a class="vp-card__thumb" href="https://aagmaal.bz/ullu-episode-1/">
            <img alt="Ullu Episode 1" src="https://i.ibb.co/ep1.jpg"/>
        </a>
    </article>
    <nav class="vp-pagi-wrap">
        <span class="page-numbers current">1</span>
        <a class="next page-numbers" href="https://aagmaal.bz/ott/ullu/page/2/">Next</a>
    </nav>
    </body></html>"""

    downloads = []
    dirs = []
    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        aagmaal.site,
        "add_download_link",
        lambda name, url, mode, icon, desc="", **k: downloads.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(
        aagmaal.site,
        "add_dir",
        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.ListOTT("https://aagmaal.bz/ott/ullu/")

    assert len(downloads) == 1
    assert downloads[0]["name"] == "Ullu Episode 1"
    assert downloads[0]["url"] == "https://aagmaal.bz/ullu-episode-1/"
    assert downloads[0]["mode"] == "Playvid"

    assert len(dirs) == 1
    assert dirs[0]["mode"] == "ListOTT"
    assert dirs[0]["url"] == "https://aagmaal.bz/ott/ullu/page/2/"


def test_playvid_dl_server_links(monkeypatch):
    """Test that Playvid handles .vp-dl-server and .vp-dl-btn link blocks."""
    html = """<html><body>
    <div class="vp-dl-server">LuluStream</div>
    <p><a class="vp-dl-btn" href="https://luluvid.com/d/12345">Download</a></p>
    <div class="vp-dl-server">Playmogo</div>
    <p><a class="vp-dl-btn" href="https://playmogo.com/d/67890">Download</a></p>
    </body></html>"""

    played_urls = []

    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(aagmaal.utils, "selector", lambda title, links: list(links.values())[0])

    class DummyVP:
        def __init__(self, name, download=None):
            class DummyResolve:
                def HostedMediaFile(self, link):
                    return True
            self.resolveurl = DummyResolve()
            class DummyProgress:
                def update(self, *a, **k): pass
                def close(self): pass
            self.progress = DummyProgress()

        def play_from_link_to_resolve(self, url):
            played_urls.append(url)

    monkeypatch.setattr(aagmaal.utils, "VideoPlayer", DummyVP)

    aagmaal.Playvid("https://aagmaal.bz/test-video/", "Test Video")

    assert len(played_urls) == 1
    assert "https://luluvid.com/d/12345" in played_urls or "https://playmogo.com/d/67890" in played_urls


def test_playvid_iframe_fallback(monkeypatch):
    """Test that Playvid falls back to iframe when no direct server links."""
    html = """<html><body>
    <article>
        <iframe src="https://embed.streamtape.com/e/abc123xyz"></iframe>
    </article>
    </body></html>"""

    played_urls = []
    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)

    class DummyVP:
        def __init__(self, name, download=None):
            class DummyResolve:
                def HostedMediaFile(self, link):
                    return False
            self.resolveurl = DummyResolve()
            class DummyProgress:
                def update(self, *a, **k): pass
                def close(self): pass
            self.progress = DummyProgress()

        def play_from_link_to_resolve(self, url):
            played_urls.append(url)

    monkeypatch.setattr(aagmaal.utils, "VideoPlayer", DummyVP)

    aagmaal.Playvid("https://aagmaal.bz/test-video/", "Test Video")

    assert len(played_urls) == 1
    assert played_urls[0] == "https://embed.streamtape.com/e/abc123xyz"


def test_categories_parses_footer_widget(monkeypatch):
    """Test that Categories finds the Categories h3 widget and its ul links."""
    html = load_fixture("categories.html")

    dirs = []

    monkeypatch.setattr(aagmaal.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(aagmaal.site, "add_dir",
                        lambda name, url, mode, icon=None, **k: dirs.append({"name": name, "url": url}))
    monkeypatch.setattr(aagmaal.utils, "eod", lambda: None)

    aagmaal.Categories("https://aagmaal.bz/")

    # 4 categories, sorted alphabetically
    assert len(dirs) == 4
    names = [d["name"] for d in dirs]
    assert names == sorted(names, key=str.lower)
    assert any("Desi Videos" in d["name"] for d in dirs)
    assert any("NueFliks" in d["name"] for d in dirs)


def test_search_without_keyword(monkeypatch):
    """Test that Search without keyword shows search input dialog."""
    search_called = []
    monkeypatch.setattr(aagmaal.site, "search_dir",
                        lambda url, mode: search_called.append(mode))

    aagmaal.Search("https://aagmaal.bz/?s=")

    assert len(search_called) == 1
    assert search_called[0] == "Search"


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search with keyword calls List (not List2)."""
    list_calls = []
    monkeypatch.setattr(aagmaal, "List", lambda url: list_calls.append(url))

    aagmaal.Search("https://aagmaal.bz/?s=", keyword="desi bhabhi")

    assert len(list_calls) == 1
    assert "desi+bhabhi" in list_calls[0]
