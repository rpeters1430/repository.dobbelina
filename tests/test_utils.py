from resources.lib import utils
from tests.conftest import read_fixture


def test_parse_html_and_safe_get_attr_handles_fallbacks():
    soup = utils.parse_html(read_fixture('sample_listing.html'))
    anchors = soup.select('a.video-link')
    assert len(anchors) == 2

    first_img = anchors[0].select_one('img')
    # src attribute missing, should fall back to data-src
    thumbnail = utils.safe_get_attr(first_img, 'src', ['data-src'])
    assert thumbnail == '//cdn.example.com/thumb-alpha.jpg'

    second_img = anchors[1].select_one('img')
    # src attribute present, primary lookup should succeed
    assert utils.safe_get_attr(second_img, 'src', ['data-src']) == '//cdn.example.com/thumb-beta.jpg'


def test_safe_get_text_strips_whitespace():
    soup = utils.parse_html(read_fixture('sample_listing.html'))
    anchor = soup.select_one('a.video-link:last-of-type')
    assert utils.safe_get_text(anchor) == 'Beta Video'


def test_safe_get_helpers_return_defaults_when_missing():
    assert utils.safe_get_attr(None, 'href', ['data-href'], default='missing') == 'missing'
    assert utils.safe_get_text(None, default='missing') == 'missing'


def test_prefquality_selects_top_available_quality_with_aliases(monkeypatch):
    monkeypatch.setattr(utils.addon, '_settings', {**utils.addon._settings, 'qualityask': '1'})

    sources = {
        '4k': 'https://cdn.example.com/video-4k.mp4',
        '1080p60': 'https://cdn.example.com/video-1080p60.mp4',
        '720p': 'https://cdn.example.com/video-720p.mp4',
    }

    selected = utils.prefquality(sources)

    # With qualityask set to 1 (1080p threshold), prefquality caps selections
    # at the desired quality and picks the highest source that does not exceed
    # it (after normalizing aliases like 4k -> 2160 and 1080p60 -> 1080).
    assert selected == 'https://cdn.example.com/video-1080p60.mp4'


def test_prefquality_selects_2160p_when_quality_0(monkeypatch):
    monkeypatch.setattr(utils.addon, '_settings', {**utils.addon._settings, 'qualityask': '0'})

    sources = {
        '2160p': 'https://cdn.example.com/video-4k.mp4',
        '1080p': 'https://cdn.example.com/video-1080p.mp4',
        '720p': 'https://cdn.example.com/video-720p.mp4',
    }

    assert utils.prefquality(sources) == 'https://cdn.example.com/video-4k.mp4'


def test_prefquality_selects_720p_when_quality_2(monkeypatch):
    monkeypatch.setattr(utils.addon, '_settings', {**utils.addon._settings, 'qualityask': '2'})

    sources = {
        '2160p': 'https://cdn.example.com/video-4k.mp4',
        '1080p': 'https://cdn.example.com/video-1080p.mp4',
        '720p': 'https://cdn.example.com/video-720p.mp4',
        '480p': 'https://cdn.example.com/video-480p.mp4',
    }

    assert utils.prefquality(sources) == 'https://cdn.example.com/video-720p.mp4'


def test_prefquality_selects_576p_when_quality_3(monkeypatch):
    monkeypatch.setattr(utils.addon, '_settings', {**utils.addon._settings, 'qualityask': '3'})

    sources = {
        '1080p': 'https://cdn.example.com/video-1080p.mp4',
        '720p': 'https://cdn.example.com/video-720p.mp4',
        '576p': 'https://cdn.example.com/video-576p.mp4',
    }

    assert utils.prefquality(sources) == 'https://cdn.example.com/video-576p.mp4'


def test_prefquality_defers_to_selector_when_configured(monkeypatch):
    monkeypatch.setattr(utils.addon, '_settings', {**utils.addon._settings, 'qualityask': '4'})

    called = {}

    def fake_selector(prompt, items, sort_by=None, reverse=False):
        called['prompt'] = prompt
        called['sort_by'] = sort_by
        called['reverse'] = reverse
        return 'picked'

    monkeypatch.setattr(utils, 'selector', fake_selector)

    result = utils.prefquality({'360p': 'low', '720p': 'mid'}, sort_by=lambda k: k, reverse=True)

    assert result == 'picked'
    assert called['prompt'] == utils.i18n('pick_qual')
    assert called['reverse'] is True
    assert callable(called['sort_by'])
    assert called['sort_by']('key') == 'key'


def test_prefquality_falls_back_to_lowest_when_all_sources_exceed_limit(monkeypatch):
    monkeypatch.setattr(utils.addon, '_settings', {**utils.addon._settings, 'qualityask': '3'})

    sources = {
        '1080p': 'https://cdn.example.com/video-1080p.mp4',
        '720p': 'https://cdn.example.com/video-720p.mp4',
    }

    assert utils.prefquality(sources) == 'https://cdn.example.com/video-720p.mp4'
