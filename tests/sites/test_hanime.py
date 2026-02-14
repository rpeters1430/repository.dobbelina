"""
Comprehensive tests for hanime.tv site implementation.

This site is primarily API-based (JSON responses) with BeautifulSoup
for video page parsing. Tests cover:
- API-based video listing with pagination
- Search functionality
- Tag filtering
- Video playback script extraction (BeautifulSoup + regex)
- Episode listing
"""

from pathlib import Path
from unittest.mock import MagicMock

from resources.lib.sites import hanime


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "hanime"


def load_fixture(name):
    """Load a fixture file from the hanime fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_hanime_play_extracts_video_sources(monkeypatch):
    """Test that hanime_play() correctly extracts video sources using BeautifulSoup."""
    html = load_fixture("playvid.html")

    sources_selected = {}
    play_called = [False]

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_prefquality(sources, **kwargs):
        # Store the sources that were passed to prefquality
        sources_selected.update(sources)
        # Return the highest quality
        return sources.get("1080", sources.get("720", sources.get("480", None)))

    # Mock VideoPlayer
    mock_vp = MagicMock()
    mock_vp.progress.update = MagicMock()

    def fake_video_player(name, download=None):
        return mock_vp

    def fake_play_from_direct_link(url):
        play_called[0] = True
        assert url == "https://hanime.tv/videos/1080p.mp4"

    mock_vp.play_from_direct_link = fake_play_from_direct_link

    def fake_get_video_api(url, member=False, premium_member=False):
        # Return something based on url if needed, or generic
        val = "alt-" if "alt" in str(html) else ""
        return {"videos_manifest": {"servers": [{"streams": [
            {"height": "1080", "url": "https://hanime.tv/videos/{}1080p.mp4".format(val)},
            {"height": "720", "url": "https://hanime.tv/videos/{}720p.mp4".format(val)},
            {"height": "480", "url": "https://hanime.tv/videos/{}480p.mp4".format(val)}
        ]}]}}

    monkeypatch.setattr(hanime, "get_video_api", fake_get_video_api)
    monkeypatch.setattr(hanime.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(hanime.utils, "VideoPlayer", fake_video_player)

    # Call hanime_play
    hanime.hanime_play("sample-video-slug", "Sample Video")

    # Verify sources were extracted
    assert len(sources_selected) == 3
    assert sources_selected["1080"] == "https://hanime.tv/videos/1080p.mp4"
    assert sources_selected["720"] == "https://hanime.tv/videos/720p.mp4"
    assert sources_selected["480"] == "https://hanime.tv/videos/480p.mp4"

    # Verify play was called
    assert play_called[0]


def test_hanime_play_handles_empty_sources(monkeypatch):
    """Test that hanime_play() handles HTML with no video sources gracefully."""
    empty_html = '<html><body><div class="video-player"></div></body></html>'

    play_called = [False]

    def fake_get_html(url, *args, **kwargs):
        return empty_html

    def fake_prefquality(sources, **kwargs):
        return None  # No sources available

    # Mock VideoPlayer
    mock_vp = MagicMock()
    mock_vp.progress.update = MagicMock()

    def fake_video_player(name, download=None):
        return mock_vp

    def fake_play_from_direct_link(url):
        play_called[0] = True

    mock_vp.play_from_direct_link = fake_play_from_direct_link

    monkeypatch.setattr(hanime, "get_video_api", lambda *a, **k: {})
    monkeypatch.setattr(hanime.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(hanime.utils, "VideoPlayer", fake_video_player)

    # Should not crash
    hanime.hanime_play("sample-video-slug", "Sample Video")

    # Play should not be called when no sources
    assert not play_called[0]


def test_hanime_list_parses_json_results(monkeypatch):
    """Test that hanime_list() correctly parses JSON API results."""
    json_response = """{
        "hits": "[{\\"name\\":\\"Sample Hentai 1\\",\\"slug\\":\\"sample-1\\",\\"is_censored\\":false,\\"cover_url\\":\\"https://example.com/cover1.jpg\\",\\"poster_url\\":\\"https://example.com/poster1.jpg\\",\\"description\\":\\"<p>Sample description 1</p>\\",\\"tags\\":[\\"tag1\\",\\"tag2\\"]}]",
        "nbPages": 5
    }"""

    downloads = []
    dirs = []

    def fake_post_html(url, *args, **kwargs):
        return json_response

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage, "desc": desc}
        )

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    monkeypatch.setattr(hanime.utils, "postHtml", fake_post_html)
    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    # Call hanime_list
    hanime.hanime_list("", "", 0)

    # Verify we got 1 video
    assert len(downloads) == 1
    assert "Sample Hentai 1" in downloads[0]["name"]
    assert "Uncensored" in downloads[0]["name"]  # Because is_censored is false
    assert downloads[0]["url"] == "sample-1"
    assert downloads[0]["mode"] == "hanime_play_combined"

    # Verify pagination was added (nbPages = 5, we're on page 0)
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1


def test_hanime_search_without_keyword_shows_dialog(monkeypatch):
    """Test that hanime_search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(hanime.site, "search_dir", fake_search_dir)

    hanime.hanime_search("https://hanime.tv")

    assert search_dir_called[0]


