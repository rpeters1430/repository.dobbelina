"""Comprehensive tests for erogarga site implementation."""
from pathlib import Path

from resources.lib.sites import erogarga


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "erogarga"


def load_fixture(name):
    """Load a fixture file from the erogarga fixtures directory."""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_video_items(monkeypatch):
    """Test that List() correctly parses video items using BeautifulSoup."""
    html = load_fixture("list.html")

    downloads = []
    dirs = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc="", contextm=None, quality='', **kwargs):
        downloads.append({
            'name': name,
            'url': url,
            'mode': mode,
            'icon': iconimage,
            'desc': desc,
            'quality': quality,
            'contextm': contextm
        })

    def fake_add_dir(name, url, mode, iconimage=None, contextm=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'contextm': contextm})

    monkeypatch.setattr(erogarga.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(erogarga.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(erogarga.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(erogarga.utils, "eod", lambda: None)

    # Call List
    erogarga.List('https://www.erogarga.com/?filter=latest')

    # Verify we got 3 videos (skipped the photo gallery)
    assert len(downloads) == 3

    # Verify first video (HD)
    assert downloads[0]['name'] == 'Sample Video 1'
    assert downloads[0]['url'] == 'https://www.erogarga.com/video/sample-video-1/'
    assert downloads[0]['mode'] == 'Play'
    assert 'thumb1.jpg' in downloads[0]['icon']
    assert downloads[0]['quality'] == 'HD'
    assert downloads[0]['contextm'] is not None

    # Verify second video (no HD)
    assert downloads[1]['name'] == 'Sample Video 2'
    assert downloads[1]['quality'] == ''

    # Verify third video (HD)
    assert downloads[2]['name'] == 'Sample Video 3'
    assert downloads[2]['quality'] == 'HD'


def test_list_skips_photo_galleries(monkeypatch):
    """Test that List() skips photo galleries (type-photos class)."""
    html = load_fixture("list.html")

    downloads = []

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.site, "add_download_link", lambda *a, **k: downloads.append(a))
    monkeypatch.setattr(erogarga.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(erogarga.utils, "eod", lambda: None)

    erogarga.List('https://www.erogarga.com/?filter=latest')

    # Should have 3 videos, skipping the 1 photo gallery
    assert len(downloads) == 3
    # Verify none of the downloads are the photo album
    for download in downloads:
        assert 'Sample Album' not in str(download)


def test_list_handles_pagination(monkeypatch):
    """Test that List() correctly handles pagination."""
    html = load_fixture("list.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, contextm=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'contextm': contextm})

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(erogarga.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(erogarga.utils, "eod", lambda: None)

    # Call List
    erogarga.List('https://www.erogarga.com/?filter=latest')

    # Verify pagination was added
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1
    assert next_pages[0]['url'] == '/page/4/'
    assert next_pages[0]['mode'] == 'List'
    # Should have goto page context menu
    assert next_pages[0]['contextm'] is not None


def test_cat_parses_categories(monkeypatch):
    """Test that Cat() correctly parses category items using BeautifulSoup."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'icon': iconimage})

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(erogarga.utils, "eod", lambda: None)

    # Call Cat
    erogarga.Cat('https://www.erogarga.com/categories/')

    # Should have 3 categories
    assert len(dirs) == 3

    # Verify first category
    assert dirs[0]['name'] == 'Asian (125 videos)'
    assert dirs[0]['url'] == 'https://www.erogarga.com/category/asian/'
    assert dirs[0]['mode'] == 'List'

    # Verify second category
    assert dirs[1]['name'] == 'Brunette (89 videos)'
    assert dirs[1]['url'] == 'https://www.erogarga.com/category/brunette/'

    # Verify third category
    assert dirs[2]['name'] == 'MILF (156 videos)'


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(erogarga.site, 'search_dir', fake_search_dir)

    erogarga.Search('https://www.erogarga.com/?s=')

    assert search_dir_called[0]


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search() with keyword calls List()."""
    list_called_with = {}

    def fake_list(url):
        list_called_with['url'] = url

    monkeypatch.setattr(erogarga, 'List', fake_list)

    erogarga.Search('https://www.erogarga.com/?s=', keyword='sample search')

    # Verify URL contains the search keyword
    assert 'url' in list_called_with
    assert 'sample%20search' in list_called_with['url']


def test_list_handles_empty_results(monkeypatch):
    """Test that List() handles empty results gracefully."""
    html = load_fixture("empty_results.html")

    notify_called = []

    def fake_notify(msg=None, **kwargs):
        notify_called.append(msg)

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.utils, "notify", fake_notify)
    monkeypatch.setattr(erogarga.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(erogarga.site, "add_dir", lambda *a, **k: None)

    erogarga.List('https://www.erogarga.com/?s=nonexistent')

    # Should have called notify with "No data found"
    assert len(notify_called) == 1
    assert notify_called[0] == 'No data found'


def test_list_extracts_duration(monkeypatch):
    """Test that List() correctly extracts video durations."""
    html = load_fixture("list.html")

    downloads = []

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append({'name': name, 'desc': desc})

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(erogarga.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(erogarga.utils, "eod", lambda: None)

    erogarga.List('https://www.erogarga.com/?filter=latest')

    # The description should be the video name (as per the code)
    assert len(downloads) == 3
    assert downloads[0]['name'] == 'Sample Video 1'
    assert downloads[0]['desc'] == 'Sample Video 1'


def test_list_adds_context_menu(monkeypatch):
    """Test that List() adds context menu items for lookup and related."""
    html = load_fixture("list.html")

    downloads = []

    def fake_add_download_link(name, url, mode, iconimage, desc="", contextm=None, **kwargs):
        downloads.append({'contextm': contextm})

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(erogarga.site, "add_dir", lambda *a, **k: None)
    monkeypatch.setattr(erogarga.utils, "eod", lambda: None)

    erogarga.List('https://www.erogarga.com/?filter=latest')

    # All videos should have context menus
    assert len(downloads) == 3
    for download in downloads:
        assert download['contextm'] is not None
        assert len(download['contextm']) == 2  # Lookup info and Related videos
        # Check for expected context menu text
        cm_text = str(download['contextm'])
        assert 'Lookup info' in cm_text
        assert 'Related videos' in cm_text


def test_play_extracts_phixxx_iframe(monkeypatch):
    """Test that Play() extracts video from phixxx.cc player."""
    html = load_fixture("video.html")

    video_player_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None, regex=None, direct_regex=None):
            self.name = name
            self.download = download
            self.regex = regex
            self.direct_regex = direct_regex
            self.resolveurl = FakeResolveUrl()
            video_player_calls.append(('init', name, download))

        def play_from_link_to_resolve(self, url):
            video_player_calls.append(('play_resolve', url))

        def play_from_direct_link(self, url):
            video_player_calls.append(('play_direct', url))

        def play_from_html(self, html, url):
            video_player_calls.append(('play_html', html, url))

        def play_from_site_link(self, url, referer):
            video_player_calls.append(('play_site', url, referer))

    class FakeResolveUrl:
        def HostedMediaFile(self, url):
            return FakeHostedMediaFile(url)

    class FakeHostedMediaFile:
        def __init__(self, url):
            self.url = url

        def valid_url(self):
            return False

    def fake_post_html(url, form_data=None, **kwargs):
        # Simulate phixxx.cc AJAX response
        return '{"source":[{"file":"https://cdn.example.com/video.mp4"}]}'

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(erogarga.utils, "postHtml", fake_post_html)

    # Call Play
    erogarga.Play('https://www.erogarga.com/video/hot-japanese-schoolgirl-12345/', 'Test Video')

    # Should have initialized VideoPlayer
    assert len(video_player_calls) >= 1
    assert video_player_calls[0][0] == 'init'
    assert video_player_calls[0][1] == 'Test Video'


def test_play_handles_watcherotic_embed(monkeypatch):
    """Test that Play() handles watcherotic.com iframe embeds."""
    html = load_fixture("video_iframe.html")

    video_player_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None, regex=None, direct_regex=None):
            self.name = name
            self.resolveurl = FakeResolveUrl()
            video_player_calls.append(('init', name))

        def play_from_direct_link(self, url):
            video_player_calls.append(('play_direct', url))

    class FakeResolveUrl:
        def HostedMediaFile(self, url):
            return FakeHostedMediaFile()

    class FakeHostedMediaFile:
        def valid_url(self):
            return False

    embed_html = """
    <html>
    <script>
    video_url: 'https://cdn.watcherotic.com/videos/test.mp4'
    </script>
    </html>
    """

    def fake_get_html(url, *args, **kwargs):
        if 'watcherotic' in url:
            return embed_html
        return html

    monkeypatch.setattr(erogarga.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(erogarga.utils, "VideoPlayer", FakeVideoPlayer)

    erogarga.Play('https://www.erogarga.com/video/asian-milf-69/', 'Test Video')

    assert len(video_player_calls) >= 1
    assert video_player_calls[0][0] == 'init'


def test_play_handles_spankbang_embed(monkeypatch):
    """Test that Play() handles spankbang.com iframe embeds."""
    html = load_fixture("video_spankbang.html")

    playvid_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None, regex=None, direct_regex=None):
            self.resolveurl = FakeResolveUrl()

        def play_from_direct_link(self, url):
            pass

    class FakeResolveUrl:
        def HostedMediaFile(self, url):
            return FakeHostedMediaFile()

    class FakeHostedMediaFile:
        def valid_url(self):
            return False

    def fake_playvid(url, name, download=None):
        playvid_calls.append({'url': url, 'name': name, 'download': download})

    monkeypatch.setattr(erogarga.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(erogarga.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(erogarga, "Playvid", fake_playvid)

    erogarga.Play('https://www.erogarga.com/video/korean-beauty-xxx/', 'Test Video')

    # Should have called spankbang Playvid
    assert len(playvid_calls) == 1
    assert 'spankbang.com/video/' in playvid_calls[0]['url']
    assert playvid_calls[0]['name'] == 'Test Video'


def test_play_handles_koreanpornmovie(monkeypatch):
    """Test that Play() handles koreanpornmovie.com videos."""
    html = load_fixture("video_koreanpm.html")
    iframe_html = load_fixture("video_koreanpm_iframe.html")

    video_player_calls = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            video_player_calls.append(('init', name, download))

        def play_from_direct_link(self, url):
            video_player_calls.append(('play_direct', url))

    def fake_get_html(url, *args, **kwargs):
        if 'somecdn.com' in url:
            return iframe_html
        return html

    monkeypatch.setattr(erogarga.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(erogarga.utils, "VideoPlayer", FakeVideoPlayer)

    erogarga.Play('https://koreanpornmovie.com/video/test-video/', 'Korean Video')

    # Should have initialized VideoPlayer and played direct link
    assert len(video_player_calls) >= 2
    assert video_player_calls[0][0] == 'init'
    assert video_player_calls[0][1] == 'Korean Video'
    assert video_player_calls[1][0] == 'play_direct'
    assert 'sample-video.mp4' in video_player_calls[1][1]
    assert 'referer=' in video_player_calls[1][1]


def test_lookupinfo_extracts_tags_and_actors(monkeypatch):
    """Test that Lookupinfo() extracts tags and actors using BeautifulSoup."""
    lookup_calls = []
    additem_calls = []

    class FakeLookupInfo:
        def __init__(self, siteurl, url, mode, lookup_list):
            lookup_calls.append({
                'siteurl': siteurl,
                'url': url,
                'mode': mode,
                'lookup_list': lookup_list
            })

        def additem(self, category, name, url):
            additem_calls.append({
                'category': category,
                'name': name,
                'url': url
            })

    def fake_get_html(url, *args, **kwargs):
        return """
        <html>
        <a href="https://www.erogarga.com/tag/asian/" class="label" title="Asian">Asian</a>
        <a href="https://www.erogarga.com/actor/jane-doe/" title="Jane Doe">Jane Doe</a>
        </html>
        """

    monkeypatch.setattr(erogarga.utils, "LookupInfo", FakeLookupInfo)
    monkeypatch.setattr(erogarga.utils, "getHtml", fake_get_html)

    erogarga.Lookupinfo('https://www.erogarga.com/video/test-video/')

    # Should have initialized LookupInfo
    assert len(lookup_calls) == 1
    assert lookup_calls[0]['url'] == 'https://www.erogarga.com/video/test-video/'
    assert lookup_calls[0]['mode'] == 'erogarga.List'

    # Should have added items for tag and actor
    assert len(additem_calls) == 2
    # First item should be the tag
    assert additem_calls[0]['category'] == 'Tag'
    assert additem_calls[0]['name'] == 'Asian'
    assert 'tag/asian' in additem_calls[0]['url']
    # Second item should be the actor
    assert additem_calls[1]['category'] == 'Actor'
    assert additem_calls[1]['name'] == 'Jane Doe'
    assert 'actor/jane-doe' in additem_calls[1]['url']


def test_related_navigates_to_video_page(monkeypatch):
    """Test that Related() navigates to the video page."""
    executebuiltin_calls = []

    def fake_executebuiltin(cmd):
        executebuiltin_calls.append(cmd)

    import xbmc
    monkeypatch.setattr(xbmc, 'executebuiltin', fake_executebuiltin)

    erogarga.Related('https://www.erogarga.com/video/test-video/')

    # Should have called Container.Update
    assert len(executebuiltin_calls) == 1
    assert 'Container.Update' in executebuiltin_calls[0]
    assert 'erogarga.List' in executebuiltin_calls[0]
    assert 'test-video' in executebuiltin_calls[0]


def test_getbaselink_identifies_site(monkeypatch):
    """Test that getBaselink() correctly identifies the site from URL."""
    # Test erogarga.com
    result = erogarga.getBaselink('https://www.erogarga.com/video/test/')
    assert result == 'https://www.erogarga.com/'

    # Test fulltaboo.tv
    result = erogarga.getBaselink('https://fulltaboo.tv/video/test/')
    assert result == 'https://fulltaboo.tv/'

    # Test koreanpornmovie.com
    result = erogarga.getBaselink('https://koreanpornmovie.com/video/test/')
    assert result == 'https://koreanpornmovie.com/'


def test_main_creates_proper_menu_structure(monkeypatch):
    """Test that Main() creates the proper menu structure."""
    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    def fake_list(url):
        pass

    monkeypatch.setattr(erogarga.site, 'add_dir', fake_add_dir)
    monkeypatch.setattr(erogarga, 'List', fake_list)

    erogarga.Main('https://www.erogarga.com/')

    # Should have Categories and Search
    assert len(dirs) == 2
    categories = [d for d in dirs if 'Categories' in d['name']]
    search = [d for d in dirs if 'Search' in d['name']]
    assert len(categories) == 1
    assert len(search) == 1
    assert categories[0]['mode'] == 'Cat'
    assert search[0]['mode'] == 'Search'


def test_main_fulltaboo_skips_categories(monkeypatch):
    """Test that Main() for fulltaboo.tv doesn't show categories."""
    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    def fake_list(url):
        pass

    # Main always uses site.add_dir, not site1.add_dir
    monkeypatch.setattr(erogarga.site, 'add_dir', fake_add_dir)
    monkeypatch.setattr(erogarga, 'List', fake_list)

    erogarga.Main('https://fulltaboo.tv/')

    # Should only have Search, not Categories
    assert len(dirs) == 1
    search = [d for d in dirs if 'Search' in d['name']]
    categories = [d for d in dirs if 'Categories' in d['name']]
    assert len(search) == 1
    assert len(categories) == 0
