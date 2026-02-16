from pathlib import Path

from resources.lib.sites import foxnxx

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "foxnxx"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_pagination(monkeypatch):
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "duration": kwargs.get("duration"),
                "context": kwargs.get("contextm"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, desc="", **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(foxnxx.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(foxnxx.utils, "eod", lambda *a, **k: None)
    monkeypatch.setattr(foxnxx.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(foxnxx.site, "add_dir", fake_add_dir)

    foxnxx.List("https://foxnxx.com/new")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "First Video"
    assert "video-one" in downloads[0]["url"]
    assert downloads[0]["duration"] == "10:11"
    assert downloads[0]["context"]

    assert downloads[1]["name"] == "Video Two Title"
    assert "video-two" in downloads[1]["url"]
    assert downloads[1]["duration"] == "05:00"

    assert dirs, "Expected pagination entry"
    next_dir = dirs[0]
    assert "Next Page (2)" in next_dir["name"]
    assert next_dir["url"].endswith("/page/2.html")


def test_list_joins_relative_video_urls_and_strips_timer_from_name(monkeypatch):
    html = """
    <div class="thumb">
      <a href="/xxx/sample-video-123.html">
        <img src="/avatar/sample.jpg" alt="Sample Relative Title" />
        <span class="timer">01:13:17</span>
        01:13:17
        Sample Relative Title
      </a>
    </div>
    """

    downloads = []
    monkeypatch.setattr(foxnxx.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(foxnxx.utils, "eod", lambda *a, **k: None)
    monkeypatch.setattr(
        foxnxx.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "icon": iconimage}
        ),
    )

    foxnxx.List("https://foxnxx.com/")

    assert len(downloads) == 1
    assert downloads[0]["url"] == "https://foxnxx.com/xxx/sample-video-123.html"
    assert downloads[0]["icon"] == "https://foxnxx.com/avatar/sample.jpg"
    assert downloads[0]["name"] == "Sample Relative Title"
