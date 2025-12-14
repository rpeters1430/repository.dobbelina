"""Tests for MrSexe BeautifulSoup migration."""
from pathlib import Path

from resources.lib.sites import mrsexe


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "mrsexe"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_next(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(mrsexe.utils, "getHtml", lambda url, ref='': html)

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"name": name, "url": url, "mode": mode, "img": iconimage, "duration": kwargs.get("duration"), "quality": kwargs.get("quality")})

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(mrsexe.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(mrsexe.site, "add_dir", fake_add_dir)

    mrsexe.List("https://www.mrsexe.com/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Video One"
    assert downloads[0]["quality"] == "hd"
    assert downloads[1]["duration"] == "05:00"
    assert any(d["mode"] == "List" for d in dirs)


def test_playvid_uses_clic_and_plays(monkeypatch):
    video_page = load_fixture("video_page.html")
    clic_page = load_fixture("clic_page.html")
    play_calls = []

    def fake_get_html(url, ref=None, hdr=None):
        if "clic.php" in url:
            return clic_page
        return video_page

    monkeypatch.setattr(mrsexe.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(mrsexe.utils, "playvid", lambda url, name, download=None: play_calls.append((url, name, download)))

    mrsexe.Playvid("https://www.mrsexe.com/video-1", "Sample Video")

    assert play_calls
    assert play_calls[0][0].endswith("video.mp4")
