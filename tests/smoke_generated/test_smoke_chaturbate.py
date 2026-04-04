"""Smoke tests for chaturbate site"""

import importlib
import inspect
import pytest
from resources.lib import utils
from resources.lib import basics
from resources.lib import url_dispatcher


@pytest.fixture(scope="module")
def site_module():
    """Get site module"""
    return importlib.import_module("resources.lib.sites.chaturbate")


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
    """Patch dispatcher helpers to capture items instead of calling Kodi"""
    def fake_add_dir(name, url, mode, iconimage=None, *args, **kwargs):
        page = args[0] if len(args) > 0 else kwargs.get('page')
        channel = args[1] if len(args) > 1 else kwargs.get('channel')
        section = args[2] if len(args) > 2 else kwargs.get('section')
        keyword = args[3] if len(args) > 3 else kwargs.get('keyword', '')
        captured_items.dirs.append({
            'name': str(name or ''),
            'url': str(url or ''),
            'mode': str(mode or ''),
            'icon': str(iconimage or ''),
            'page': page,
            'channel': channel,
            'section': section,
            'keyword': str(keyword or ''),
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

    monkeypatch.setattr(url_dispatcher, 'addDir', fake_add_dir)
    monkeypatch.setattr(url_dispatcher, 'addDownLink', fake_add_down)
    monkeypatch.setattr(basics, 'addDir', fake_add_dir)
    monkeypatch.setattr(basics, 'addDownLink', fake_add_down)
    if hasattr(utils, 'addDir'):
        monkeypatch.setattr(utils, 'addDir', fake_add_dir)
    if hasattr(utils, 'addDownLink'):
        monkeypatch.setattr(utils, 'addDownLink', fake_add_down)
    monkeypatch.setattr(utils, 'eod', lambda *args, **kwargs: None)


def _dispatch_mode(mode, params):
    from resources.lib.url_dispatcher import URL_Dispatcher
    if mode not in URL_Dispatcher.func_registry:
        return False

    try:
        URL_Dispatcher.dispatch(mode, params)
        return True
    except Exception:
        func = URL_Dispatcher.func_registry[mode]
        required = [
            name
            for name, parameter in inspect.signature(func).parameters.items()
            if parameter.default is inspect._empty
        ]
        fallback = dict(params)
        if "name" in required and "name" not in fallback:
            fallback["name"] = params.get("site_title") or params.get("site_name") or "Test"
        if "channel" in required and "channel" not in fallback:
            fallback["channel"] = 1
        if "section" in required and "section" not in fallback:
            fallback["section"] = 0
        if "page" in required and "page" not in fallback:
            fallback["page"] = 0
        if fallback == params:
            return False
        URL_Dispatcher.dispatch(mode, fallback)
        return True


def _dispatch_preferred_listing(site_object, captured_items):
    """Prefer the site's real default flow before falling back to direct List."""
    from resources.lib.url_dispatcher import URL_Dispatcher

    def _follow_list_mode(list_mode, initial_params, max_depth=2):
        pending = [dict(initial_params)]
        visited = set()
        depth = 0

        while pending and depth <= max_depth:
            params = pending.pop(0)
            visit_key = tuple(sorted((k, str(v)) for k, v in params.items()))
            if visit_key in visited:
                continue
            visited.add(visit_key)

            captured_items.reset()
            if not _dispatch_mode(list_mode, params):
                continue
            if captured_items.downloads:
                return True

            next_dirs = []
            for item in captured_items.dirs:
                if item.get("mode") != list_mode:
                    continue
                next_params = {
                    'url': item.get('url', site_object.url),
                    'site_name': site_object.name,
                    'site_title': getattr(site_object, 'title', site_object.name),
                }
                for key in ('page', 'channel', 'section', 'keyword'):
                    value = item.get(key)
                    if value not in (None, ''):
                        next_params[key] = value
                next_dirs.append(next_params)

            if next_dirs:
                pending.extend(next_dirs)
            depth += 1

        return False

    if site_object.default_mode:
        captured_items.reset()
        _dispatch_mode(
            site_object.default_mode,
            {
                'url': site_object.url,
                'site_name': site_object.name,
                'site_title': getattr(site_object, 'title', site_object.name),
            },
        )
        if captured_items.downloads:
            return True

    list_mode = None
    for mode in URL_Dispatcher.func_registry.keys():
        if mode.startswith("chaturbate.") and 'list' in mode.lower():
            list_mode = mode
            break

    if not list_mode:
        return False

    for item in captured_items.dirs:
        if item.get('mode') != list_mode:
            continue
        params = {
            'url': item.get('url', site_object.url),
            'site_name': site_object.name,
            'site_title': getattr(site_object, 'title', site_object.name),
        }
        for key in ('page', 'channel', 'section', 'keyword'):
            value = item.get(key)
            if value not in (None, ''):
                params[key] = value
        if _follow_list_mode(list_mode, params):
            return True

    return _follow_list_mode(
        list_mode,
        {
            'url': site_object.url,
            'site_name': site_object.name,
            'site_title': getattr(site_object, 'title', site_object.name),
        },
    )



class TestMain:
    """Test Main/default entry point"""

    def test_main_returns_items(self, site_object, captured_items, mock_gethtml):
        """Main should return at least one item"""
        captured_items.reset()

        if site_object.default_mode:
            _dispatch_mode(
                site_object.default_mode,
                {
                    'url': site_object.url,
                    'site_name': site_object.name,
                    'site_title': getattr(site_object, 'title', site_object.name),
                },
            )
        else:
            pytest.skip("Site has no default mode to dispatch")

        total_items = len(captured_items.dirs) + len(captured_items.downloads)
        assert total_items > 0, "Main should return at least one directory or video item"

    def test_main_items_have_required_fields(self, site_object, captured_items, mock_gethtml):
        """Main items should have name and mode"""
        captured_items.reset()

        if site_object.default_mode:
            _dispatch_mode(
                site_object.default_mode,
                {
                    'url': site_object.url,
                    'site_name': site_object.name,
                    'site_title': getattr(site_object, 'title', site_object.name),
                },
            )
        else:
            pytest.skip("Site has no default mode to dispatch")

        all_items = captured_items.dirs + captured_items.downloads
        for item in all_items:
            assert item['name'], f"Item missing name: {item}"
            assert item['mode'], f"Item missing mode: {item}"


# Note: chaturbate is a webcam/live site
# These sites typically cannot be fully tested without a real browser session
# and websocket connections. Smoke tests are limited to menu structure only.

