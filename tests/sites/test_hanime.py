"""Comprehensive tests for hanime site implementation."""
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
        return sources.get('1080', sources.get('720', sources.get('480', None)))

    # Mock VideoPlayer
    mock_vp = MagicMock()
    mock_vp.progress.update = MagicMock()

    def fake_video_player(name, download=None):
        return mock_vp

    def fake_play_from_direct_link(url):
        play_called[0] = True
        assert url == 'https://hanime.tv/videos/1080p.mp4'

    mock_vp.play_from_direct_link = fake_play_from_direct_link

    monkeypatch.setattr(hanime.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(hanime.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(hanime.utils, "VideoPlayer", fake_video_player)

    # Call hanime_play
    hanime.hanime_play('sample-video-slug', 'Sample Video')

    # Verify sources were extracted
    assert len(sources_selected) == 3
    assert sources_selected['1080'] == 'https://hanime.tv/videos/1080p.mp4'
    assert sources_selected['720'] == 'https://hanime.tv/videos/720p.mp4'
    assert sources_selected['480'] == 'https://hanime.tv/videos/480p.mp4'

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

    monkeypatch.setattr(hanime.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(hanime.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(hanime.utils, "VideoPlayer", fake_video_player)

    # Should not crash
    hanime.hanime_play('sample-video-slug', 'Sample Video')

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
        downloads.append({
            'name': name,
            'url': url,
            'mode': mode,
            'icon': iconimage,
            'desc': desc
        })

    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    monkeypatch.setattr(hanime.utils, "postHtml", fake_post_html)
    monkeypatch.setattr(hanime.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hanime.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(hanime.utils, "eod", lambda: None)

    # Call hanime_list
    hanime.hanime_list('', '', 0)

    # Verify we got 1 video
    assert len(downloads) == 1
    assert 'Sample Hentai 1' in downloads[0]['name']
    assert 'Uncensored' in downloads[0]['name']  # Because is_censored is false
    assert downloads[0]['url'] == 'sample-1'
    assert downloads[0]['mode'] == 'hanime_play_combined'

    # Verify pagination was added (nbPages = 5, we're on page 0)
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1


def test_hanime_search_without_keyword_shows_dialog(monkeypatch):
    """Test that hanime_search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(hanime.site, 'search_dir', fake_search_dir)

    hanime.hanime_search('https://hanime.tv')

    assert search_dir_called[0]


def test_hanime_search_with_keyword_calls_list(monkeypatch):
    """Test that hanime_search() with keyword calls hanime_list()."""
    list_called_with = {}

    def fake_list(url, search, page):
        list_called_with['url'] = url
        list_called_with['search'] = search
        list_called_with['page'] = page

    monkeypatch.setattr(hanime, 'hanime_list', fake_list)

    hanime.hanime_search('https://hanime.tv', keyword='sample search')

    # Verify hanime_list was called with search keyword
    assert 'search' in list_called_with
    assert list_called_with['search'] == 'sample search'
    assert list_called_with['page'] == 0


def test_hanime_filter_creates_tag_filter(monkeypatch):
    """Test that hanime_filter() creates proper tag filter string."""
    list_called_with = {}

    # Create a mock dialog object
    class MockDialog:
        def multiselect(self, title, options):
            # Simulate user selecting indices 0 and 2 (3D and Anal from the tags list)
            return [0, 2]

    def fake_list(url, search, page):
        list_called_with['url'] = url
        list_called_with['search'] = search
        list_called_with['page'] = page

    # Replace utils.dialog with our mock
    monkeypatch.setattr(hanime.utils, 'dialog', MockDialog())
    monkeypatch.setattr(hanime, 'hanime_list', fake_list)

    hanime.hanime_filter()

    # Verify hanime_list was called with tag filter
    assert 'url' in list_called_with
    # Should be "3d|anal" (indices 0 and 2 from tags list, lowercased)
    assert list_called_with['url'] == '3d|anal'
    assert list_called_with['search'] == ''
    assert list_called_with['page'] == 0