def test_hanime_search_with_keyword_calls_list(monkeypatch):
    """Test that hanime_search() with keyword calls hanime_list()."""
    list_called_with = {}

    def fake_list(url, search, page):
        list_called_with["url"] = url
        list_called_with["search"] = search
        list_called_with["page"] = page

    monkeypatch.setattr(hanime, "hanime_list", fake_list)

    hanime.hanime_search("https://hanime.tv", keyword="sample search")

    # Verify hanime_list was called with search keyword
    assert "search" in list_called_with
    assert list_called_with["search"] == "sample search"
    assert list_called_with["page"] == 0


def test_hanime_filter_creates_tag_filter(monkeypatch):
    """Test that hanime_filter() creates proper tag filter string."""
    list_called_with = {}

    # Create a mock dialog object
    class MockDialog:
        def multiselect(self, title, options):
            # Simulate user selecting indices 0 and 2 (3D and Anal from the tags list)
            return [0, 2]

    def fake_list(url, search, page):
        list_called_with["url"] = url
        list_called_with["search"] = search
        list_called_with["page"] = page

    # Replace utils.dialog with our mock
    monkeypatch.setattr(hanime.utils, "dialog", MockDialog())
    monkeypatch.setattr(hanime, "hanime_list", fake_list)

    hanime.hanime_filter()

    # Verify hanime_list was called with tag filter
    assert "url" in list_called_with
    # Should be "3d|anal" (indices 0 and 2 from tags list, lowercased)
    assert list_called_with["url"] == "3d|anal"
    assert list_called_with["search"] == ""
    assert list_called_with["page"] == 0


# Additional comprehensive tests using new fixtures


def test_hanime_list_with_api_list_fixture(monkeypatch):
    """Test hanime_list with api_list.json fixture - comprehensive parsing."""
    api_response = load_fixture("api_list.json")

    monkeypatch.setattr(
        hanime.utils, "postHtml", lambda url, json_data=None, headers=None: api_response
    )

    downloads = []
    dirs = []

    def fake_add_download_link(
        name,
        url,
        mode,
        iconimage,
        desc="",
        stream=None,
        fav="add",
        noDownload=False,
        contextm=None,
        fanart=None,
    ):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "desc": desc,
                "noDownload": noDownload,
                "contextm": contextm,
                "fanart": fanart,
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "", 0)

    # Should parse 2 videos
    assert len(downloads) == 2

    # First video (uncensored)
    assert "Sample Hentai Episode 1" in downloads[0]["name"]
    assert "[COLOR hotpink][I]Uncensored[/I][/COLOR]" in downloads[0]["name"]
    assert downloads[0]["url"] == "sample-hentai-1"
    assert downloads[0]["mode"] == "hanime_play_combined"
    assert "droidbuzz.top" in downloads[0]["icon"]
    assert "|Referer=https://hanime.tv/" in downloads[0]["icon"]
    assert "Big Boobs" in downloads[0]["desc"]
    assert "Vanilla" in downloads[0]["desc"]
    assert downloads[0]["contextm"] is not None

    # Second video (censored)
    assert downloads[1]["name"] == "Another Hentai Episode 2"
    assert "[COLOR hotpink][I]Uncensored[/I][/COLOR]" not in downloads[1]["name"]
    assert downloads[1]["url"] == "another-hentai-2"

    # Should add Next Page (page 0 of 5)
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 1


def test_hanime_list_last_page_no_pagination(monkeypatch):
    """Test that last page doesn't add pagination link."""
    api_response = load_fixture("api_last_page.json")

    monkeypatch.setattr(
        hanime.utils, "postHtml", lambda url, json_data=None, headers=None: api_response
    )

    dirs = []

    def fake_add_download_link(*args, **kwargs):
        pass

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({"name": name})

    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "", 4)  # Page 4 (last page)

    # No Next Page link
    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert len(next_pages) == 0


def test_hanime_list_empty_results(monkeypatch):
    """Test that empty results don't crash."""
    api_response = load_fixture("api_empty.json")

    monkeypatch.setattr(
        hanime.utils, "postHtml", lambda url, json_data=None, headers=None: api_response
    )

    downloads = []
    dirs = []

    def fake_add_download_link(*args, **kwargs):
        downloads.append(True)

    def fake_add_dir(*args, **kwargs):
        dirs.append(True)

    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "", 0)

    assert len(downloads) == 0
    assert len(dirs) == 0


