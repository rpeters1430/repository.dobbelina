"""Comprehensive tests for taboofantazy site implementation."""
from pathlib import Path

from resources.lib.sites import taboofantazy


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "taboofantazy"


def load_fixture(name):
    """Load a fixture file from the taboofantazy fixtures directory."""
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

    monkeypatch.setattr(taboofantazy.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(taboofantazy.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(taboofantazy.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Call List
    taboofantazy.List('https://www.taboofantazy.com/?filter=latest')

    # Verify we got 3 videos
    assert len(downloads) == 3

    # Verify first video
    assert downloads[0]['name'] == 'Stepmom Fantasy Episode 1'
    assert downloads[0]['url'] == 'https://www.taboofantazy.com/video/stepmom-fantasy-1/'
    assert downloads[0]['mode'] == 'Play'
    assert 'thumb1.jpg' in downloads[0]['icon']
    assert downloads[0]['quality'] == 'HD'
    assert downloads[0]['contextm'] is not None

    # Verify second video (no HD)
    assert downloads[1]['name'] == 'Family Secrets Part 2'
    assert downloads[1]['quality'] == ''

    # Verify third video (HD)
    assert downloads[2]['name'] == 'Forbidden Desire'
    assert downloads[2]['quality'] == 'HD'


def test_list_handles_pagination(monkeypatch):
    """Test that List() correctly handles pagination."""
    html = load_fixture("list.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, contextm=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'contextm': contextm})

    monkeypatch.setattr(taboofantazy.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(taboofantazy.site, "add_download_link", lambda *a, **k: None)
    monkeypatch.setattr(taboofantazy.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Call List
    taboofantazy.List('https://www.taboofantazy.com/?filter=latest')

    # Verify pagination was added
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1
    assert next_pages[0]['url'] == '/page/2'
    assert next_pages[0]['mode'] == 'List'
    # Should have goto page context menu
    assert next_pages[0]['contextm'] is not None


def test_list_handles_empty_results(monkeypatch):
    """Test that List() handles empty HTML gracefully."""
    empty_html = '<html><body><div class="videos"></div></body></html>'

    downloads = []

    monkeypatch.setattr(taboofantazy.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(taboofantazy.site, "add_download_link", lambda *a, **k: downloads.append(a))
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Should not crash
    taboofantazy.List('https://www.taboofantazy.com/?filter=latest')

    # Should have no downloads
    assert len(downloads) == 0


def test_cat_parses_categories(monkeypatch):
    """Test that Cat() correctly parses category items using BeautifulSoup."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode, 'icon': iconimage})

    monkeypatch.setattr(taboofantazy.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(taboofantazy.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Call Cat
    taboofantazy.Cat('https://www.taboofantazy.com/categories/')

    # Should have 3 categories + 1 next page
    categories = [d for d in dirs if d['mode'] == 'List']
    assert len(categories) == 3

    # Verify first category
    assert categories[0]['name'] == 'Stepmom'
    assert categories[0]['url'] == 'https://www.taboofantazy.com/category/stepmom/'
    assert 'stepmom.jpg' in categories[0]['icon']

    # Verify second category
    assert categories[1]['name'] == 'Stepsister'
    assert categories[1]['url'] == 'https://www.taboofantazy.com/category/stepsister/'

    # Verify third category
    assert categories[2]['name'] == 'Family'


def test_cat_handles_pagination(monkeypatch):
    """Test that Cat() correctly handles pagination."""
    html = load_fixture("categories.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    monkeypatch.setattr(taboofantazy.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(taboofantazy.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Call Cat
    taboofantazy.Cat('https://www.taboofantazy.com/categories/')

    # Verify pagination was added
    next_pages = [d for d in dirs if 'Next Page' in d['name']]
    assert len(next_pages) == 1
    assert next_pages[0]['url'] == '/categories/page/2/'
    assert next_pages[0]['mode'] == 'Cat'


def test_tags_parses_tag_links(monkeypatch):
    """Test that Tags() correctly parses tag links using BeautifulSoup."""
    html = load_fixture("tags.html")

    dirs = []

    def fake_add_dir(name, url, mode, iconimage=None, **kwargs):
        dirs.append({'name': name, 'url': url, 'mode': mode})

    monkeypatch.setattr(taboofantazy.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(taboofantazy.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Call Tags
    taboofantazy.Tags('https://www.taboofantazy.com/tags/')

    # Verify we got all 5 tags
    assert len(dirs) == 5

    # Verify tag names include counts
    tag_names = [d['name'] for d in dirs]
    assert 'MILF (125 videos)' in tag_names
    assert 'Teen (89 videos)' in tag_names
    assert 'Brunette (156 videos)' in tag_names
    assert 'Blonde (142 videos)' in tag_names
    assert 'Taboo (203 videos)' in tag_names

    # Verify URLs are properly formatted
    tag_dict = {d['name']: d for d in dirs}
    milf_tag = tag_dict['MILF (125 videos)']
    assert milf_tag['url'] == 'https://www.taboofantazy.com/tag/milf/'
    assert milf_tag['mode'] == 'List'


def test_tags_handles_empty_response(monkeypatch):
    """Test that Tags() handles empty HTML gracefully."""
    empty_html = '<html><body></body></html>'

    dirs = []

    monkeypatch.setattr(taboofantazy.utils, "getHtml", lambda *a, **k: empty_html)
    monkeypatch.setattr(taboofantazy.site, "add_dir", lambda *a, **k: dirs.append(a))
    monkeypatch.setattr(taboofantazy.utils, "eod", lambda: None)

    # Should not crash
    taboofantazy.Tags('https://www.taboofantazy.com/tags/')

    # Should have no tags
    assert len(dirs) == 0


def test_search_without_keyword_shows_dialog(monkeypatch):
    """Test that Search() without keyword shows search dialog."""
    search_dir_called = [False]

    def fake_search_dir(*args):
        search_dir_called[0] = True

    monkeypatch.setattr(taboofantazy.site, 'search_dir', fake_search_dir)

    taboofantazy.Search('https://www.taboofantazy.com/?s=')

    assert search_dir_called[0]


def test_search_with_keyword_calls_list(monkeypatch):
    """Test that Search() with keyword calls List()."""
    list_called_with = {}

    def fake_list(url):
        list_called_with['url'] = url

    monkeypatch.setattr(taboofantazy, 'List', fake_list)

    taboofantazy.Search('https://www.taboofantazy.com/?s=', keyword='stepmom fantasy')

    # Verify URL contains the search keyword
    assert 'url' in list_called_with
    assert 'stepmom%20fantasy' in list_called_with['url']
