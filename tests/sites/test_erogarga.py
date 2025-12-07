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
