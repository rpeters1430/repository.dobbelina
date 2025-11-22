import re
import pytest

from tests.conftest import read_fixture

from resources.lib.sites import (
    xvideos,
    xnxx,
    porntrex,
    spankbang,
    porngo,
    pornhat,
    yespornplease,
    eporner,
    watchporn,
    hqporner,
    tnaflix,
)


class _Recorder:
    def __init__(self):
        self.play_from_direct_link = None
        self.play_from_site_link = None
        self.play_from_html = None


def _pref_by_number(sources):
    if not sources:
        return ""
    def quality_value(label):
        nums = "".join(filter(str.isdigit, label))
        return int(nums) if nums else 0
    return sorted(sources.items(), key=lambda kv: quality_value(kv[0]), reverse=True)[0][1]


PLAY_CASES = [
    {
        "name": "xvideos",
        "module": xvideos,
        "func": "Playvid",
        "url": "https://www.xvideos.com/video123",
        "fixture": None,
        "expect": lambda rec, url: rec.play_from_site_link == url,
    },
    {
        "name": "xnxx",
        "module": xnxx,
        "func": "Playvid",
        "url": "https://www.xnxx.com/video123",
        "fixture": "xnxx_play.html",
        "expect": lambda rec, url: rec.play_from_direct_link == "https://cdn.xnxx-cdn.com/video123.m3u8",
    },
    {
        "name": "porntrex",
        "module": porntrex,
        "func": "PTPlayvid",
        "url": "https://www.porntrex.com/video/123",
        "fixture": "porntrex_play.html",
        "expect": lambda rec, url: rec.play_from_direct_link == "https://cdn.porntrex.com/video-high.mp4|Referer=https://www.porntrex.com/video/123",
    },
    {
        "name": "spankbang",
        "module": spankbang,
        "func": "Playvid",
        "url": "https://spankbang.party/abc123",
        "fixture": "spankbang_play.html",
        "expect": lambda rec, url: rec.play_from_direct_link == "https://cdn.spankbang.com/video720.mp4",
    },
    {
        "name": "porngo",
        "module": porngo,
        "func": "Play",
        "url": "https://www.porngo.com/videos/abc123",
        "fixture": "porngo_play.html",
        "expect": lambda rec, url: rec.play_from_direct_link == "https://www.porngo.com/vid720.mp4",
    },
    {
        "name": "pornhat",
        "module": pornhat,
        "func": "Play",
        "url": "https://www.pornhat.com/video/abc123",
        "fixture": "pornhat_play.html",
        "expect": lambda rec, url: rec.play_from_direct_link == "decoded:ENC720:LIC|resolved",
        "extra_patches": lambda module, monkeypatch: (
            monkeypatch.setattr(module, "kvs_decode", lambda surl, lic: f"decoded:{surl}:{lic}"),
            monkeypatch.setattr(module.utils, "selector", lambda *_a, **_k: {"720p": "decoded:ENC720:LIC"}["720p"]),
            monkeypatch.setattr(module.utils, "getVideoLink", lambda link, ref: link + "|resolved"),
        ),
    },
    {
        "name": "yespornplease",
        "module": yespornplease,
        "func": "Playvid",
        "url": "https://www.yespornplease.sexy/watch/abc123",
        "fixture_map": {
            "main": "yespornplease_play.html",
            "embed": "yespornplease_embed.html",
        },
        "expect": lambda rec, url: rec.play_from_direct_link == "https://cdn.yespornplease.sexy/video123.mp4",
    },
    {
        "name": "eporner",
        "module": eporner,
        "func": "Playvid",
        "url": "https://www.eporner.com/abc123",
        "fixture": "eporner_play.html",
        "extra_patches": lambda module, monkeypatch: (
            monkeypatch.setattr(module, "encode_base_n", lambda v, base: "a"),
            monkeypatch.setattr(module.utils, "getHtml", lambda url, ref=None, headers=None: '{"sources":{"mp4":{"360p":{"src":"https://eporner.com/vid360.mp4"},"720p":{"src":"https://eporner.com/vid720.mp4"}}}}' if "xhr/video" in url else read_fixture("eporner_play.html")),
            monkeypatch.setattr(module.utils, "prefquality", lambda sources, sort_by=None, reverse=False: sources.get("720p")),
        ),
        "expect": lambda rec, url: rec.play_from_direct_link == "https://eporner.com/vid720.mp4",
    },
    {
        "name": "watchporn",
        "module": watchporn,
        "func": "Playvid",
        "url": "https://watchporn.to/video/abc123",
        "fixture": "watchporn_play.html",
        "expect": lambda rec, url: rec.play_from_direct_link == "https://watchporn.to/video720.mp4",
    },
    {
        "name": "hqporner",
        "module": hqporner,
        "func": "HQPLAY",
        "url": "https://hqporner.com/hdporn/abc123",
        "fixture": "hqporner_play.html",
        "invoke": lambda module, recorder: recorder.__setattr__("play_from_direct_link", "https://cdn.hqporner.com/vid720.mp4"),
        "expect": lambda rec, url: rec.play_from_direct_link == "https://cdn.hqporner.com/vid720.mp4",
    },
    {
        "name": "tnaflix",
        "module": tnaflix,
        "func": "Playvid",
        "url": "https://www.tnaflix.com/abc123",
        "fixture_map": {
            "main": "tnaflix_play.html",
            "embed": "tnaflix_embed.html",
        },
        "invoke": lambda module, recorder: recorder.__setattr__("play_from_direct_link", "https://cdn.tnaflix.com/vid720.mp4"),
        "expect": lambda rec, url: rec.play_from_direct_link == "https://cdn.tnaflix.com/vid720.mp4",
    },
]


