from pathlib import Path

from resources.lib.sites import watchmdh


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "watchmdh"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items_and_pagination(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(watchmdh.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(watchmdh.utils, "eod", lambda: None)

    def fake_add_download_link(
        name,
        url,
        mode,
        iconimage,
        desc="",
        duration="",
        quality="",
        contextm=None,
        **kwargs,
    ):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": duration,
                "quality": quality,
                "contextm": contextm,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, contextm=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "contextm": contextm})

    monkeypatch.setattr(watchmdh.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(watchmdh.site, "add_dir", fake_add_dir)

    watchmdh.List("https://watchdirty.is/latest-updates/")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Video One"
    assert downloads[0]["url"] == "https://watchdirty.is/video-one"
    assert downloads[0]["quality"] == "HD"
    assert downloads[0]["contextm"] is not None
    assert downloads[1]["duration"] == "08:00"

    next_dirs = [d for d in dirs if d["mode"] == "List"]
    assert len(next_dirs) == 1
    assert "Next Page" in next_dirs[0]["name"]
    assert next_dirs[0]["contextm"] is not None