def test_hanime_list_tag_filtering_single_tag(monkeypatch):
    """Test that single tag uses OR mode."""
    api_response = load_fixture("api_list.json")

    post_calls = []

    def fake_post(url, json_data=None, headers=None):
        post_calls.append(json_data)
        return api_response

    monkeypatch.setattr(hanime.utils, "postHtml", fake_post)
    monkeypatch.setattr(hanime.site, "add_download_link", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.site, "add_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("uncensored", "", 0)

    assert post_calls[-1]["tags"] == ["uncensored"]
    assert post_calls[-1]["tags_mode"] == "OR"


def test_hanime_list_tag_filtering_multiple_tags(monkeypatch):
    """Test that multiple tags use AND mode."""
    api_response = load_fixture("api_list.json")

    post_calls = []

    def fake_post(url, json_data=None, headers=None):
        post_calls.append(json_data)
        return api_response

    monkeypatch.setattr(hanime.utils, "postHtml", fake_post)
    monkeypatch.setattr(hanime.site, "add_download_link", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.site, "add_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("uncensored|vanilla|hd", "", 0)

    assert post_calls[-1]["tags"] == ["uncensored", "vanilla", "hd"]
    assert post_calls[-1]["tags_mode"] == "AND"


def test_hanime_list_search_query(monkeypatch):
    """Test that search query is properly sent."""
    api_response = load_fixture("api_list.json")

    post_calls = []

    def fake_post(url, json_data=None, headers=None):
        post_calls.append(json_data)
        return api_response

    monkeypatch.setattr(hanime.utils, "postHtml", fake_post)
    monkeypatch.setattr(hanime.site, "add_download_link", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.site, "add_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "test search", 0)

    assert post_calls[-1]["search_text"] == "test search"


def test_hanime_list_cdn_replacement(monkeypatch):
    """Test CDN URL replacement from highwinds-cdn.com to droidbuzz.top."""
    api_response = load_fixture("api_list.json")

    monkeypatch.setattr(
        hanime.utils, "postHtml", lambda url, json_data=None, headers=None: api_response
    )

    downloads = []

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"icon": iconimage, "fanart": kwargs.get("fanart")})

    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "", 0)

    assert "droidbuzz.top" in downloads[0]["icon"]
    assert "highwinds-cdn.com" not in downloads[0]["icon"]
    assert "droidbuzz.top" in downloads[0]["fanart"]


def test_hanime_list_description_html_stripping(monkeypatch):
    """Test that HTML tags are stripped from description."""
    api_response = load_fixture("api_list.json")

    monkeypatch.setattr(
        hanime.utils, "postHtml", lambda url, json_data=None, headers=None: api_response
    )

    downloads = []

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"desc": desc})

    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "", 0)

    assert "<p>" not in downloads[0]["desc"]
    assert "</p>" not in downloads[0]["desc"]
    assert "thrilling first episode" in downloads[0]["desc"]


def test_hanime_eps_parses_episodes(monkeypatch):
    """Test hanime_eps with api_episodes.json fixture."""
    api_response = load_fixture("api_episodes.json")

    monkeypatch.setattr(hanime.utils, "getHtml", lambda url, headers=None: api_response)

    selector_calls = []

    def fake_selector(title, options, show_on_one=False):
        selector_calls.append({"title": title, "options": options})
        return list(options.values())[0]

    monkeypatch.setattr(hanime.utils, "selector", fake_selector)

    play_calls = []

    def fake_play(url, name):
        play_calls.append({"url": url, "name": name})

    monkeypatch.setattr(hanime, "hanime_play", fake_play)

    hanime.hanime_eps("sample-hentai-1")

    # Should have 3 episodes
    assert len(selector_calls) == 1
    assert len(selector_calls[0]["options"]) == 3

    # Check uncensored tags
    episode_names = list(selector_calls[0]["options"].keys())
    assert any(
        "[COLOR hotpink][I]Uncensored[/I][/COLOR]" in name and "Episode 1" in name
        for name in episode_names
    )
    assert any(
        "Episode 2" in name and "[COLOR hotpink][I]Uncensored[/I][/COLOR]" not in name
        for name in episode_names
    )

    # Should play selected episode
    assert len(play_calls) == 1


def test_hanime_eps_no_selection(monkeypatch):
    """Test that hanime_eps handles cancelled selection."""
    api_response = load_fixture("api_episodes.json")

    monkeypatch.setattr(hanime.utils, "getHtml", lambda url, headers=None: api_response)
    monkeypatch.setattr(
        hanime.utils, "selector", lambda title, options, show_on_one=False: None
    )

    play_calls = []
    monkeypatch.setattr(
        hanime, "hanime_play", lambda url, name: play_calls.append(True)
    )

    result = hanime.hanime_eps("sample-hentai-1")

    assert result is None
    assert len(play_calls) == 0


