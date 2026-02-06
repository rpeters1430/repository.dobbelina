from resources.lib.sites import pornxp
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", *args, **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": pornxp.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": pornxp.site.get_full_mode(mode),
            }
        )


def test_list_populates_download_links(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, pornxp, {"pornxp.com-mirror.com/": "sites/pornxp/list.html"}
    )
    monkeypatch.setattr(pornxp.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(pornxp.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(pornxp.utils, "eod", lambda *args, **kwargs: None)

    pornxp.List("https://pornxp.com-mirror.com/")

    # Check first item
    assert recorder.downloads[0] == {
        "name": "NO BLOW-UP-DOLL SON, STEP-MOMMY IS HERE",
        "url": "https://pornxp.com-mirror.com/videos/93214129780",
        "mode": "pornxp.Playvid",
        "icon": "https://ii.porn-xp.com/9321412964780.jpg",
        "duration": "21:17",
    }

    # Check pagination
    assert recorder.dirs == [
        {
            "name": "Next Page",
            "url": "https://pornxp.com-mirror.com/?page=2",
            "mode": "pornxp.List",
        }
    ]


def test_playvid_finds_sources(monkeypatch):
    captured = {}

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            captured["videourl"] = url

    # Simplified video page fixture
    video_html = """
    <video>
        <source src="https://v.pornxp.com/1080p.mp4" title="1080p">
        <source src="https://v.pornxp.com/720p.mp4" title="720p">
    </video>
    """

    monkeypatch.setattr(pornxp.utils, "getHtml", lambda *a, **k: video_html)
    monkeypatch.setattr(pornxp.utils, "VideoPlayer", _DummyVP)

    pornxp.Playvid("https://pornxp.com-mirror.com/videos/123", "Example")

    assert captured["videourl"] == "https://v.pornxp.com/1080p.mp4"
