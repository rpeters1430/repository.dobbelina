from pathlib import Path

from resources.lib.sites import sexyporn


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sexyporn"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_pagination(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(sexyporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(sexyporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        sexyporn.site,
        "add_download_link",
        lambda name,
        url,
        mode,
        iconimage,
        desc="",
        quality="",
        duration="",
        **kwargs: downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "quality": quality,
                "duration": duration,
            }
        ),
    )
    monkeypatch.setattr(
        sexyporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    sexyporn.List("https://www.sexyporn.xxx/")

    assert len(downloads) == 3
    assert downloads[0]["name"] == "Video One"
    assert downloads[0]["url"] == "https://www.sexyporn.xxx/videos/video-one"
    assert downloads[0]["quality"] == "HD"
    assert downloads[1]["url"] == "https://www.sexyporn.xxx/videos/video-two"
    assert downloads[2]["duration"] == "05:55"

    next_dirs = [d for d in dirs if d["mode"] == "List"]
    assert len(next_dirs) == 1
    assert next_dirs[0]["url"] == "https://www.sexyporn.xxx/page/2/"
    assert "Next Page" in next_dirs[0]["name"]


def test_categories(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(sexyporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(sexyporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        sexyporn.site,
        "add_dir",
        lambda name, url, mode, iconimage=None, **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    sexyporn.Categories("https://www.sexyporn.xxx/categories")

    assert len(dirs) == 3
    assert dirs[0]["name"] == "Anal"
    assert dirs[0]["url"] == "https://www.sexyporn.xxx/category/anal"
    assert dirs[2]["name"] == "MILF"


def test_playvid_uses_direct_source(monkeypatch):
    html = load_fixture("video.html")
    played = {}

    class DummyVP:
        def __init__(self, name, download=None):
            self.name = name
            self.progress = type("p", (), {"update": lambda *a, **k: None})

        def play_from_direct_link(self, url):
            played["url"] = url

        def play_from_link_to_resolve(self, url):
            played["resolve"] = url

    monkeypatch.setattr(sexyporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(sexyporn.utils, "VideoPlayer", DummyVP)

    sexyporn.Playvid("https://www.sexyporn.xxx/videos/video-one", "Video One")

    assert "url" in played
    assert (
        played["url"]
        == "https://cdn.sexyporn.xxx/videos/video-one.mp4|referer=https://www.sexyporn.xxx/"
    )
