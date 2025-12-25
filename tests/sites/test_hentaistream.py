"""Comprehensive tests for hentaistream site implementation."""

from pathlib import Path

from resources.lib.sites import hentaistream


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "hentaistream"


def load_fixture(name):
    """Load a fixture file from the hentaistream fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List() correctly parses video items using BeautifulSoup."""
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(
        name, url, mode, iconimage, desc="", fanart=None, quality="", **kwargs
    ):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "fanart": fanart,
                "quality": quality,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hentaistream.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hentaistream.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Call List
    hentaistream.List("https://hstream.moe/search?order=recently-uploaded&page=1")

    # Verify we got 3 videos
    assert len(downloads) == 3

    # Verify first video
    assert downloads[0]["name"] == "Sample Anime Episode 1"
    assert downloads[0]["url"] == "https://hstream.moe/hentai/sample-anime-1"
    assert downloads[0]["mode"] == "Playvid"
    assert "cover-ep-1" in downloads[0]["icon"]
    assert " [COLOR orange]4K[/COLOR]" in downloads[0]["quality"]

    # Verify second video
    assert downloads[1]["name"] == "Another Series Episode 2"
    assert downloads[1]["url"] == "https://hstream.moe/hentai/another-series-2"
    assert " [COLOR orange]FHD 48FPS[/COLOR]" in downloads[1]["quality"]

    # Verify third video
    assert downloads[2]["name"] == "Test Anime Episode 3"
    assert " [COLOR orange]HD[/COLOR]" in downloads[2]["quality"]


def test_list_handles_pagination(monkeypatch):
    """Test that List() correctly handles pagination with rel=next."""
    html = load_fixture("list.html")

    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hentaistream.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hentaistream.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Call List with page 1
    hentaistream.List("https://hstream.moe/search?order=recently-uploaded&page=1")

    # Verify pagination was added
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1
    assert "Next Page (2)" in next_pages[0]["name"]
    assert "page=2" in next_pages[0]["url"]


def test_list_handles_empty_results(monkeypatch):
    """Test that List() handles empty HTML gracefully."""
    empty_html = '<html><body><div class="container"></div></body></html>'

    downloads = []

    def fake_add_download_link(*args, **kwargs):
        downloads.append(args)

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(hentaistream.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Should not crash
    hentaistream.List("https://hstream.moe/search?order=recently-uploaded&page=1")

    # Should have no downloads
    assert len(downloads) == 0


def test_tags_parses_labels(monkeypatch):
    """Test that Tags() correctly parses tag labels using BeautifulSoup."""
    html = load_fixture("tags.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Call Tags
    hentaistream.Tags("https://hstream.moe/search?order=recently-uploaded&page=1")

    # Verify we got all 8 tags
    assert len(dirs) == 8

    # Verify tags are sorted alphabetically
    tag_names = [d["name"] for d in dirs]
    assert tag_names == sorted(tag_names)

    # Verify first tag (Ahegao)
    assert dirs[0]["name"] == "Ahegao"
    assert "tags[0]=ahegao" in dirs[0]["url"]
    assert dirs[0]["mode"] == "List"

    # Verify some other tags
    tag_dict = {d["name"]: d for d in dirs}
    assert "Big Boobs" in tag_dict
    assert "tags[0]=big-boobs" in tag_dict["Big Boobs"]["url"]
    assert "MILF" in tag_dict
    assert "Uncensored" in tag_dict


def test_tags_handles_empty_response(monkeypatch):
    """Test that Tags() handles empty HTML gracefully."""
    empty_html = "<html><body></body></html>"

    dirs = []

    def fake_add_dir(*args, **kwargs):
        dirs.append(args)

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(hentaistream.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)

    # Should not crash
    hentaistream.Tags("https://hstream.moe/search?order=recently-uploaded&page=1")

    # Should have no tags
    assert len(dirs) == 0


def test_playvid_extracts_episode_id(monkeypatch):
    """Test that Playvid() correctly extracts episode ID using BeautifulSoup."""
    html = load_fixture("playvid.html")

    post_called_with = {}

    def fake_get_html(url, referer=None):
        return html

    def fake_post_html(url, headers=None, json_data=None):
        post_called_with["json_data"] = json_data
        return '{"stream_domains": ["https://domain1.com"], "asia_stream_domains": [], "stream_url": "/path/to/video"}'

    class MockCookie:
        domain = "hstream.moe"
        name = "XSRF-TOKEN"
        value = "test-token"

    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type(
                "obj", (object,), {"update": lambda *a: None, "close": lambda: None}
            )()

        def play_from_direct_link(self, url):
            pass

    monkeypatch.setattr(hentaistream.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hentaistream.utils, "_postHtml", fake_post_html)
    monkeypatch.setattr(
        hentaistream.utils, "prefquality", lambda *a, **k: "/720/manifest.mpd"
    )
    monkeypatch.setattr(hentaistream.utils, "checkUrl", lambda *a: False)
    monkeypatch.setattr(hentaistream.utils, "VideoPlayer", MockVideoPlayer)
    monkeypatch.setattr(hentaistream.utils, "cj", [MockCookie()])

    # Call Playvid
    hentaistream.Playvid(
        "https://hstream.moe/hentai/sample-anime-1", "Sample Anime Episode 1"
    )

    # Verify that _postHtml was called with correct episode_id
    assert "json_data" in post_called_with
    assert post_called_with["json_data"]["episode_id"] == "abc123xyz789"


def test_playvid_handles_missing_episode_id(monkeypatch):
    """Test that Playvid() handles missing episode ID gracefully."""
    html_no_id = '<html><body><div class="player"></div></body></html>'

    notify_called_with = {}

    def fake_notify(title, message):
        notify_called_with["title"] = title
        notify_called_with["message"] = message

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: html_no_id)
    monkeypatch.setattr(hentaistream.utils, "notify", fake_notify)

    # Call Playvid
    result = hentaistream.Playvid("https://hstream.moe/hentai/sample", "Sample")

    # Verify notify was called with error
    assert notify_called_with["title"] == "Oh Oh"
    assert "No Videos found" in notify_called_with["message"]
    assert result is None


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(hentaistream.site, "search_dir", fake_search_dir)

    hentaistream.Search("https://hstream.moe/search?search=")

    assert search_dir_called[0]


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search() with keyword calls List()."""
    list_called_with = {}

    def fake_list(url, *args):
        list_called_with["url"] = url

    monkeypatch.setattr(hentaistream.utils, "getHtml", lambda *a, **k: "<html></html>")
    monkeypatch.setattr(hentaistream.utils, "eod", lambda: None)
    monkeypatch.setattr(hentaistream, "List", fake_list)

    hentaistream.Search("https://hstream.moe/search?search=", keyword="test anime")

    # Verify URL contains the search keyword
    assert "url" in list_called_with
    assert "test%20anime" in list_called_with["url"]
    assert "page=1" in list_called_with["url"]
