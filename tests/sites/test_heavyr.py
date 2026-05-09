"""Tests for heavyr site implementation."""

from unittest.mock import MagicMock, patch
from resources.lib.sites import heavyr


def test_list_videos(monkeypatch):
    with open("tests/fixtures/sites/heavyr_list.html", "r", encoding="utf-8") as f:
        html = f.read()

    mock_site = MagicMock()
    monkeypatch.setattr(heavyr, "site", mock_site)

    def fake_get_html_cf(url, *args, **kwargs):
        return html, ""

    monkeypatch.setattr(heavyr.utils, "get_html_with_cloudflare_retry", fake_get_html_cf)
    monkeypatch.setattr(heavyr.utils, "eod", lambda: None)

    heavyr.List("https://www.heavy-r.com/")

    # Verify some videos were added
    assert mock_site.add_download_link.called


def test_main_adds_nav_and_calls_list(monkeypatch):
    mock_site = MagicMock()
    mock_site.url = "https://www.heavy-r.com/"
    monkeypatch.setattr(heavyr, "site", mock_site)
    
    list_calls = []
    monkeypatch.setattr(heavyr, "List", lambda url: list_calls.append(url))

    heavyr.Main()

    assert mock_site.add_dir.called
    assert list_calls == ["https://www.heavy-r.com/"]