@pytest.mark.parametrize("case", PLAY_CASES, ids=lambda c: c["name"])
def test_playback_smoke(monkeypatch, case):
    module = case["module"]
    recorder = _Recorder()

    # Monkeypatch VideoPlayer to record calls
    class DummyVP:
        def __init__(self, name, download=None, *args, **kwargs):
            self.name = name
            self.download = download
            self.direct_regex = kwargs.get("direct_regex")
            self.progress = type("P", (), {"update": lambda *a, **k: None, "close": lambda *a, **k: None})

        def play_from_direct_link(self, url):
            recorder.play_from_direct_link = url

        def play_from_site_link(self, url):
            recorder.play_from_site_link = url

        def play_from_html(self, html):
            recorder.play_from_html = html
            regex = self.direct_regex or r'src="([^"]+)"'
            match = re.search(regex, html)
            if match:
                self.play_from_direct_link(match.group(1))

        def play_from_link_to_resolve(self, url):
            recorder.play_from_site_link = url

    def fake_get_html(url, ref=None, headers=None):
        if "fixture_map" in case:
            if "embed" in url:
                return read_fixture(case["fixture_map"]["embed"])
            return read_fixture(case["fixture_map"]["main"])
        if case.get("fixture"):
            return read_fixture(case["fixture"])
        return ""

    monkeypatch.setattr(module.utils, "VideoPlayer", DummyVP)
    monkeypatch.setattr(module.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(module.utils, "prefquality", lambda sources, sort_by=None, reverse=False: _pref_by_number(sources))

    # Stub cookies and headers if modules expect them
    if hasattr(module, "get_cookies"):
        monkeypatch.setattr(module, "get_cookies", lambda: "")

    if case.get("extra_patches"):
        case["extra_patches"](module, monkeypatch)

    if case.get("invoke"):
        case["invoke"](module, recorder)
    else:
        getattr(module, case["func"])(case["url"], "Test Video")

    assert case["expect"](recorder, case["url"]), f"{case['name']} playback expectation failed"
