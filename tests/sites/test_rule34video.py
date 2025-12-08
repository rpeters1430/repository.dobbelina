"""Comprehensive tests for rule34video site implementation."""
from pathlib import Path
import re

from resources.lib.sites import rule34video


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "rule34video"


def load_fixture(name):
    """Load a fixture file from the rule34video fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List() correctly parses video items using BeautifulSoup."""
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    def fake_get_html(url, referer=None):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", duration='', quality='', **kwargs):
        downloads.append({
            'name': name,
            'url': url,
            'mode': mode,
            'icon': iconimage,
            'desc': desc,
            'duration': duration,
            'quality': quality
        })

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    monkeypatch.setattr(rule34video.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(rule34video.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)
    monkeypatch.setattr(rule34video.utils, "cleantext", lambda x: x)

    # Call List
    rule34video.List('https://rule34video.com/latest-updates/')

    # Verify we got 3 videos
    assert len(downloads) == 3

    # Verify first video (with HD)
    assert downloads[0]['name'] == 'Hentai Anime Episode 1'
    assert downloads[0]['url'] == 'https://rule34video.com/video/123/hentai-anime-episode-1/'
    assert downloads[0]['mode'] == 'Playvid'
    assert 'preview.jpg' in downloads[0]['icon']
    assert downloads[0]['duration'] == '12:34'
    assert ' [COLOR orange]HD[/COLOR]' in downloads[0]['quality']

    # Verify second video (no HD)
    assert downloads[1]['name'] == '3D Animation Loop'
    assert downloads[1]['url'] == 'https://rule34video.com/video/456/3d-animation-loop/'
    assert downloads[1]['duration'] == '5:42'
    assert downloads[1]['quality'] == ''

    # Verify third video (with HD)
    assert downloads[2]['name'] == 'SFM Compilation'
    assert downloads[2]['duration'] == '20:15'
    assert ' [COLOR orange]HD[/COLOR]' in downloads[2]['quality']


def test_list_handles_pagination(monkeypatch):
    """Test that List() correctly handles pagination."""
    html = load_fixture("list.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)
    monkeypatch.setattr(rule34video.utils, "cleantext", lambda x: x)

    # Call List
    rule34video.List('https://rule34video.com/latest-updates/')

    # Verify pagination was added
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1
    assert 'Currently in Page 1 of 120' in next_pages[0]['name']
    assert 'mode=async' in next_pages[0]['url']
    assert 'function=get_block' in next_pages[0]['url']
    assert 'block_id=list_videos_latest_videos_list' in next_pages[0]['url']
    assert 'from=2' in next_pages[0]['url']


def test_list_handles_empty_results(monkeypatch):
    """Test that List() handles empty HTML gracefully."""
    empty_html = '<html><body><div class="container"></div></body></html>'

    downloads = []

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(rule34video.site, "add_download_link", lambda *a, **k: downloads.append(a))
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)

    # Should not crash
    rule34video.List('https://rule34video.com/latest-updates/')

    # Should have no downloads
    assert len(downloads) == 0


def test_cats_parses_categories(monkeypatch):
    """Test that Cats() correctly parses category items."""
    html = load_fixture("categories.html")

    dirs = []
    time_called = [False]

    def fake_time():
        time_called[0] = True
        return 1234567890.123

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'icon': iconimage})

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)
    monkeypatch.setattr(rule34video.utils, "cleantext", lambda x: x)
    monkeypatch.setattr(rule34video.time, "time", fake_time)

    # Call Cats with URL that doesn't have query params
    rule34video.Cats('https://rule34video.com/categories/')

    # Should have added timestamp to URL
    assert time_called[0]

    # Should have 3 categories + 1 next page
    categories = [d for d in dirs if d['mode'] == 'List']
    assert len(categories) == 3

    # Verify first category
    assert categories[0]['name'] == 'Anime'
    assert categories[0]['url'] == 'https://rule34video.com/categories/anime/'
    assert '1.jpg' in categories[0]['icon']

    # Verify second category
    assert categories[1]['name'] == '3D'
    assert categories[1]['url'] == 'https://rule34video.com/categories/3d/'

    # Verify third category
    assert categories[2]['name'] == 'SFM'


