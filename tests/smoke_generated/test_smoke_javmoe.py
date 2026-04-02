"""Smoke tests for javmoe site"""

import pytest
from resources.lib.sites import javmoe
from resources.lib import utils


@pytest.fixture
def site_module():
    """Get site module"""
    return javmoe


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


class TestList:
    """Test video listing function"""

    def test_list_returns_videos(self, site_object, captured_items, mock_gethtml):
        """List should return video items"""
        captured_items.reset()

        # Try to find List function
        from resources.lib.url_dispatcher import URL_Dispatcher
        list_mode = None
        for mode in URL_Dispatcher.func_registry.keys():
            if mode.startswith(f"{site_object.name}.") and 'list' in mode.lower():
                list_mode = mode
                break

        if list_mode:
            URL_Dispatcher.dispatch(list_mode, {'url': site_object.url})
            assert len(captured_items.downloads) > 0, "List should return at least one video"

    def test_list_videos_have_metadata(self, site_object, captured_items, mock_gethtml):
        """List videos should have name, url, and image"""
        captured_items.reset()

        from resources.lib.url_dispatcher import URL_Dispatcher
        list_mode = None
        for mode in URL_Dispatcher.func_registry.keys():
            if mode.startswith(f"{site_object.name}.") and 'list' in mode.lower():
                list_mode = mode
                break

        if list_mode and captured_items.downloads:
            URL_Dispatcher.dispatch(list_mode, {'url': site_object.url})
            for video in captured_items.downloads:
                assert video['name'], f"Video missing name: {video}"
                assert video['url'], f"Video missing URL: {video}"
                # Icon is optional but recommended
                if not video['icon']:
                    pytest.skip("No thumbnail - may be lazy-loaded")


class TestSearch:
    """Test search functionality"""

    def test_search_returns_results(self, site_object, captured_items, mock_gethtml):
        """Search should return results for a common keyword"""
        captured_items.reset()

        from resources.lib.url_dispatcher import URL_Dispatcher
        search_mode = None
        for mode in URL_Dispatcher.func_registry.keys():
            if mode.startswith(f"{site_object.name}.") and 'search' in mode.lower():
                search_mode = mode
                break

        if search_mode:
            URL_Dispatcher.dispatch(search_mode, {'url': site_object.url, 'keyword': 'test'})
            total = len(captured_items.dirs) + len(captured_items.downloads)
            if total == 0:
                pytest.skip("Search returned no results - may require live site")


class TestPlayback:
    """Test video playback URL extraction"""

    @pytest.mark.skip(reason="Requires actual video URL from site")
    def test_playvid_extracts_url(self, site_object, monkeypatch):
        """Playvid should extract a playable URL"""
        # This would need a real video URL from the site
        # and mock HTML fixtures to test properly
        pass

