"""Tests for TabooTube BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import tabootube


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "tabootube"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(tabootube.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(tabootube.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(tabootube.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(tabootube.site, "add_dir", fake_add_dir)

    tabootube.List(
        "https://www.tabootube.xxx/?mode=async&function=get_block&block_id=list_videos_most_recent_videos&sort_by=post_date&from=1",
        1,
    )

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Taboo Video"
    assert downloads[0]["url"] == "https://www.tabootube.xxx/video/first-video/"
    assert downloads[0]["icon"] == "https://www.tabootube.xxx/thumbs/first.jpg"
    assert downloads[0]["duration"] == "12:34"

    assert downloads[1]["name"] == "Second Taboo Video"
    assert downloads[1]["url"] == "https://www.tabootube.xxx/video/second-video/"
    assert downloads[1]["icon"] == "https://www.tabootube.xxx/thumbs/second.jpg"
    assert downloads[1]["duration"] == "03:21"

    assert any(d["name"] == "Next Page (2)" for d in dirs)


def test_categories_parses_items(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(tabootube.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(tabootube.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(tabootube.site, "add_dir", fake_add_dir)

    tabootube.Categories("https://www.tabootube.xxx/categories/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Category One"
    assert "list_videos_common_videos_list" in dirs[0]["url"]
    assert dirs[1]["name"] == "Category Two"


def test_tags_parses_items(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(tabootube.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(tabootube.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(tabootube.site, "add_dir", fake_add_dir)

    tabootube.Tags("https://www.tabootube.xxx/tags/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Alpha"
    assert "list_videos_common_videos_list" in dirs[0]["url"]
    assert dirs[1]["name"] == "Beta"
