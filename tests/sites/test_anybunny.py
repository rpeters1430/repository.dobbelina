from resources.lib.sites import anybunny
from tests.conftest import fixture_mapped_get_html
class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc='', *args, **kwargs):
        self.downloads.append({
            'name': name,
            'url': url,
            'mode': anybunny.site.get_full_mode(mode),
            'icon': iconimage,
        })

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append({
            'name': name,
            'url': url,
            'mode': anybunny.site.get_full_mode(mode),
        })


def test_list_populates_download_links(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(monkeypatch, anybunny, {'new/?p=1': 'sites/anybunny/listing.html'})
    monkeypatch.setattr(anybunny.site, 'add_download_link', recorder.add_download)
    monkeypatch.setattr(anybunny.site, 'add_dir', recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, 'eod', lambda *args, **kwargs: None)

    anybunny.List('http://anybunny.org/new/?p=1')

    assert recorder.downloads == [
        {
            'name': 'First Video Title',
            'url': 'http://anybunny.org/videos/first-video',
            'mode': 'anybunny.Playvid',
            'icon': 'http://cdn.anybunny.org/thumb-first.jpg',
        },
        {
            'name': 'Second Video Title',
            'url': 'http://anybunny.org/videos/second-video',
            'mode': 'anybunny.Playvid',
            'icon': 'http://cdn.anybunny.org/thumb-second.jpg',
        },
    ]

    assert recorder.dirs == [
        {
            'name': 'Next Page',
            'url': 'http://anybunny.org/new/?p=2',
            'mode': 'anybunny.List',
        }
    ]


def test_search_results_have_no_pagination(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(monkeypatch, anybunny, {'search': 'sites/anybunny/search.html'})
    monkeypatch.setattr(anybunny.site, 'add_download_link', recorder.add_download)
    monkeypatch.setattr(anybunny.site, 'add_dir', recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, 'eod', lambda *args, **kwargs: None)

    anybunny.List('http://anybunny.org/search?q=query')

    assert [d['name'] for d in recorder.downloads] == ['Search Result One', 'Search Result Two']
    assert recorder.dirs == []


def test_playvid_uses_direct_regex(monkeypatch):
    captured = {}

    class _DummyVP:
        def __init__(self, name, download=False, direct_regex=None, **kwargs):
            captured['direct_regex'] = direct_regex
            self.progress = type('P', (), {'update': lambda *a, **k: None})()

        def play_from_site_link(self, url):
            captured['site_url'] = url

    monkeypatch.setattr(anybunny.utils, 'VideoPlayer', _DummyVP)

    anybunny.Playvid('http://anybunny.org/videos/video-123', 'Example')

    assert captured['site_url'] == 'http://anybunny.org/videos/video-123'
    assert captured['direct_regex'] == r"source src=\\'([^']+)\\'"
