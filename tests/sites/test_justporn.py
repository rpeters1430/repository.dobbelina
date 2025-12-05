import pytest

from resources.lib.sites import justporn
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc='', contextm=None, fanart=None, duration='', quality=''):
        self.downloads.append({
            'name': name,
            'url': url,
            'mode': justporn.site.get_full_mode(mode),
            'icon': iconimage,
            'duration': duration,
            'quality': quality,
        })

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append({'name': name, 'url': url, 'mode': justporn.site.get_full_mode(mode)})


@pytest.fixture
def recorder(monkeypatch):
    rec = _Recorder()
    monkeypatch.setattr(justporn.site, 'add_download_link', rec.add_download)
    monkeypatch.setattr(justporn.site, 'add_dir', rec.add_dir)
    monkeypatch.setattr(justporn.utils, 'eod', lambda *a, **k: None)
    return rec


@pytest.fixture
def quality_prompt(monkeypatch):
    original_settings = justporn.utils.addon._settings.copy()
    monkeypatch.setattr(justporn.utils.addon, '_settings', {**original_settings, 'qualityask': '1'})
    yield
    monkeypatch.setattr(justporn.utils.addon, '_settings', original_settings)


def test_listing_uses_soup_spec(monkeypatch, recorder):
    fixture_mapped_get_html(monkeypatch, justporn, {'page=1': 'sites/justporn/listing.html'})

    justporn.List('https://justporn.com/?page=1')

    assert len(recorder.downloads) == 3
    assert recorder.downloads[0]['name'] == 'Sample Video One'
    assert recorder.downloads[0]['duration'] == '10:25'
    assert recorder.downloads[0]['quality'] == 'HD'

    assert recorder.dirs == [
        {
            'name': '[COLOR hotpink]Next Page...[/COLOR] (2)',
            'url': 'https://justporn.com/?page=2',
            'mode': 'justporn.List',
        }
    ]


def test_search_delegates_to_listing(monkeypatch, recorder):
    fixture_mapped_get_html(monkeypatch, justporn, {
        'search-term': 'sites/justporn/search.html',
    })

    justporn.Search('https://justporn.com/search', keyword='search term')

    names = [item['name'] for item in recorder.downloads]
    durations = [item['duration'] for item in recorder.downloads]
    assert names == ['Search Hit One', 'Search Hit Two']
    assert durations == ['09:01', '07:59']
    assert recorder.dirs == [
        {
            'name': '[COLOR hotpink]Next Page...[/COLOR] (2)',
            'url': 'https://justporn.com/search/search-term/?page=2',
            'mode': 'justporn.List',
        }
    ]


def test_playvid_prefers_highest_available_quality(monkeypatch, quality_prompt):
    fixture_mapped_get_html(monkeypatch, justporn, {'/video/': 'sites/justporn/video.html'})

    played = {}

    class _DummyVideoPlayer:
        def __init__(self, name, download=None, **kwargs):
            self.progress = type('P', (), {'update': lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            played['url'] = url

    monkeypatch.setattr(justporn.utils, 'VideoPlayer', _DummyVideoPlayer)
    justporn.Playvid('https://justporn.com/video/9999/example', 'Example video')

    assert played['url'] == 'https://justporn.com/media/videos/vid-1080.mp4'
