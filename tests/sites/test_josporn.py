import pytest
import os
from resources.lib import utils
from resources.lib.sites import josporn

def test_josporn_list_parsing(monkeypatch):
    """Test that josporn list parsing correctly extracts videos."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_list.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Mock getHtml to return our fixture
    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

    # We need to capture calls to add_download_link
    captured_items = []
    monkeypatch.setattr(josporn.site, "add_download_link", 
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append({
                            "name": name, "url": url, "mode": mode, "thumb": thumb
                        }))
    
    # Run List
    josporn.List("https://josporn.club/latest-updates/")
    
    assert len(captured_items) > 0
    # Check a specific item if possible
    assert any("anal bliss" in item["name"].lower() for item in captured_items)
    assert all(item["mode"] == "Playvid" for item in captured_items)
    assert all("/videos/" in item["url"] for item in captured_items)

def test_josporn_categories_parsing(monkeypatch):
    """Test that josporn categories parsing correctly extracts categories."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "josporn_home.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

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

    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

    captured_items = []
    captured_dirs = []
    monkeypatch.setattr(josporn.site, "add_download_link",
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append(None))
    monkeypatch.setattr(josporn.site, "add_dir",
                        lambda name, url, mode, thumb, **kwargs: captured_dirs.append({
                            "name": name, "url": url, "mode": mode
                        }))

    josporn.List("https://josporn.club/latest-updates/")

    next_pages = [d for d in captured_dirs if d["name"] == "Next Page"]
    assert len(next_pages) == 1
    assert "/page/2/" in next_pages[0]["url"]
    assert next_pages[0]["mode"] == "List"
