"""Tests for tubxporn.com site implementation."""

import os
from resources.lib import utils
from resources.lib.sites import tubxporn

def test_tubxporn_list_parsing(monkeypatch):
    """Test that tubxporn list parsing correctly extracts videos using real fixture."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "tubxporn_list.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Mock getHtml to return our fixture
    monkeypatch.setattr(utils, "getHtml", lambda url, *args, **kwargs: html)

    # We need to capture calls to add_download_link
    captured_items = []
    monkeypatch.setattr(tubxporn.site, "add_download_link", 
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append({
                            "name": name, "url": url, "mode": mode, "thumb": thumb
                        }))
    
    # Run List
    tubxporn.List("https://web.tubxporn.com/latest-updates/")
    
    assert len(captured_items) > 0
    # Check a specific item if possible
    assert any("Young Guy Fucks Curvy Sexy MILF" in item["name"] for item in captured_items)
    assert all(item["mode"] == "tubxporn.Playvid" for item in captured_items)
    assert all("/videos/" in item["url"] for item in captured_items)


def test_tubxporn_playvid_extraction(monkeypatch):
    """Test that tubxporn Playvid extracts video URL from data-c or video tag."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "tubxporn_video.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, *args, **kwargs: html)
    
    # Mock VideoPlayer
    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.played_url = None
            self.progress = type('MockProgress', (), {'update': lambda *a, **k: None})()
            
        def play_from_direct_link(self, url):
            self.played_url = url

    mock_vp_instance = None
    def mock_vp_factory(name, download=None):
        nonlocal mock_vp_instance
        mock_vp_instance = MockVideoPlayer(name, download)
        return mock_vp_instance

    monkeypatch.setattr(utils, "VideoPlayer", mock_vp_factory)
    
    # Run Playvid
    tubxporn.Playvid("https://web.tubxporn.com/videos/20554/young-guy-fucks-curvy-sexy-milf/", "Test Video")
    
    assert mock_vp_instance is not None
    assert mock_vp_instance.played_url is not None
    # It should find either the constructed URL or the one from the video tag
    assert "vstors.top" in mock_vp_instance.played_url or "vstor.top" in mock_vp_instance.played_url
    assert ".mp4" in mock_vp_instance.played_url


def test_search_with_keyword(monkeypatch):
    """Test that Search with keyword calls List with encoded query."""
    list_calls = []

    def fake_list(url):
        list_calls.append(url)

    monkeypatch.setattr(tubxporn, "List", fake_list)

    tubxporn.Search("https://tubxporn.com/search/", keyword="test query")

    assert len(list_calls) == 1
    assert "q=test%20query" in list_calls[0]