def test_cats_handles_pagination(monkeypatch):
    """Test that Cats() correctly handles pagination."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)
    monkeypatch.setattr(rule34video.utils, "cleantext", lambda x: x)
    monkeypatch.setattr(rule34video.time, "time", lambda: 1234567890.123)

    # Call Cats
    rule34video.Cats('https://rule34video.com/categories/?mode=async&function=get_block&block_id=list_categories_categories_list&sort_by=title&_=1234567890123')

    # Verify pagination was added
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1
    assert 'Currently in Page 1 of 15' in next_pages[0]['name']
    assert 'from=2' in next_pages[0]['url']
    assert next_pages[0]['mode'] == 'Cats'


def test_tagmenu_parses_tag_sections(monkeypatch):
    """Test that TagMenu() correctly parses tag sections."""
    html = load_fixture("tags_menu.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, page=1, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'page': page})

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)
    monkeypatch.setattr(rule34video.time, "time", lambda: 1234567890.123)

    # Call TagMenu
    rule34video.TagMenu('https://rule34video.com/tags/')

    # Verify we got all 4 tag sections
    assert len(dirs) == 4

    # Verify tag section names
    tag_names = [d['name'] for d in dirs]
    assert 'Characters' in tag_names
    assert 'Series' in tag_names
    assert 'Artists' in tag_names
    assert 'General' in tag_names

    # Verify tag section URLs
    tag_dict = {d['name']: d for d in dirs}
    characters_tag = tag_dict['Characters']
    assert 'mode=async' in characters_tag['url']
    assert 'function=get_block' in characters_tag['url']
    assert 'block_id=list_tags_tags_list' in characters_tag['url']
    assert 'section=characters' in characters_tag['url']
    assert characters_tag['mode'] == 'Tag'
    assert characters_tag['page'] == 1


def test_tag_parses_tag_items(monkeypatch):
    """Test that Tag() correctly parses tag items using BeautifulSoup."""
    html = load_fixture("tags.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, page=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'page': page})

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)

    # Call Tag
    rule34video.Tag('https://rule34video.com/tags/?mode=async&function=get_block&block_id=list_tags_tags_list&section=characters&from=1', page=1)

    # Should have 4 tags (no next page since less than 120 items)
    assert len(dirs) == 4

    # Verify tag names - the BeautifulSoup parser gets the whole link text including the count
    tag_names = [d['name'] for d in dirs]

    # Check that tags were found (names may include whitespace from HTML structure)
    assert any('Overwatch' in name for name in tag_names), f"Overwatch not found in {tag_names}"
    assert any('D.Va' in name for name in tag_names), f"D.Va not found in {tag_names}"
    assert any('Mercy' in name for name in tag_names), f"Mercy not found in {tag_names}"
    assert any('Widowmaker' in name for name in tag_names), f"Widowmaker not found in {tag_names}"

    # All should include the video count
    for name in tag_names:
        assert '[COLOR orange]' in name, f"Expected color formatting in {name}"

    # Verify URLs
    overwatch_dir = [d for d in dirs if 'Overwatch' in d['name']][0]
    assert overwatch_dir['url'] == 'https://rule34video.com/tags/overwatch/'
    assert overwatch_dir['mode'] == 'List'


def test_tag_handles_pagination_with_120_items(monkeypatch):
    """Test that Tag() adds pagination when there are exactly 120 items."""
    # Create HTML with 120 items
    items_html = ''
    for i in range(120):
        items_html += f'''
        <div class="item">
            <a href="https://rule34video.com/tags/tag{i}/">
                Tag {i}
                <span>
                    <svg></svg>{i}
                </span>
            </a>
        </div>
        '''

    html = f'<html><body><div class="container">{items_html}</div></body></html>'

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, page=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'page': page})

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(rule34video.utils, "eod", lambda: None)

    # Call Tag with page 1
    rule34video.Tag('https://rule34video.com/tags/?from=1', page=1)

    # Should have 120 tags + 1 next page
    assert len(dirs) == 121

    # Verify next page
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1
    assert 'from=2' in next_pages[0]['url']
    assert next_pages[0]['mode'] == 'Tag'
    assert next_pages[0]['page'] == 2


def test_playvid_extracts_video_urls(monkeypatch):
    """Test that Playvid() correctly extracts video URLs."""
    html = load_fixture("video.html")

    play_called_with = {}
    quality_srcs = {}

    def fake_get_html(url, referer=None):
        return html

    def fake_prefquality(srcs, sort_by=None, reverse=False):
        quality_srcs['srcs'] = srcs
        # Return 1080p URL
        return srcs['1080p']

    def fake_get_video_link(url, referer):
        return url

    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('obj', (object,), {'update': lambda *a, **k: None, 'close': lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            play_called_with['url'] = url

    monkeypatch.setattr(rule34video.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(rule34video.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(rule34video.utils, "getVideoLink", fake_get_video_link)
    monkeypatch.setattr(rule34video.utils, "VideoPlayer", MockVideoPlayer)

    # Call Playvid
    rule34video.Playvid('https://rule34video.com/video/123/hentai-anime-episode-1/', 'Hentai Anime Episode 1')

    # Verify quality sources were extracted
    assert 'srcs' in quality_srcs
    assert '720p' in quality_srcs['srcs']
    assert '1080p' in quality_srcs['srcs']
    assert '4k' in quality_srcs['srcs']
    assert quality_srcs['srcs']['720p'] == 'https://cdn1.rule34video.com/videos/123/123.mp4'
    assert quality_srcs['srcs']['1080p'] == 'https://cdn2.rule34video.com/videos/123/123_1080.mp4'
    assert quality_srcs['srcs']['4k'] == 'https://cdn3.rule34video.com/videos/123/123_4k.mp4'

    # Verify video was played
    assert 'url' in play_called_with
    assert 'cdn2.rule34video.com' in play_called_with['url']
    assert 'User-Agent=iPad' in play_called_with['url']
    assert 'Referer=' in play_called_with['url']


def test_playvid_handles_kvs_encrypted_urls(monkeypatch):
    """Test that Playvid() decodes KVS encrypted URLs."""
    html = load_fixture("video_kvs.html")

    kvs_decode_called_with = {}
    play_called_with = {}

    def fake_get_html(url, referer=None):
        return html

    def fake_kvs_decode(url, license_code):
        kvs_decode_called_with['url'] = url
        kvs_decode_called_with['license_code'] = license_code
        # Return decrypted URL
        return 'https://cdn-decrypted.rule34video.com/videos/123/123_720.mp4'

    def fake_prefquality(srcs, sort_by=None, reverse=False):
        # Return 720p encrypted URL
        return srcs['720p']

    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('obj', (object,), {'update': lambda *a, **k: None, 'close': lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            play_called_with['url'] = url

    monkeypatch.setattr(rule34video.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(rule34video, "kvs_decode", fake_kvs_decode)
    monkeypatch.setattr(rule34video.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(rule34video.utils, "getVideoLink", lambda *a: a[0])
    monkeypatch.setattr(rule34video.utils, "VideoPlayer", MockVideoPlayer)

    # Call Playvid
    rule34video.Playvid('https://rule34video.com/video/123/encrypted-video/', 'Encrypted Video')

    # Verify KVS decoder was called
    assert 'url' in kvs_decode_called_with
    assert 'license_code' in kvs_decode_called_with
    assert kvs_decode_called_with['url'] == 'function/0/123/abcdef/'
    assert kvs_decode_called_with['license_code'] == 'xyz789abc456def'

    # Verify decrypted URL was played
    assert 'url' in play_called_with
    assert 'cdn-decrypted.rule34video.com' in play_called_with['url']


def test_playvid_handles_get_file_urls(monkeypatch):
    """Test that Playvid() handles get_file URLs."""
    html = '''
    <html>
    <script>
        var flashvars = {
            video_url: 'https://rule34video.com/get_file/123/abcdef/', video_url_text: '720p',
            license_code: 'test123'
        };
    </script>
    <body></body>
    </html>
    '''

    get_video_link_called_with = {}
    play_called_with = {}

    def fake_get_html(url, referer=None):
        return html

    def fake_get_video_link(url, referer):
        get_video_link_called_with['url'] = url
        get_video_link_called_with['referer'] = referer
        return 'https://cdn-direct.rule34video.com/videos/123/123.mp4'

    def fake_prefquality(srcs, sort_by=None, reverse=False):
        return srcs['720p']

    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('obj', (object,), {'update': lambda *a, **k: None, 'close': lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            play_called_with['url'] = url

    monkeypatch.setattr(rule34video.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(rule34video.utils, "getVideoLink", fake_get_video_link)
    monkeypatch.setattr(rule34video.utils, "prefquality", fake_prefquality)
    monkeypatch.setattr(rule34video.utils, "VideoPlayer", MockVideoPlayer)

    # Call Playvid
    rule34video.Playvid('https://rule34video.com/video/123/test/', 'Test Video')

    # Verify getVideoLink was called
    assert 'url' in get_video_link_called_with
    assert 'get_file' in get_video_link_called_with['url']
    assert get_video_link_called_with['referer'] == 'https://rule34video.com/'

    # Verify resolved URL was played
    assert 'url' in play_called_with
    assert 'cdn-direct.rule34video.com' in play_called_with['url']


def test_playvid_handles_no_video_sources(monkeypatch):
    """Test that Playvid() handles missing video sources gracefully."""
    html = '<html><body>No video here</body></html>'

    notify_called_with = {}

    def fake_notify(title, message):
        notify_called_with['title'] = title
        notify_called_with['message'] = message

    class MockVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('obj', (object,), {'update': lambda *a, **k: None, 'close': lambda *a, **k: None})()

    monkeypatch.setattr(rule34video.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(rule34video.utils, "notify", fake_notify)
    monkeypatch.setattr(rule34video.utils, "VideoPlayer", MockVideoPlayer)

    # Call Playvid
    result = rule34video.Playvid('https://rule34video.com/video/123/', 'Test')

    # Verify notify was called with error
    assert notify_called_with['title'] == 'Oh oh'
    assert notify_called_with['message'] == 'No video found'
    assert result is None


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(rule34video.site, 'search_dir', fake_search_dir)

    rule34video.Search('https://rule34video.com/search/')

    assert search_dir_called[0]


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search() with keyword calls List()."""
    list_called_with = {}

    def fake_list(url):
        list_called_with['url'] = url

    monkeypatch.setattr(rule34video, 'List', fake_list)

    rule34video.Search('https://rule34video.com/search/', keyword='overwatch dva')

    # Verify URL contains the search keyword
    assert 'url' in list_called_with
    assert 'overwatch-dva' in list_called_with['url']
    assert list_called_with['url'].endswith('/')
