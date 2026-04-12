import os
from resources.lib import utils
from resources.lib.sites import josporn

def test_josporn_list_parsing(monkeypatch):
    """Test that josporn list parsing correctly extracts videos."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Mock getHtml to return our fixture
    monkeypatch.setattr(utils, "getHtml", lambda url, *args, **kwargs: html)

    # We need to capture calls to add_download_link
    captured_items = []
    monkeypatch.setattr(josporn.site, "add_download_link", 
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append({
                            "name": name, "url": url, "mode": mode, "thumb": thumb
                        }))
    
    # Run List
    josporn.List("https://josporn.club/videos/")
    
    assert len(captured_items) > 0
    # Check a specific item if possible
    assert any("red-haired" in item["name"].lower() for item in captured_items)
    assert all(item["mode"] == "Playvid" for item in captured_items)
    assert all("/videos/" in item["url"] for item in captured_items)

def test_josporn_categories_parsing(monkeypatch):
    """Test that josporn categories parsing correctly extracts categories."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_home.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, *args, **kwargs: html)

    captured_dirs = []
    monkeypatch.setattr(josporn.site, "add_dir", 
                        lambda name, url, mode, thumb, **kwargs: captured_dirs.append({
                            "name": name, "url": url, "mode": mode
                        }))
    
    josporn.Categories("https://josporn.club/categories/")
    
    assert len(captured_dirs) > 0
    assert any("Amateur" in item["name"] for item in captured_dirs)
    assert any("Asians" in item["name"] for item in captured_dirs)


def test_josporn_list_pagination(monkeypatch):
    """Test that josporn pagination finds Next link in .mobnavigation."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, *args, **kwargs: html)

    captured_items = []
    captured_dirs = []
    monkeypatch.setattr(josporn.site, "add_download_link",
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append(None))
    monkeypatch.setattr(josporn.site, "add_dir",
                        lambda name, url, mode, thumb, **kwargs: captured_dirs.append({
                            "name": name, "url": url, "mode": mode
                        }))

    josporn.List("https://josporn.club/videos/")

    next_pages = [d for d in captured_dirs if d["name"] == "Next Page"]
    assert len(next_pages) == 1
    assert "/page/2/" in next_pages[0]["url"]
    assert next_pages[0]["mode"] == "List"


def test_josporn_search(monkeypatch):
    """Test that josporn search correctly dispatches with text param."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, *args, **kwargs: html)
    
    list_urls = []
    monkeypatch.setattr(josporn, "List", lambda url, *args, **kwargs: list_urls.append(url))
    
    josporn.Search("https://josporn.club/search/", "test keyword")
    
    assert len(list_urls) == 1
    assert "search/?text=test+keyword" in list_urls[0]


def test_josporn_playvid_extraction(monkeypatch):
    """Test that josporn Playvid extracts video URL from Playerjs or video tag."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_video.html")
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
    josporn.Playvid("https://josporn.club/videos/30348-the-red-haired-bitch/", "Test Video")
    
    assert mock_vp_instance is not None
    assert mock_vp_instance.played_url is not None
    assert "servisehost.com" in mock_vp_instance.played_url
    assert ".mp4" in mock_vp_instance.played_url
