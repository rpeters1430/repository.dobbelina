import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

MODULE_PATH = PLUGIN_ROOT / "resources" / "lib" / "sites" / "hentai-moon.py"
spec = importlib.util.spec_from_file_location("hentai_moon", MODULE_PATH)
hentai_moon = importlib.util.module_from_spec(spec)
if spec and spec.loader:
    spec.loader.exec_module(hentai_moon)
    sys.modules["hentai_moon"] = hentai_moon


FIXTURE_BASE = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "hentai-moon"


def load_fixture(name: str) -> str:
    return (FIXTURE_BASE / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_pagination(monkeypatch):
    html = load_fixture("listing.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(hentai_moon.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentai_moon.utils, "eod", lambda: None)
    monkeypatch.setattr(hentai_moon.utils, "notify", lambda *a, **k: None)

    def fake_add_download_link(name, url, mode, thumb, desc="", **kwargs):
        downloads.append({
            "name": name,
            "url": url,
            "mode": mode,
            "thumb": thumb,
            "duration": kwargs.get("duration"),
            "quality": kwargs.get("quality"),
        })

    monkeypatch.setattr(hentai_moon.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hentai_moon.site, "add_dir", lambda name, url, mode, icon=None, *a, **k: dirs.append((name, url, mode)))

    hentai_moon.List("https://hentai-moon.com/latest-updates/" + hentai_moon.ajaxlist)

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Sample One"
    assert downloads[0]["quality"] == " [COLOR orange]HD[/COLOR]"
    assert downloads[0]["duration"] == "12:34"
    assert downloads[0]["url"].startswith("https://hentai-moon.com/videos/sample-one")

    assert downloads[1]["name"] == "Sample Two"
    assert downloads[1]["duration"] == "07:00"
    assert downloads[1]["quality"] == ""

    next_entries = [d for d in dirs if d[2] == "List"]
    assert next_entries
    assert next_entries[0][0].startswith("Next Page")
    assert "from=21" in next_entries[0][1]


def test_categories_builds_listing_links(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(hentai_moon.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentai_moon.utils, "eod", lambda: None)
    monkeypatch.setattr(hentai_moon.site, "add_dir", lambda *a, **k: dirs.append(a))

    hentai_moon.Categories("https://hentai-moon.com/categories/")

    assert len(dirs) == 2
    labels = [entry[0] for entry in dirs]
    assert any("Action" in label and "12 videos" in label for label in labels)
    assert any("Comedy" in label for label in labels)
    urls = [entry[1] for entry in dirs]
    assert all(hentai_moon.ajaxcommon in url for url in urls)


def test_series_handles_next_page(monkeypatch):
    html = load_fixture("series.html")
    dirs = []

    monkeypatch.setattr(hentai_moon.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentai_moon.utils, "eod", lambda: None)
    monkeypatch.setattr(hentai_moon.site, "add_dir", lambda *a, **k: dirs.append(a))

    current_url = (
        "https://hentai-moon.com/series/?mode=async&function=get_block&block_id="
        "list_dvds_channels_list&sort_by=title&from=1"
    )
    hentai_moon.Series(current_url)

    # two series entries + one pagination entry
    assert len(dirs) == 3
    next_links = [d for d in dirs if d[0].startswith("Next Page")]
    assert next_links
    assert "from=3" in next_links[0][1]


def test_tags_parse_links(monkeypatch):
    html = load_fixture("tags.html")
    dirs = []

    monkeypatch.setattr(hentai_moon.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentai_moon.utils, "eod", lambda: None)
    monkeypatch.setattr(hentai_moon.site, "add_dir", lambda *a, **k: dirs.append(a))

    hentai_moon.Tags("https://hentai-moon.com/tags/")

    assert len(dirs) == 2
    assert all(hentai_moon.ajaxcommon in entry[1] for entry in dirs)
    labels = [entry[0] for entry in dirs]
    assert "Elf" in labels[0]
    assert any("Dragon" in label for label in labels)
