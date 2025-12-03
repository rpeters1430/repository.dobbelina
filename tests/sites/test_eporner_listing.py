from resources.lib.sites import eporner
from tests.conftest import read_fixture


def test_list_parses_video_items_and_next(monkeypatch):
    html = read_fixture('eporner/list.html')
    downloads = []
    dirs = []

    monkeypatch.setattr(eporner.utils, 'getHtml', lambda url, ref='': html)
    monkeypatch.setattr(eporner.utils, 'eod', lambda *args, **kwargs: None)

    def capture_download(name, url, mode, iconimage, desc='', **kwargs):
        downloads.append({
            'name': name,
            'url': url,
            'mode': eporner.site.get_full_mode(mode),
            'icon': iconimage,
            'duration': kwargs.get('duration'),
            'quality': kwargs.get('quality'),
        })

    def capture_dir(name, url, mode, iconimage=None, desc='', **kwargs):
        dirs.append({
            'name': name,
            'url': url,
            'mode': eporner.site.get_full_mode(mode),
        })

    monkeypatch.setattr(eporner.site, 'add_download_link', capture_download)
    monkeypatch.setattr(eporner.site, 'add_dir', capture_dir)

    eporner.List('https://www.eporner.com/recent/')

    assert downloads == [
        {
            'name': 'First Video',
            'url': 'https://www.eporner.com/video-abcd',
            'mode': 'eporner.Playvid',
            'icon': 'https://static.eporner-cdn.com/thumbs/abcd.jpg',
            'duration': '12:34',
            'quality': '1080p',
        },
        {
            'name': 'Second Clip',
            'url': 'https://cdn.eporner.com/video-efgh',
            'mode': 'eporner.Playvid',
            'icon': 'https://static.eporner-cdn.com/thumbs/efgh.jpg',
            'duration': '03:21',
            'quality': 'HD',
        },
    ]

    assert dirs == [
        {
            'name': 'Next Page (5)',
            'url': 'https://www.eporner.com/5/',
            'mode': 'eporner.List',
        }
    ]
