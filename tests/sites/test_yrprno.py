from pathlib import Path

from resources.lib.sites import yrprno


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "yrprno"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_uses_soup_and_pagination(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(yrprno.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(yrprno.utils, "eod", lambda: None)
    monkeypatch.setattr(
        yrprno.site,
        "add_download_link",
        lambda name,
        url,
        mode,
        iconimage,
        desc="",
        quality="",
        duration="",
        contextm=None,
        **kwargs: downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "quality": quality,
                "duration": duration,
                "contextm": contextm,
            }
        ),
    )
    monkeypatch.setattr(
        yrprno.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, contextm=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode, "contextm": contextm}
        ),
    )

    yrprno.List("https://www.yrprno.com/most-recent/")

    assert len(downloads) == 2  # skip modelfeed
    assert downloads[0]["name"] == "Video One"
    assert downloads[0]["url"] == "https://www.yrprno.com/video-one"
    assert downloads[0]["quality"] == "HD"
    assert downloads[1]["url"] == "/video-two"
    assert downloads[0]["contextm"] == "yrprno.Related"

    next_dirs = [d for d in dirs if d["mode"] == "yrprno.List"]
    assert len(next_dirs) == 1
    assert next_dirs[0]["url"] == "page2.html"
    assert "(2/3)" in next_dirs[0]["name"]
    assert next_dirs[0]["contextm"] is not None


def test_categories(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(yrprno.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(yrprno.utils, "eod", lambda: None)
    monkeypatch.setattr(
        yrprno.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    yrprno.Categories("https://www.yrprno.com/channels/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Anal"
    assert dirs[0]["url"] == "https://www.yrprno.com/cat/anal"
    assert dirs[1]["url"] == "/cat/teen"
