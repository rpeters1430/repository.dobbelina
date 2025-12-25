"""Tests for NL tubes BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import nltubes


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "nltubes"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_poldertube_branch(monkeypatch):
    html = load_fixture("listing_poldertube.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(nltubes.utils, "getHtml", lambda url, ref="": html)
    monkeypatch.setattr(
        nltubes.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "duration": kwargs.get("duration")}
        ),
    )
    monkeypatch.setattr(
        nltubes.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    nltubes.NLVIDEOLIST("https://www.poldertube.nl/page1")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Video One"
    assert downloads[1]["duration"] == "04:00"
    assert any("Next Page" in d["name"] for d in dirs)


def test_list_sextube_branch(monkeypatch):
    html = load_fixture("listing_sextube.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(nltubes.utils, "getHtml", lambda url, ref="": html)
    monkeypatch.setattr(
        nltubes.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url}
        ),
    )
    monkeypatch.setattr(
        nltubes.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url}
        ),
    )

    nltubes.NLVIDEOLIST("https://www.sextube.nl/page1")

    assert len(downloads) == 2
    assert any("Next Page" in d["name"] for d in dirs)


def test_playvid_uses_meta(monkeypatch):
    html = load_fixture("video.html")
    plays = []

    class FakeVP:
        def __init__(self, name, download=None):
            self.progress = type(
                "p",
                (),
                {
                    "update": lambda *args, **kwargs: None,
                    "close": lambda *args, **kwargs: None,
                },
            )()

        def play_from_direct_link(self, url):
            plays.append(url)

    monkeypatch.setattr(nltubes.utils, "getHtml", lambda url, ref=None, hdr=None: html)
    monkeypatch.setattr(nltubes.utils, "VideoPlayer", FakeVP)

    nltubes.NLPLAYVID("https://www.sextube.nl/video/1", "Test")

    assert plays
    assert "Referer=" in plays[0]
