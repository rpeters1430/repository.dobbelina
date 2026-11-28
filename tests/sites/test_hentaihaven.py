from unittest.mock import MagicMock

from resources.lib.sites import hentaihaven


def test_site_is_marked_new_hentai_site():
    assert hentaihaven.site.category == "Hentai"
    assert hentaihaven.site.is_new is True


def test_list_parses_watch_and_rule34_cards(monkeypatch):
    html = """
    <div class="grid">
        <a href="/watch/sample-ova/">
            <img src="https://img.hentaihaven.xxx/images/sample.jpg" alt="Sample OVA">
        </a>
        <a href="/watch/?sort=latest">All</a>
    </div>
    <a rel="next" href="/watch/?sort=latest&page=2">Next</a>
    """
    downloads = []
    dirs = []

    monkeypatch.setattr(hentaihaven.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        hentaihaven.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(
        hentaihaven.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(hentaihaven.utils, "eod", lambda: None)

    hentaihaven.List("https://hentaihaven.xxx/")

    assert downloads == [
        {
            "name": "Sample OVA",
            "url": "https://hentaihaven.xxx/watch/sample-ova/",
            "mode": "Playvid",
            "icon": "https://img.hentaihaven.xxx/images/sample.jpg",
        }
    ]
    assert dirs == [
        {
            "name": "Next Page",
            "url": "https://hentaihaven.xxx/watch/?sort=latest&page=2",
            "mode": "List",
        }
    ]


def test_search_formats_query(monkeypatch):
    called_urls = []
    monkeypatch.setattr(hentaihaven, "List", lambda url: called_urls.append(url))

    hentaihaven.Search("https://hentaihaven.xxx/watch/", "school girl")
    assert called_urls == ["https://hentaihaven.xxx/watch/?q=school+girl"]


def test_playvid_direct_source(monkeypatch):
    html = '<video><source src="https://stream2.defeated.xxx/2022files/sample.mp4"></video>'
    vp = MagicMock()
    monkeypatch.setattr(hentaihaven.utils, "VideoPlayer", lambda *a, **k: vp)
    monkeypatch.setattr(hentaihaven.utils, "getHtml", lambda *a, **k: html)

    hentaihaven.Playvid("https://hentaihaven.xxx/watch/sample-ova/", "Sample OVA")
    vp.play_from_direct_link.assert_called_once_with(
        "https://stream2.defeated.xxx/2022files/sample.mp4|Referer=https://hentaihaven.xxx/"
    )
