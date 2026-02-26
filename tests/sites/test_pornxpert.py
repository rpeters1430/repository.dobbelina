import os
from resources.lib import utils
from resources.lib.sites import pornxpert

def test_pornxpert_list_parsing(monkeypatch):
    """Test that pornxpert list parsing correctly extracts videos."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "pornxpert_home.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

    captured_items = []
    monkeypatch.setattr(pornxpert.site, "add_download_link", 
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append({
                            "name": name, "url": url, "mode": mode, "thumb": thumb
                        }))
    
    pornxpert.List("https://www.pornxpert.com/latest-updates/")
    
    assert len(captured_items) > 0
    assert any("busty nurse" in item["name"].lower() for item in captured_items)
    assert all(item["mode"] == "Playvid" for item in captured_items)
    assert all("/video/" in item["url"] for item in captured_items)

def test_pornxpert_video_parsing(monkeypatch):
    """Test that pornxpert video parsing correctly extracts stream URL."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "pornxpert_video.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

    # Mock VideoPlayer
    class MockVP:
        def __init__(self, name, download):
            self.progress = type('obj', (object,), {'update': lambda self, p, m: None})()
            self.played_url = None
        def play_from_direct_link(self, url):
            self.played_url = url

    mock_vp_instance = [None]
    def mock_vp_init(name, download):
        mock_vp_instance[0] = MockVP(name, download)
        return mock_vp_instance[0]

    monkeypatch.setattr(utils, "VideoPlayer", mock_vp_init)
    
    pornxpert.Playvid("https://www.pornxpert.com/video/4921/busty-nurse/", "Busty Nurse")
    
    assert mock_vp_instance[0].played_url is not None
    assert ".mp4" in mock_vp_instance[0].played_url
    assert ".mp4/" not in mock_vp_instance[0].played_url
    assert "Referer=" in mock_vp_instance[0].played_url


def test_pornxpert_main_loads_latest(monkeypatch):
    """Test that main screen renders menu and latest list items."""
    captured_dirs = []
    list_calls = []

    monkeypatch.setattr(
        pornxpert.site,
        "add_dir",
        lambda name, url, mode, thumb, **kwargs: captured_dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornxpert, "List", lambda url, page=1: list_calls.append((url, page)))

    pornxpert.Main("https://www.pornxpert.com/")

    assert any(d["mode"] == "List" and "latest-updates" in d["url"] for d in captured_dirs)
    assert list_calls == [("https://www.pornxpert.com/latest-updates/", 1)]


def test_pornxpert_list_pagination(monkeypatch):
    """Test that pornxpert pagination uses .load-more link."""
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "sites", "pornxpert_home.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

    captured_items = []
    captured_dirs = []
    monkeypatch.setattr(pornxpert.site, "add_download_link",
                        lambda name, url, mode, thumb, label, **kwargs: captured_items.append(None))
    monkeypatch.setattr(pornxpert.site, "add_dir",
                        lambda name, url, mode, thumb, **kwargs: captured_dirs.append({
                            "name": name, "url": url, "mode": mode
                        }))

    pornxpert.List("https://www.pornxpert.com/latest-updates/")

    next_pages = [d for d in captured_dirs if d["name"] == "Next Page"]
    assert len(next_pages) == 1
    assert "/2/" in next_pages[0]["url"]
    assert next_pages[0]["mode"] == "List"


def test_pornxpert_categories_parsing(monkeypatch):
    """Test that pornxpert categories extracts a.item elements correctly."""
    html = """
    <html><body>
    <div class="list-categories">
        <div class="margin-fix" id="list_categories_categories_list_items">
            <a class="item" href="https://www.pornxpert.com/categories/french/" title="French">
                <div class="img"><span class="no-thumb">no image</span></div>
                <strong class="title">French</strong>
                <div class="wrap"><div class="videos">32 videos</div></div>
            </a>
            <a class="item" href="https://www.pornxpert.com/categories/webcams/" title="Webcams">
                <div class="img"><img class="thumb" src="https://www.pornxpert.com/thumb.jpg" alt="Webcams"></div>
                <strong class="title">Webcams</strong>
                <div class="wrap"><div class="videos">11 videos</div></div>
            </a>
            <a class="item" href="https://www.pornxpert.com/categories/german/" title="German">
                <div class="img"><span class="no-thumb">no image</span></div>
                <strong class="title">German</strong>
                <div class="wrap"><div class="videos">62 videos</div></div>
            </a>
        </div>
    </div>
    </body></html>
    """

    monkeypatch.setattr(utils, "getHtml", lambda url, **kwargs: html)

    captured_dirs = []
    monkeypatch.setattr(pornxpert.site, "add_dir",
                        lambda name, url, mode, thumb, **kwargs: captured_dirs.append({
                            "name": name, "url": url, "mode": mode, "thumb": thumb
                        }))

    pornxpert.Categories("https://www.pornxpert.com/categories/")

    assert len(captured_dirs) == 3
    assert captured_dirs[0]["name"] == "French"
    assert "/categories/french/" in captured_dirs[0]["url"]
    assert captured_dirs[1]["name"] == "Webcams"
    assert captured_dirs[1]["thumb"] == "https://www.pornxpert.com/thumb.jpg"
    assert captured_dirs[2]["name"] == "German"
    assert all(d["mode"] == "List" for d in captured_dirs)