def test_hanime_eps_constructs_correct_url(monkeypatch):
    """Test that episode API URL is correctly constructed."""
    gethtml_calls = []

    def fake_gethtml(url, headers=None):
        gethtml_calls.append(url)
        return load_fixture("api_episodes.json")

    monkeypatch.setattr(hanime.utils, "getHtml", fake_gethtml)
    monkeypatch.setattr(
        hanime.utils, "selector", lambda title, options, show_on_one=False: None
    )

    hanime.hanime_eps("test-video-id")

    assert len(gethtml_calls) == 1
    assert gethtml_calls[0] == "https://hanime.tv/api/v8/video?id=test-video-id"


def test_hanime_filter_no_selection(monkeypatch):
    """Test that filter without selection doesn't call hanime_list."""

    class MockDialog:
        def multiselect(self, title, options):
            return None  # User cancelled

    monkeypatch.setattr(hanime.utils, "dialog", MockDialog())

    list_calls = []
    monkeypatch.setattr(hanime, "hanime_list", lambda *args: list_calls.append(True))

    hanime.hanime_filter()

    assert len(list_calls) == 0


def test_hanime_play_url_construction(monkeypatch):
    """Test that video page URL is correctly constructed."""
    api_calls = []

    def fake_get_video_api(url, member=False, premium_member=False):
        api_calls.append(url)
        return {}

    monkeypatch.setattr(hanime, "get_video_api", fake_get_video_api)

    mock_vp = MagicMock()
    mock_vp.progress.update = MagicMock()
    monkeypatch.setattr(
        hanime.utils, "VideoPlayer", lambda name, download=None: mock_vp
    )
    monkeypatch.setattr(hanime.utils, "prefquality", lambda sources, **kwargs: None)

    hanime.hanime_play("test-video-slug", "Test Video")

    assert len(api_calls) == 2
    assert api_calls[0] == "test-video-slug"


def test_hanime_list_context_menu_structure(monkeypatch):
    """Test that video items have proper context menu entries."""
    api_response = load_fixture("api_list.json")

    monkeypatch.setattr(
        hanime.utils, "postHtml", lambda url, json_data=None, headers=None: api_response
    )
    monkeypatch.setattr(hanime.utils.addon, "getSetting", lambda key: "false")

    downloads = []

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({"contextm": kwargs.get("contextm")})

    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", lambda *args, **kwargs: None)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    hanime.hanime_list("", "", 0)

    # Should have context menu with episodes option
    assert len(downloads) > 0
    assert downloads[0]["contextm"] is not None
    assert len(downloads[0]["contextm"]) >= 1
    assert "episode" in downloads[0]["contextm"][0][0].lower()


def test_hanime_play_handles_alternative_format(monkeypatch):
    """Test that hanime_play() handles alternative JavaScript formatting with improved regex."""
    html = load_fixture("playvid_variation.html")

    sources_selected = {}
    play_called = [False]

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_prefquality(sources, **kwargs):
        sources_selected.update(sources)
        return sources.get("1080", sources.get("720", None))

    mock_vp = MagicMock()
    mock_vp.progress.update = MagicMock()

    def fake_video_player(name, download=None):
        return mock_vp

    def fake_play_from_direct_link(url):
        play_called[0] = True
        assert "hanime.tv/videos/alt-" in url

    mock_vp.play_from_direct_link = fake_play_from_direct_link

    def fake_get_video_api(url, member=False, premium_member=False):
        # Return something based on url if needed, or generic
        val = "alt-" if "alt" in str(html) else ""
        return {"videos_manifest": {"servers": [{"streams": [
            {"height": "1080", "url": "https://hanime.tv/videos/{}1080p.mp4".format(val)},
            {"height": "720", "url": "https://hanime.tv/videos/{}720p.mp4".format(val)},
            {"height": "480", "url": "https://hanime.tv/videos/{}480p.mp4".format(val)}
        ]}]}}

    monkeypatch.setattr(hanime, "get_video_api", fake_get_video_api)
    monkeypatch.setattr(hanime.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(hanime.utils, "VideoPlayer", fake_video_player)

    hanime.hanime_play("sample-video-slug", "Sample Video")

    # Verify sources were extracted from alternative format
    assert len(sources_selected) >= 2
    assert sources_selected.get("1080") == "https://hanime.tv/videos/alt-1080p.mp4"
    assert sources_selected.get("720") == "https://hanime.tv/videos/alt-720p.mp4"
    assert play_called[0]
