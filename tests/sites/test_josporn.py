"""Tests for josporn site implementation."""

import os
from resources.lib.sites import josporn
from resources.lib import utils


def test_josporn_list_parsing(monkeypatch):
    """Test that josporn list parsing correctly extracts videos."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")  
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Mock get_html_with_cloudflare_retry
    monkeypatch.setattr(utils, "get_html_with_cloudflare_retry", lambda url, *args, **kwargs: (html, ""))
    monkeypatch.setattr(utils, "eod", lambda: None)

    # We need to capture calls to add_download_link
    captured_items = []
    def fake_add_download_link(name, url, mode, icon, desc="", **kwargs):
        captured_items.append({
            "name": name, "url": url, "mode": mode, "thumb": icon
        })
        
    monkeypatch.setattr(josporn.site, "add_download_link", fake_add_download_link)

    # Run List
    josporn.List("https://josporn.club/videos/")

    assert len(captured_items) > 0
    assert captured_items[0]["name"] == "The red-haired bitch is always ready to suck and fuck"


def test_josporn_categories_parsing(monkeypatch):
    """Test that josporn categories parsing correctly extracts categories."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")  
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "get_html_with_cloudflare_retry", lambda url, *args, **kwargs: (html, ""))
    monkeypatch.setattr(utils, "eod", lambda: None)

    captured_dirs = []
    def fake_add_dir(name, url, mode, icon=None, **kwargs):
        captured_dirs.append({
            "name": name, "url": url, "mode": mode
        })
        
    monkeypatch.setattr(josporn.site, "add_dir", fake_add_dir)

    josporn.Categories("https://josporn.club/categories/")

    assert len(captured_dirs) > 0
    # Categories are in #leftcategories a
    assert any("Amateur" in d["name"] for d in captured_dirs)


def test_josporn_list_pagination(monkeypatch):
    """Test that josporn pagination finds Next link."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")  
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "get_html_with_cloudflare_retry", lambda url, *args, **kwargs: (html, ""))
    monkeypatch.setattr(utils, "eod", lambda: None)

    captured_dirs = []
    monkeypatch.setattr(josporn.site, "add_download_link", lambda *a, **k: None)        
    
    def fake_add_dir(name, url, mode, icon=None, **kwargs):
        captured_dirs.append({
            "name": name, "url": url, "mode": mode
        })
        
    monkeypatch.setattr(josporn.site, "add_dir", fake_add_dir)

    josporn.List("https://josporn.club/videos/")

    # Next Page (2)
    next_pages = [d for d in captured_dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1


def test_josporn_playvid_extraction(monkeypatch):
    """Test that josporn Playvid extracts video URL."""
    html = '<video><source src="https://cdn.com/video.mp4" type="video/mp4"></video>'

    monkeypatch.setattr(utils, "get_html_with_cloudflare_retry", lambda url, *args, **kwargs: (html, ""))

    played = {}
    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('MockProgress', (), {'update': lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            played["url"] = url

    monkeypatch.setattr(utils, "VideoPlayer", MockVideoPlayer)

    # Run Playvid
    josporn.Playvid("https://josporn.club/videos/30348", "Test Video")

    assert played.get("url").startswith("https://cdn.com/video.mp4")
    assert "|Referer=" in played.get("url")
