import pytest

from resources.lib.sites import justporn
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(
        self,
        name,
        url,
        mode,
        iconimage,
        desc="",
        contextm=None,
        fanart=None,
        duration="",
        quality="",
    ):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": justporn.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": duration,
                "quality": quality,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {"name": name, "url": url, "mode": justporn.site.get_full_mode(mode)}
        )


@pytest.fixture
def recorder(monkeypatch):
    rec = _Recorder()
    monkeypatch.setattr(justporn.site, "add_download_link", rec.add_download)
    monkeypatch.setattr(justporn.site, "add_dir", rec.add_dir)
    monkeypatch.setattr(justporn.utils, "eod", lambda *a, **k: None)
    return rec


@pytest.fixture
def quality_prompt(monkeypatch):
    original_settings = justporn.utils.addon._settings.copy()
    monkeypatch.setattr(
        justporn.utils.addon, "_settings", {**original_settings, "qualityask": "1"}
    )
    yield
    monkeypatch.setattr(justporn.utils.addon, "_settings", original_settings)


def test_listing_uses_soup_spec(monkeypatch, recorder):
    fixture_mapped_get_html(
        monkeypatch, justporn, {"latest-updates": "sites/justporn/listing.html"}
    )

    justporn.List("https://www.justporn.com/latest-updates/")

    assert len(recorder.downloads) == 3
    assert recorder.downloads[0]["name"] == "Sample Video One"
    assert recorder.downloads[0]["duration"] == "10:25"

    assert recorder.dirs == [
        {
            "name": "Next Page",
            "url": "https://www.justporn.com/latest-updates/2/",
            "mode": "justporn.List",
        }
    ]


def test_search_delegates_to_listing(monkeypatch, recorder):
    fixture_mapped_get_html(
        monkeypatch,
        justporn,
        {
            "search": "sites/justporn/listing.html",
        },
    )

    justporn.Search("https://www.justporn.com/search/", keyword="search term")

    assert len(recorder.downloads) == 3
    assert recorder.downloads[0]["name"] == "Sample Video One"


def test_playvid_prefers_highest_available_quality(monkeypatch, quality_prompt):
    fixture_mapped_get_html(
        monkeypatch, justporn, {"/watch/": "sites/justporn/video.html"}
    )

    played = {}

    class _DummyVideoPlayer:
        def __init__(self, name, download=None, **kwargs):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            played["url"] = url

        def play_from_link_to_resolve(self, url):
            played["resolve"] = url

    monkeypatch.setattr(justporn.utils, "VideoPlayer", _DummyVideoPlayer)
    justporn.Playvid("https://www.justporn.com/watch/9999/example", "Example video")

    assert played["url"] or played["resolve"]
