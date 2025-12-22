from pathlib import Path

from resources.lib.sites import xmegadrive


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "xmegadrive"


def load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_extract_list_items_parses_videos():
    html = load_fixture("latest_updates.html")
    items = xmegadrive._extract_list_items(html)

    assert items, "Expected at least one video item"

    url, name, thumb, duration = items[0]
    assert "/videos/" in url
    assert name
    assert thumb
    assert duration


def test_find_next_page_detects_pagination():
    html = load_fixture("latest_updates.html")
    current_url = "https://www.xmegadrive.com/latest-updates/"

    next_url = xmegadrive._find_next_page(html, current_url)

    assert next_url is not None
    assert "/latest-updates/2/" in next_url


def test_extract_video_url_from_flashvars(monkeypatch):
    html = load_fixture("video_page.html")

    monkeypatch.setattr(
        xmegadrive,
        "kvs_decode",
        lambda url, license_code: "https://www.xmegadrive.com/get_file/3/test.mp4",
    )

    video_url = xmegadrive._extract_video_url(html)

    assert video_url.startswith("https://")
    assert ".mp4" in video_url
