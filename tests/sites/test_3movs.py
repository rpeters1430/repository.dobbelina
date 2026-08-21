"""Comprehensive tests for 3movs.com site implementation."""

from pathlib import Path
import importlib

threemovs = importlib.import_module("resources.lib.sites.3movs")

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "3movs"


def load_fixture(name):
    """Load a fixture file from the 3movs fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items with BeautifulSoup."""
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "page": kwargs.get("page"),
            }
        )

    monkeypatch.setattr(threemovs.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(threemovs.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(threemovs.site, "add_dir", fake_add_dir)

    threemovs.List("https://www.3movs.com/videos/")

    assert len(downloads) > 0
    first = downloads[0]
    assert first["mode"] == "Playvid"
    assert first["url"].startswith("https://www.3movs.com/videos/")
    assert first["name"]
    assert first["icon"].startswith("http")

    next_page_dirs = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_page_dirs) == 1
    assert next_page_dirs[0]["page"] == 2


def test_categories(monkeypatch):
    """Test that Categories parses category entries."""
    sample_cat_html = """
    <div class="thumb_cat item">
        <a class="wrap_image" href="https://www.3movs.com/categories/amateur/" title="Amateur">
            <img class="img" src="https://img.3movs.com/cat/1.jpg" />
        </a>
        <a class="title" href="https://www.3movs.com/categories/amateur/" title="Amateur">Amateur</a>
        <span class="count">12,345</span>
    </div>
    """
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return sample_cat_html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
            }
        )

    monkeypatch.setattr(threemovs.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(threemovs.site, "add_dir", fake_add_dir)

    threemovs.Categories("https://www.3movs.com/categories/")

    assert len(dirs) == 1
    assert "Amateur" in dirs[0]["name"]
    assert "12,345" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://www.3movs.com/categories/amateur/"
    assert dirs[0]["icon"] == "https://img.3movs.com/cat/1.jpg"


def test_playvid_extracts_flashvars(monkeypatch):
    """Test that Playvid extracts video_url from KVS flashvars."""
    sample_video_html = """
    <script>
    var flashvars = {
        video_id: '459432',
        video_title: 'Sample Video',
        video_url: 'https://cdn.3movs.com/videos/459432.mp4',
        video_alt_url: 'https://cdn.3movs.com/videos/459432_lq.mp4'
    };
    </script>
    """
    played = []

    def fake_get_html(url, *args, **kwargs):
        return sample_video_html

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = self

        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

        def play_from_direct_link(self, stream_url):
            played.append(stream_url)

    monkeypatch.setattr(threemovs.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(threemovs.utils, "VideoPlayer", FakeVideoPlayer)

    threemovs.Playvid("https://www.3movs.com/videos/459432/sample/", "Sample Video")

    assert len(played) == 1
    assert "https://cdn.3movs.com/videos/459432.mp4" in played[0]
    assert "User-Agent=" in played[0]
