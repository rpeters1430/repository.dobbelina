"""Tests for legacy listing helpers in utils."""

from resources.lib import utils


class DummySite:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.calls = []

    def add_download_link(self, *args, **kwargs):
        self.calls.append((args, kwargs))


def test_videos_list_parses_entries():
    site = DummySite("demo", "https://example.com/")
    html = (
        'DELIM <a href="/video1">Video One</a>'
        '<img src="//img1" />'
        '<span class="dur">1:00</span>'
        'DELIM <a href="video2">Video Two</a>'
        '<img src="/img2" />'
        '<span class="dur">2:00</span>'
    )

    utils.videos_list(
        site=site,
        playvid="demo.Playvid",
        html=html,
        delimiter="DELIM",
        re_videopage=r"href=\"([^\"]+)\"",
        re_name=r">([^<]+)</a>",
        re_img=r"src=\"([^\"]+)\"",
        re_duration=r"class=\"dur\">([^<]+)",
        contextm="demo.Related",
    )

    assert len(site.calls) == 2
    first_args = site.calls[0][0]
    assert first_args[0] == "Video One"
    assert first_args[1].startswith("https://example.com/")


def test_lookupinfo_getinfo_extracts_items(monkeypatch):
    html = '<section>START<a href="/a">Alpha</a>END</section>'
    calls = []

    monkeypatch.setattr(utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(utils.dialog, "select", lambda *a, **k: 0, raising=False)
    monkeypatch.setattr(
        utils.xbmc, "executebuiltin", lambda cmd: calls.append(cmd), raising=False
    )

    lookup = utils.LookupInfo(
        siteurl="https://example.com",
        url="https://example.com/list",
        default_mode="demo.Playvid",
        lookup_list=[("Item", r"href=\"([^\"]+)\">([^<]+)", None)],
        starthtml="START",
        stophtml="END",
    )

    result = lookup.getinfo()

    assert result is None
    assert calls
    assert calls[0].startswith("Container.Update(")
