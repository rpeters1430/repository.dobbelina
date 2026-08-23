"""Comprehensive tests for pornyteen.com site implementation."""

from pathlib import Path
import importlib

pornyteen = importlib.import_module("resources.lib.sites.pornyteen")

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "pornyteen"


def load_fixture(name):
    """Load a fixture file from the pornyteen fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_site_metadata():
    """Verify site registration metadata."""
    assert pornyteen.site.category == "Video Tubes"
    assert pornyteen.site.url == "https://pornyteen.com/"
    assert pornyteen.site.name == "pornyteen"


def test_main_menu(monkeypatch):
    """Test Main menu entries."""
    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(pornyteen.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornyteen, "List", lambda url: None)
    monkeypatch.setattr(pornyteen.utils, "eod", lambda: None)

    pornyteen.Main()

    modes = [d["mode"] for d in dirs]
    assert "Search" in modes
    assert "Categories" in modes
    assert "Tags" in modes
    assert "List" in modes


def test_list_parses_video_items(monkeypatch):
    """Test that List correctly parses video items from fixture."""
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
            }
        )

    monkeypatch.setattr(pornyteen.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornyteen.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(pornyteen.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornyteen.utils, "eod", lambda: None)

    pornyteen.List("https://pornyteen.com/videos/")

    assert len(downloads) == 24
    first = downloads[0]
    assert first["mode"] == "Playvid"
    assert first["url"].startswith("https://pornyteen.com/video/")
    assert "PublicAgent" in first["name"]
    assert first["icon"].startswith("https://cdn.pornyteen.com/media/thumbs/")
    assert first["duration"] == "45:16"

    next_page_dirs = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_page_dirs) == 1
    assert "page2.html" in next_page_dirs[0]["url"]


def test_categories(monkeypatch):
    """Test that Categories parses category entries."""
    sample_cat_html = """
    <ul class="counter-list">
        <li class="counter-list__li">
            <a href="https://pornyteen.com/categories/amateur/" title="Amateur">
                <span>Amateur</span>
                <span class="counter">3687</span>
            </a>
        </li>
        <li class="counter-list__li">
            <a href="https://pornyteen.com/categories/lesbian/" title="Lesbian">
                <span>Lesbian</span>
                <span class="counter">1200</span>
            </a>
        </li>
    </ul>
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

    monkeypatch.setattr(pornyteen.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornyteen.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornyteen.utils, "eod", lambda: None)

    pornyteen.Categories("https://pornyteen.com/categories/")

    assert len(dirs) == 2
    assert "Amateur" in dirs[0]["name"]
    assert "3687" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://pornyteen.com/categories/amateur/"
    assert dirs[0]["mode"] == "List"


def test_tags(monkeypatch):
    """Test that Tags parses tag entries."""
    sample_tag_html = """
    <ul class="counter-list">
        <li class="counter-list__li">
            <a href="https://pornyteen.com/tags/hardcore/" title="Hardcore">
                <span>Hardcore</span>
                <span class="counter">500</span>
            </a>
        </li>
    </ul>
    """
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return sample_tag_html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(pornyteen.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornyteen.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(pornyteen.utils, "eod", lambda: None)

    pornyteen.Tags("https://pornyteen.com/tags/")

    assert len(dirs) == 1
    assert "Hardcore" in dirs[0]["name"]
    assert dirs[0]["url"] == "https://pornyteen.com/tags/hardcore/"


def test_search(monkeypatch):
    """Test Search builds appropriate query url."""
    called_with = []
    monkeypatch.setattr(pornyteen, "List", lambda url: called_with.append(url))

    pornyteen.Search("https://pornyteen.com/search/", keyword="teen amateur")

    assert called_with == ["https://pornyteen.com/search/teen-amateur/"]


def test_playvid_extracts_video_source(monkeypatch):
    """Test that Playvid extracts video source element."""
    video_html = load_fixture("video.html")
    played = []

    def fake_get_html(url, *args, **kwargs):
        return video_html

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            pass

        def play_from_direct_link(self, stream_url):
            played.append(stream_url)

        def play_from_site_link(self, url, ref):
            played.append(f"site:{url}")

    monkeypatch.setattr(pornyteen.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(pornyteen.utils, "VideoPlayer", FakeVideoPlayer)

    pornyteen.Playvid(
        "https://pornyteen.com/video/publicagent-compilation-best-of-public-agent-fucks-british-women-20154.html",
        "PublicAgent Compilation",
    )

    assert len(played) == 1
    assert "https://cdn.pornyteen.com/media/videos/" in played[0]
    assert ".mp4" in played[0]
    assert "User-Agent=" in played[0]
