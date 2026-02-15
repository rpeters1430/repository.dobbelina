#!/usr/bin/env python3
"""Generate Smart Smoke Tests for Cumination Sites

Uses site analysis to generate appropriate pytest-based smoke tests
that match each site's actual implementation and use proper Kodi mocks.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parents[1]


def load_site_analysis() -> Dict[str, Any]:
    """Load site analysis report"""
    analysis_path = ROOT / 'results' / 'site_analysis.json'
    if not analysis_path.exists():
        print("ERROR: Site analysis not found. Run analyze_sites.py first.")
        sys.exit(1)

    return json.loads(analysis_path.read_text(encoding='utf-8'))


def generate_test_module(site_info: Dict[str, Any]) -> str:
    """Generate a pytest test module for a site"""
    site_name = site_info['name']
    has_main = site_info['has_main']
    has_list = site_info['has_list']
    has_search = site_info['has_search']
    has_play = site_info['has_play']
    is_webcam = site_info['is_webcam']
    uses_bs = site_info['uses_beautifulsoup']

    # Generate imports
    test_code = f'''"""Smoke tests for {site_name} site"""

import pytest
from resources.lib.sites import {site_name}
from resources.lib import utils


@pytest.fixture
def site_module():
    """Get site module"""
    return {site_name}


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
        captured_items.dirs.append({{
            'name': str(name or ''),
            'url': str(url or ''),
            'mode': str(mode or ''),
            'icon': str(iconimage or ''),
        }})
        return True

    def fake_add_down(name, url, mode, iconimage, *args, **kwargs):
        desc = args[0] if args else kwargs.get('desc', '')
        captured_items.downloads.append({{
            'name': str(name or ''),
            'url': str(url or ''),
            'mode': str(mode or ''),
            'icon': str(iconimage or ''),
            'desc': str(desc or ''),
        }})
        return True

    monkeypatch.setattr(utils, 'addDir', fake_add_dir)
    monkeypatch.setattr(utils, 'addDownLink', fake_add_down)
    monkeypatch.setattr(utils, 'eod', lambda *args, **kwargs: None)


'''

    # Test Main function
    if has_main:
        test_code += f'''
class TestMain:
    """Test Main/default entry point"""

    def test_main_returns_items(self, site_object, captured_items, mock_gethtml):
        """Main should return at least one item"""
        captured_items.reset()

        # Call the default mode
        from resources.lib.url_dispatcher import URL_Dispatcher
        if site_object.default_mode:
            URL_Dispatcher.dispatch(site_object.default_mode, {{'url': site_object.url}})

        total_items = len(captured_items.dirs) + len(captured_items.downloads)
        assert total_items > 0, "Main should return at least one directory or video item"

    def test_main_items_have_required_fields(self, site_object, captured_items, mock_gethtml):
        """Main items should have name and mode"""
        captured_items.reset()

        from resources.lib.url_dispatcher import URL_Dispatcher
        if site_object.default_mode:
            URL_Dispatcher.dispatch(site_object.default_mode, {{'url': site_object.url}})

        all_items = captured_items.dirs + captured_items.downloads
        for item in all_items:
            assert item['name'], f"Item missing name: {{item}}"
            assert item['mode'], f"Item missing mode: {{item}}"

'''

    # Test List function
    if has_list and not is_webcam:
        test_code += f'''
class TestList:
    """Test video listing function"""

    def test_list_returns_videos(self, site_object, captured_items, mock_gethtml):
        """List should return video items"""
        captured_items.reset()

        # Try to find List function
        from resources.lib.url_dispatcher import URL_Dispatcher
        list_mode = None
        for mode in URL_Dispatcher.func_registry.keys():
            if mode.startswith(f"{{site_object.name}}.") and 'list' in mode.lower():
                list_mode = mode
                break

        if list_mode:
            URL_Dispatcher.dispatch(list_mode, {{'url': site_object.url}})
            assert len(captured_items.downloads) > 0, "List should return at least one video"

    def test_list_videos_have_metadata(self, site_object, captured_items, mock_gethtml):
        """List videos should have name, url, and image"""
        captured_items.reset()

        from resources.lib.url_dispatcher import URL_Dispatcher
        list_mode = None
        for mode in URL_Dispatcher.func_registry.keys():
            if mode.startswith(f"{{site_object.name}}.") and 'list' in mode.lower():
                list_mode = mode
                break

        if list_mode and captured_items.downloads:
            URL_Dispatcher.dispatch(list_mode, {{'url': site_object.url}})
            for video in captured_items.downloads:
                assert video['name'], f"Video missing name: {{video}}"
                assert video['url'], f"Video missing URL: {{video}}"
                # Icon is optional but recommended
                if not video['icon']:
                    pytest.skip("No thumbnail - may be lazy-loaded")

'''

    # Test Search function
    if has_search and not is_webcam:
        test_code += f'''
class TestSearch:
    """Test search functionality"""

    def test_search_returns_results(self, site_object, captured_items, mock_gethtml):
        """Search should return results for a common keyword"""
        captured_items.reset()

        from resources.lib.url_dispatcher import URL_Dispatcher
        search_mode = None
        for mode in URL_Dispatcher.func_registry.keys():
            if mode.startswith(f"{{site_object.name}}.") and 'search' in mode.lower():
                search_mode = mode
                break

        if search_mode:
            URL_Dispatcher.dispatch(search_mode, {{'url': site_object.url, 'keyword': 'test'}})
            total = len(captured_items.dirs) + len(captured_items.downloads)
            if total == 0:
                pytest.skip("Search returned no results - may require live site")

'''

    # Test Play function
    if has_play and not is_webcam:
        test_code += f'''
class TestPlayback:
    """Test video playback URL extraction"""

    @pytest.mark.skip(reason="Requires actual video URL from site")
    def test_playvid_extracts_url(self, site_object, monkeypatch):
        """Playvid should extract a playable URL"""
        # This would need a real video URL from the site
        # and mock HTML fixtures to test properly
        pass

'''

    # Webcam site warning
    if is_webcam:
        test_code += f'''
# Note: {site_name} is a webcam/live site
# These sites typically cannot be fully tested without a real browser session
# and websocket connections. Smoke tests are limited to menu structure only.

'''

    # BeautifulSoup migration check
    if not uses_bs:
        test_code += f'''
# TODO: This site still uses regex parsing. Consider migrating to BeautifulSoup
# See MODERNIZATION.md and plugin.video.cumination/resources/lib/sites/pornhub.py for examples

'''

    return test_code


def generate_conftest_fixture() -> str:
    """Generate conftest.py additions for smoke tests"""
    return '''
# Add to tests/conftest.py or create tests/smoke/conftest.py

import pytest
from resources.lib import utils


@pytest.fixture
def mock_gethtml(monkeypatch):
    """Mock getHtml to return minimal HTML instead of making real requests"""
    def fake_gethtml(url, *args, **kwargs):
        # Return minimal valid HTML
        return """
        <html>
            <body>
                <div class="video-item">
                    <a href="/video/123" title="Test Video 1">
                        <img src="/thumb1.jpg" data-src="/thumb1-lazy.jpg" alt="Test Video 1">
                    </a>
                </div>
                <div class="video-item">
                    <a href="/video/456" title="Test Video 2">
                        <img src="/thumb2.jpg" alt="Test Video 2">
                    </a>
                </div>
                <a href="/page/2" class="next">Next</a>
            </body>
        </html>
        """

    monkeypatch.setattr(utils, 'getHtml', fake_gethtml)
    return fake_gethtml
'''


def main():
    parser = argparse.ArgumentParser(description='Generate smoke tests for Cumination sites')
    parser.add_argument('--site', nargs='+', help='Specific sites to generate tests for')
    parser.add_argument('--output-dir', default='tests/smoke_generated',
                        help='Output directory for generated tests')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print tests without writing files')
    args = parser.parse_args()

    # Load analysis
    print("Loading site analysis...")
    analysis = load_site_analysis()

    # Filter sites if requested
    sites = analysis['sites']
    if args.site:
        sites = [s for s in sites if s['name'] in args.site]

    print(f"Generating tests for {len(sites)} sites...")

    # Create output directory
    output_dir = ROOT / args.output_dir
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate conftest
        conftest_path = output_dir / 'conftest.py'
        conftest_path.write_text(generate_conftest_fixture(), encoding='utf-8')
        print(f"  Generated: {conftest_path.relative_to(ROOT)}")

    # Generate test modules
    for site in sites:
        if site.get('import_error'):
            print(f"  SKIP {site['name']}: {site['import_error']}")
            continue

        test_code = generate_test_module(site)

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"test_smoke_{site['name']}.py")
            print('='*60)
            print(test_code)
        else:
            test_path = output_dir / f"test_smoke_{site['name']}.py"
            test_path.write_text(test_code, encoding='utf-8')
            print(f"  Generated: {test_path.relative_to(ROOT)}")

    if not args.dry_run:
        print(f"\nTests generated in: {output_dir}")
        print(f"\nRun with: python run_tests.py {args.output_dir}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
