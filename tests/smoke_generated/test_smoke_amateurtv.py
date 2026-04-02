"""Smoke tests for amateurtv site"""

import pytest
from resources.lib.sites import amateurtv
from resources.lib import utils


@pytest.fixture
def site_module():
    """Get site module"""
    return amateurtv


@pytest.fixture
def site_object(site_module):
    """Get site AdultSite object"""
    return site_module.site


@pytest.fixture
def captured_items():
    """Fixture to capture addDir and addDownLink calls"""
    class ItemCapture:
        def __init__(self):
            self.dirs = []
            self.downloads = []

        def reset(self):
            self.dirs.clear()
            self.downloads.clear()

    return ItemCapture()


@pytest.fixture(autouse=True)
def patch_utils(monkeypatch, captured_items):
    """Patch utils to capture items instead of calling Kodi"""
    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        captured_items.dirs.append({
            'name': str(name or ''),
            'url': str(url or ''),
            'mode': str(mode or ''),
            'icon': str(iconimage or ''),
        })
        return True

    def fake_add_down(name, url, mode, iconimage, *args, **kwargs):
        desc = args[0] if args else kwargs.get('desc', '')
        captured_items.downloads.append({
            'name': str(name or ''),
            'url': str(url or ''),
            'mode': str(mode or ''),
            'icon': str(iconimage or ''),
            'desc': str(desc or ''),
        })
        return True

    monkeypatch.setattr(utils, 'addDir', fake_add_dir)
    monkeypatch.setattr(utils, 'addDownLink', fake_add_down)
    monkeypatch.setattr(utils, 'eod', lambda *args, **kwargs: None)



class TestMain:
    """Test Main/default entry point"""

    def test_main_returns_items(self, site_object, captured_items, mock_gethtml):
        """Main should return at least one item"""
        captured_items.reset()

        # Call the default mode
        from resources.lib.url_dispatcher import URL_Dispatcher
        if site_object.default_mode:
            URL_Dispatcher.dispatch(site_object.default_mode, {'url': site_object.url})

        total_items = len(captured_items.dirs) + len(captured_items.downloads)
        assert total_items > 0, "Main should return at least one directory or video item"

    def test_main_items_have_required_fields(self, site_object, captured_items, mock_gethtml):
        """Main items should have name and mode"""
        captured_items.reset()

        from resources.lib.url_dispatcher import URL_Dispatcher
        if site_object.default_mode:
            URL_Dispatcher.dispatch(site_object.default_mode, {'url': site_object.url})

        all_items = captured_items.dirs + captured_items.downloads
        for item in all_items:
            assert item['name'], f"Item missing name: {item}"
            assert item['mode'], f"Item missing mode: {item}"


# Note: amateurtv is a webcam/live site
# These sites typically cannot be fully tested without a real browser session
# and websocket connections. Smoke tests are limited to menu structure only.


# TODO: This site still uses regex parsing. Consider migrating to BeautifulSoup
# See MODERNIZATION.md and plugin.video.cumination/resources/lib/sites/pornhub.py for examples

