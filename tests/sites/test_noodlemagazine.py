"""Tests for Noodlemagazine BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import noodlemagazine


FIXTURE_DIR = (
    Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "noodlemagazine"
)


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(noodlemagazine.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(noodlemagazine.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(
        noodlemagazine.site, "add_download_link", fake_add_download_link
    )
    monkeypatch.setattr(noodlemagazine.site, "add_dir", fake_add_dir)

    noodlemagazine.List("https://noodlemagazine.com/video/?sort=0&hd=0&len=any&p=1", 1)

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Noodle"
    assert downloads[0]["url"] == "https://noodlemagazine.com/video/first-video/"
    assert downloads[0]["duration"] == "11:11"
    assert downloads[0]["quality"] == " [COLOR orange]HD[/COLOR]"
    assert downloads[0]["icon"].startswith(
        "https://cdn.noodlemagazine.com/getVideoPreview/abc.jpg|User-Agent="
    )

    assert downloads[1]["name"] == "Second Noodle"
    assert downloads[1]["url"] == "https://noodlemagazine.com/video/second-video/"
    assert downloads[1]["duration"] == "05:05"
    assert downloads[1]["quality"] == ""
    assert (
        "cdn.noodlemagazine.com/thumbs/second.jpg|User-Agent=" in downloads[1]["icon"]
    )

    assert any(d["name"] == "Next Page (2)" for d in dirs)
