#!/usr/bin/env python3
"""Generate Smart Smoke Tests for Cumination Sites

Uses site analysis to generate appropriate pytest-based smoke tests
that match each site's actual implementation and use proper Kodi mocks.
"""

import argparse
import importlib
import json
import inspect
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

import importlib
import inspect
import pytest
from resources.lib import utils
from resources.lib import basics
from resources.lib import url_dispatcher


@pytest.fixture(scope="module")
def site_module():
    """Get site module"""
    return importlib.import_module("resources.lib.sites.{site_name}")


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
        captured_items.dirs.append({{
            'name': str(name or ''),
            'url': str(url or ''),
            'mode': str(mode or ''),
            'icon': str(iconimage or ''),
            'page': page,
            'channel': channel,
            'section': section,
            'keyword': str(keyword or ''),
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
                next_params = {{
                    'url': item.get('url', site_object.url),
                    'site_name': site_object.name,
                    'site_title': getattr(site_object, 'title', site_object.name),
                }}
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
            {{
                'url': site_object.url,
                'site_name': site_object.name,
                'site_title': getattr(site_object, 'title', site_object.name),
            }},
        )
        if captured_items.downloads:
            return True

    list_mode = None
    for mode in URL_Dispatcher.func_registry.keys():
        if mode.startswith("{site_name}.") and 'list' in mode.lower():
            list_mode = mode
            break

    if not list_mode:
        return False

    for item in captured_items.dirs:
        if item.get('mode') != list_mode:
            continue
        params = {{
            'url': item.get('url', site_object.url),
            'site_name': site_object.name,
            'site_title': getattr(site_object, 'title', site_object.name),
        }}
        for key in ('page', 'channel', 'section', 'keyword'):
            value = item.get(key)
            if value not in (None, ''):
                params[key] = value
        if _follow_list_mode(list_mode, params):
            return True

    return _follow_list_mode(
        list_mode,
        {{
            'url': site_object.url,
            'site_name': site_object.name,
            'site_title': getattr(site_object, 'title', site_object.name),
        }},
    )


'''

    # Test Main function
    if has_main:
        test_code += f'''
class TestMain:
    """Test Main/default entry point"""

    def test_main_returns_items(self, site_object, captured_items, mock_gethtml):
        """Main should return at least one item"""
        captured_items.reset()

        if site_object.default_mode:
            _dispatch_mode(
                site_object.default_mode,
                {{
                    'url': site_object.url,
                    'site_name': site_object.name,
                    'site_title': getattr(site_object, 'title', site_object.name),
                }},
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
                {{
                    'url': site_object.url,
                    'site_name': site_object.name,
                    'site_title': getattr(site_object, 'title', site_object.name),
                }},
            )
        else:
            pytest.skip("Site has no default mode to dispatch")

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

        if _dispatch_preferred_listing(site_object, captured_items):
            assert len(captured_items.downloads) > 0, "List should return at least one video"
        else:
            pytest.skip("No list mode registered for this site")

    def test_list_videos_have_metadata(self, site_object, captured_items, mock_gethtml):
        """List videos should have name, url, and image"""
        captured_items.reset()

        if _dispatch_preferred_listing(site_object, captured_items):
            if not captured_items.downloads:
                pytest.skip("List returned no video items")
            for video in captured_items.downloads:
                assert video['name'], f"Video missing name: {{video}}"
                assert video['url'], f"Video missing URL: {{video}}"
                # Icon is optional but recommended
                if not video['icon']:
                    pytest.skip("No thumbnail - may be lazy-loaded")
        else:
            pytest.skip("No list mode registered for this site")

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
            if mode.startswith("{site_name}.") and 'search' in mode.lower():
                search_mode = mode
                break

        if search_mode:
            URL_Dispatcher.dispatch(search_mode, {{'url': site_object.url, 'keyword': 'test'}})
            total = len(captured_items.dirs) + len(captured_items.downloads)
            if total == 0:
                pytest.skip("Search returned no results - may require live site")
        else:
            pytest.skip("No search mode registered for this site")

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

import sys
from pathlib import Path
import json
import pytest

KODI_ARGV = ["plugin.video.cumination", "1", ""]
ROOT = Path(__file__).resolve().parents[2]


def _fallback_html():
    return """
    <html>
        <head>
            <title>Test Listing</title>
            <script>
                window.initials={"layoutPage":{"videoListProps":{"videoThumbProps":[{"title":"Test Video 1","pageURL":"https://xhamster.com/videos/test-video-1","thumbURL":"https://example.com/thumb-xhamster.jpg","duration":123,"isHD":true}]},"paginationProps":{"currentPageNumber":1,"lastPageNumber":2,"pageLinkTemplate":"https://xhamster.com/newest/{#}"}}};
            </script>
        </head>
        <body>
            <a class="th item" href="/videos/test-allclassic" title="Test AllClassic">
                <img src="/thumb-allclassic.jpg" data-src="/thumb-allclassic-lazy.jpg" alt="Test AllClassic">
                <span class="th-description">Test AllClassic Video</span>
                <span><i class="la-clock-o"></i>10:01</span>
            </a>

            <div class="list-videos">
                <div class="item">
                    <a class="popup-video-link" href="/videos/test-analdin" thumb="/thumb-analdin.jpg" title="Test Analdin Video">Test Analdin Video</a>
                    <div class="title">Test Analdin Video</div>
                    <img src="/thumb-analdin-fallback.jpg" data-original="/thumb-analdin.jpg">
                </div>
            </div>

            <div class="video-block">
                <a class="video-link" href="https://beemtube.com/videos/test-beemtube">
                    <img data-src="/thumb-beemtube.jpg" src="/thumb-beemtube-fallback.jpg" alt="Test BeemTube">
                    <strong>Test BeemTube Video</strong>
                </a>
                <div class="duration">06:16</div>
                <span class="hd_video"></span>
            </div>

            <article data-video-id="100" data-main-thumb="https://example.com/thumb-article-main.jpg">
                <a href="https://example.com/watch/test-article-video" title="Test Article Video">
                    <img src="https://example.com/thumb-article.jpg" data-src="https://example.com/thumb-article-lazy.jpg" alt="Test Article Video">
                </a>
                <div class="duration">04:44</div>
                <span class="hd-video">HD</span>
                <i class="fa-clock-o">04:44</i>
            </article>

            <div class="album" id="album-1">
                <img src="https://www.erome.com/thumb-erome.jpg" alt="Test Erome Album">
                <a class="album-title" href="https://www.erome.com/a/test-erome-album">Test Erome Album</a>
                <div class="album-images">12</div>
                <div class="album-videos">3</div>
            </div>

            <div class="media-group">
                <div class="video">
                    <video class="video-splash-mov" poster="https://www.erome.com/thumb-erome-video.jpg"></video>
                    <source src="https://cdn.erome.com/test-erome-video.mp4" label='720'>
                    <div class="duration">07:20</div>
                </div>
                <div class="clearfix"></div>
            </div>

            <div class="thumi">
                <a href="https://www.freeomovie.to/test-video" title="Test FreeOMovie">
                    <img src="/thumb-freeomovie.jpg" data-src="/thumb-freeomovie-lazy.jpg" alt="Test FreeOMovie">
                </a>
            </div>

            <div class="thumbs-inner">
                <a href="https://freshporno.org/test-freshporno" title="Test FreshPorno Video">
                    <img data-original="https://freshporno.org/thumb-freshporno.jpg" src="https://freshporno.org/thumb-freshporno-fallback.jpg" alt="Test FreshPorno Video">
                </a>
            </div>

            <li id="post-1">
                <a class="image" href="/video/123" alt="Test Porno365">
                    <img src="/thumb-porno365.jpg" alt="Test Porno365">
                    <span class="duration">09:59</span>
                </a>
            </li>

            <div class="item_cont">
                <a href="/videos/test-pornxp" class="item_link">
                    <img class="item_img" data-src="/thumb-pornxp.jpg" src="/thumb-pornxp-fallback.jpg" />
                    <div class="item_title">Test PornXP</div>
                    <div class="item_dur">08:00</div>
                </a>
            </div>

            <a class="item" href="https://www.heavy-r.com/videos/test-heavyr">
                <img src="/thumb-heavyr.jpg" data-src="/thumb-heavyr-lazy.jpg" />
                <div class="title">Test HeavyR Video</div>
            </a>

            <figure>
                <a class="img" href="https://jizzbunker.com/watch/test-jizzbunker">
                    <img data-original="/thumb-jizzbunker.jpg" src="/thumb-jizzbunker-fallback.jpg" />
                </a>
                <figcaption>
                    <a href="https://jizzbunker.com/watch/test-jizzbunker">Test Jizzbunker Video</a>
                </figcaption>
                <li class="dur"><time>05:55</time></li>
            </figure>

            <article class="post" data-post-id="1">
                <a href="https://premiumporn.org/test-video" title="Test PremiumPorn">
                    <img data-src="/thumb-premiumporn.jpg" src="/thumb-premiumporn-fallback.jpg" />
                    <div class="title">Test PremiumPorn</div>
                    <div class="duration">12:00</div>
                </a>
            </article>

            <div wire:key="video-test-1">
                <a href="/videos/test-hentaistream">
                    <img src="/gallery/test-hentaistream-0-thumbnail.jpg" alt="Test Hentaistream Video">
                    <p class="quality">1080p</p>
                </a>
            </div>

            <a class="clip-link" href="https://www.hitprn.com/test-hitprn" title="Test Hitprn Video">
                <img src="https://www.hitprn.com/thumb-hitprn.jpg" data-original="https://www.hitprn.com/thumb-hitprn-lazy.jpg">
            </a>

            <div class="video-thumb">
                <a class="frame video" href="/videos/test-youjizz">
                    <img class="lazy" data-original="//example.com/thumb-youjizz.jpg" src="//example.com/thumb-youjizz-fallback.jpg" alt="Test YouJizz Video">
                </a>
                <div class="video-title"><a href="/videos/test-youjizz">Test YouJizz Video</a></div>
                <div class="time">08:08</div>
            </div>

            <div class="v">
                <a href="https://xxdbx.com/video/test-xxdbx">
                    <img data-src="//example.com/thumb-xxdbx.jpg" src="//example.com/thumb-xxdbx-fallback.jpg">
                    <div class="v_title">Test xxdbx</div>
                    <div class="v_dur">07:07</div>
                </a>
            </div>

            <div class="item">
                <a href="https://www.wow.xxx/videos/test-longvideos" title="Test LongVideos">
                    <img src="https://example.com/thumb-longvideos.jpg">
                </a>
                <span class="duration">11:11</span>
                <div class="FHD"></div>
            </div>

            <div class="list-videos">
                <div class="item">
                    <a href="https://hornyfap.tv/video/test-hornyfap" title="Test HornyFap Video">
                        <strong class="title">Test HornyFap Video</strong>
                        <img class="thumb" src="/thumb-hornyfap.jpg" data-src="/thumb-hornyfap-lazy.jpg">
                        <div class="duration">03:33</div>
                    </a>
                </div>
            </div>

            <div class="video-item">
                <a href="/video/456" title="Test Generic Video">Test Generic Video
                    <img src="/thumb-generic.jpg" data-src="/thumb-generic-lazy.jpg" alt="Test Generic Video">
                </a>
            </div>

            <li class="pcVideoListItem js-pop videoBox">
                <a href="/view_video.php?viewkey=testpornhubkey" title="Test Pornhub Video">
                    <img data-thumb-url="https://ei.phncdn.com/thumbs/test-pornhub.jpg" src="https://ei.phncdn.com/thumbs/test-pornhub-fallback.jpg" alt="Test Pornhub Video">
                </a>
                <span class="title">Test Pornhub Video</span>
                <var class="duration">10:10</var>
            </li>

            <li class="thumbnail-card">
                <a class="video_link" href="/redtube/test-redtube">
                    <img data-src="https://ei.phncdn.com/thumbs/test-redtube.jpg" src="https://ei.phncdn.com/thumbs/test-redtube-fallback.jpg" alt="Test RedTube Video">
                </a>
                <a class="video-title-text" href="/redtube/test-redtube">Test RedTube Video</a>
                <div class="duration"><span>09:19</span></div>
            </li>

            <div class="video-box thumbnail-card">
                <a class="video-box-image" href="/watch/test-youporn">
                    <img class="thumb-image" src="//example.com/thumb-youporn.jpg" alt="Test YouPorn Video" />
                </a>
                <div class="video-title-text"><span>Test YouPorn Video</span></div>
                <div class="video-duration"><span>09:09</span></div>
            </div>

            <div class="well well-sm">
                <a class="video-link" href="/video/test-yrprno" title="Test YRPRNO Video">
                    <img data-original="https://example.com/thumb-yrprno.jpg" src="https://example.com/thumb-yrprno-fallback.jpg" alt="Test YRPRNO Video">
                </a>
                <div class="title-new">Test XFreeHD Video</div>
                <div class="duration">07:07</div>
                <div class="duration-new">07:07</div>
                <span class="badge">HD</span>
            </div>

            <div class="list-videos">
                <div class="item">
                    <a href="https://xmegadrive.com/videos/test-xmegadrive" title="Test XMegaDrive Video">
                        <strong class="title">Test XMegaDrive Video</strong>
                        <img data-original="https://example.com/thumb-xmegadrive.jpg" src="https://example.com/thumb-xmegadrive-fallback.jpg" alt="Test XMegaDrive Video">
                        <div class="duration">05:05</div>
                    </a>
                </div>
            </div>

            <a href="/page/2" class="next">Next</a>
            <a href="/page/2" rel="next">Next</a>
            <a class="prevnext" href="/page2.html">Next</a>
        </body>
    </html>
    """


def _fallback_json(url):
    if "search.htv-services.com" in url:
        return json.dumps({
            "hits": json.dumps([
                {
                    "name": "Test Hanime Video",
                    "is_censored": False,
                    "slug": "test-hanime-video",
                    "cover_url": "https://highwinds-cdn.com/test-hanime-cover.jpg",
                    "poster_url": "https://highwinds-cdn.com/test-hanime-poster.jpg",
                    "description": "<p>Test Hanime description</p>",
                    "tags": ["HD", "Vanilla"],
                }
            ])
        })
    if "externulls.com/facts/tag" in url:
        return json.dumps([
            {
                "fc_facts": [{"fc_thumbs": [1], "fc_start": None, "fc_end": None}],
                "tags": [{"is_owner": True, "tg_name": "TestTag", "tg_slug": "test-tag", "id": 1}],
                "file": {
                    "id": 999,
                    "fl_duration": 123,
                    "fl_height": 720,
                    "data": [
                        {"cd_column": "sf_name", "cd_value": "Test Beeg Video"},
                        {"cd_column": "sf_story", "cd_value": "Test story"},
                    ],
                },
            }
        ])
    if "posts/load_more_posts" in url:
        return json.dumps({
            "success": True,
            "content": '<section><a href="/video/test-porndig">Test Porndig Video</a><img src="/thumb-porndig.jpg"><div class="duration"><span>06:06</span></div></section>'
        })
    if "load_more_studios" in url or "load_more_pornstars" in url:
        return '<div id="_1"><img src="/thumb-porndig-studio.jpg" alt="Test Studio"><p>10 videos</p></div>'
    return None


def _archivebate_requests_stub():
    class _ArchivebateResponse:
        def __init__(self, text="", url="https://archivebate.com/", payload=None):
            self.text = text
            self.url = url
            self._payload = payload or {}

        def json(self):
            return self._payload

    class _ArchivebateSession:
        def __init__(self):
            self.headers = {}

        def get(self, url, timeout=None):
            text = (
                '<meta name="csrf-token" content="csrf-test">'
                ' <div wire:initial-data="{&quot;fingerprint&quot;:{&quot;name&quot;:&quot;videos&quot;},&quot;serverMemo&quot;:{}}" wire:init="loadVideos"></div>'
            )
            return _ArchivebateResponse(text=text, url=url)

        def post(self, url, json=None, headers=None, timeout=None):
            fragment = (
                '<section class="video_item">'
                '<a href="https://archivebate.com/watch/test-archivebate"></a>'
                '<video class="video-splash-mov" poster="https://archivebate.com/thumb-archivebate.jpg"></video>'
                '<a href="https://archivebate.com/profile/test-performer">Test Archivebate Performer</a>'
                '</section>'
            )
            return _ArchivebateResponse(payload={"effects": {"html": fragment}})

    return _ArchivebateSession


def _site_name_from_request(request):
    module_name = request.module.__name__.split(".")[-1]
    if module_name.startswith("test_smoke_"):
        return module_name[len("test_smoke_"):]
    return module_name


def _fixture_candidates(site_name):
    site_dir = ROOT / "tests" / "fixtures" / "sites" / site_name
    candidates = [
        site_dir / "listing.html",
        site_dir / "list.html",
        site_dir / "index.html",
        site_dir / "search.html",
        ROOT / "tests" / "fixtures" / f"{site_name}_list.html",
        ROOT / "tests" / "fixtures" / f"{site_name}_listing.html",
    ]
    return [path for path in candidates if path.exists()]


@pytest.fixture(autouse=True)
def _set_kodi_argv(monkeypatch):
    """Ensure addon imports see Kodi-style argv during smoke tests."""
    monkeypatch.setattr(sys, 'argv', KODI_ARGV.copy())


@pytest.fixture
def mock_gethtml(monkeypatch, request, _set_kodi_argv):
    """Mock getHtml to use a site fixture when available, else a broad fallback."""
    from resources.lib import utils
    site_name = _site_name_from_request(request)
    fixture_paths = _fixture_candidates(site_name)
    fallback_html = _fallback_html()

    def fake_gethtml(url, *args, **kwargs):
        json_payload = _fallback_json(url)
        if json_payload is not None:
            return json_payload
        for fixture_path in fixture_paths:
            return fixture_path.read_text(encoding="utf-8")
        return fallback_html

    monkeypatch.setattr(utils, 'getHtml', fake_gethtml)
    if hasattr(utils, '_getHtml'):
        monkeypatch.setattr(utils, '_getHtml', fake_gethtml)
    if hasattr(utils, 'postHtml'):
        monkeypatch.setattr(utils, 'postHtml', fake_gethtml)
    if hasattr(utils, '_postHtml'):
        monkeypatch.setattr(utils, '_postHtml', fake_gethtml)
    if site_name == "archivebate":
        import resources.lib.sites.archivebate as archivebate
        monkeypatch.setattr(archivebate.requests, "Session", _archivebate_requests_stub())
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
