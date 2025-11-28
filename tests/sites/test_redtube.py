"""Tests for RedTube site implementation using BeautifulSoup parsing."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from resources.lib.sites import redtube

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "redtube"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos(monkeypatch):
    """Ensure List uses BeautifulSoup selectors to parse videos and pagination."""
    html_data = load_fixture("listing.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(redtube.utils, "getHtml", lambda url, referer=None, headers=None: html_data)
    monkeypatch.setattr(redtube.site, "add_download_link", lambda *args, **kwargs: downloads.append({
        "name": args[0],
        "url": args[1],
        "mode": args[2],
        "icon": args[3],
        "duration": kwargs.get("duration", ""),
    }))
    monkeypatch.setattr(redtube.site, "add_dir", lambda *args, **kwargs: dirs.append({
        "name": args[0],
        "url": args[1],
    }))
    monkeypatch.setattr(redtube.utils, "eod", lambda: None)

    redtube.List("https://www.redtube.com/")

    assert [item["name"] for item in downloads] == ["First Video Title", "Second Video Title"]
    assert downloads[0]["url"] == "https://www.redtube.com/123456/video/first-video"
    assert downloads[1]["url"] == "https://www.redtube.com/7891011/video/second-video"
    assert downloads[0]["duration"] == "10:12"
    assert downloads[1]["duration"] == "08:45"
    assert downloads[0]["icon"].endswith("first.jpg")
    assert downloads[1]["icon"].endswith("second.jpg")

    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert next_pages[0]["url"] == "https://www.redtube.com/most-viewed?page=3"
    assert next_pages[0]["name"] == "Next Page (3)"


def test_categories_parses_and_sorts(monkeypatch):
    """Ensure Categories uses BeautifulSoup to extract and sort category entries."""
    html_data = load_fixture("categories.html")

    dirs = []

    monkeypatch.setattr(redtube.utils, "getHtml", lambda url, referer=None, headers=None: html_data)
    monkeypatch.setattr(redtube.site, "add_dir", lambda *args, **kwargs: dirs.append({
        "name": args[0],
        "url": args[1],
    }))
    monkeypatch.setattr(redtube.utils, "eod", lambda: None)

    redtube.Categories("https://www.redtube.com/categories")

    assert [d["name"] for d in dirs] == ["Anal", "Blonde", "MILF"]
    assert [d["url"] for d in dirs] == [
        "https://www.redtube.com/category/anal",
        "https://www.redtube.com/category/blonde",
        "https://www.redtube.com/category/milf",
    ]


def test_search_builds_correct_url(monkeypatch):
    """Search should delegate to List with encoded keywords."""
    called = []

    monkeypatch.setattr(redtube, "List", lambda url: called.append(url))

    redtube.Search("https://www.redtube.com/?search=", keyword="test query")

    assert called == ["https://www.redtube.com/?search=test+query"]

