"""Tests for TheyAreHuge BeautifulSoup migration."""

from pathlib import Path

from resources.lib.sites import theyarehuge


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "theyarehuge"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_items(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(theyarehuge.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(theyarehuge.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(theyarehuge.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(theyarehuge.site, "add_dir", fake_add_dir)

    theyarehuge.List(
        "https://www.theyarehuge.com/latest-updates/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=1",
        1,
    )

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Big Boobs Porn Video First"
    assert downloads[0]["url"] == "https://www.theyarehuge.com/video/first-video/"
    assert downloads[0]["icon"] == "https://www.theyarehuge.com/thumbs/first.jpg"
    assert downloads[0]["duration"] == "14:00"

    assert downloads[1]["name"] == "Big Boobs Porn Video Second"
    assert downloads[1]["url"] == "https://www.theyarehuge.com/video/second-video/"
    assert downloads[1]["icon"] == "https://www.theyarehuge.com/thumbs/second.jpg"
    assert downloads[1]["duration"] == "07:30"

    assert any(d["name"] == "Next Page (3)" for d in dirs)


def test_tags_parses_items(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(theyarehuge.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(theyarehuge.utils, "eod", lambda: None)

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(theyarehuge.site, "add_dir", fake_add_dir)

    theyarehuge.Tags("https://www.theyarehuge.com/porn-video.tags/")

    assert len(dirs) == 2
    assert dirs[0]["name"] == "Alpha Tag"
    assert "list_videos_common_videos_list" in dirs[0]["url"]
    assert dirs[1]["name"] == "Beta Tag"
