# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Kodi addon repository for adult content addons. The primary addon is **Cumination** (plugin.video.cumination), which provides access to various adult video sites through Kodi's plugin system.

## Quick Reference

**Common Commands**:
```bash
# Build addon package
python build_repo_addons.py --addons plugin.video.cumination

# Build and update repository index
python build_repo_addons.py --update-index

# Run tests
pytest

# Run tests with coverage
pytest --cov=plugin.video.cumination/resources/lib --cov-report=term-missing

# Lint code
ruff check plugin.video.cumination/resources/lib/

# Auto-fix linting issues
ruff check --fix plugin.video.cumination/resources/lib/

# Run specific site test
pytest tests/sites/test_[sitename].py -v
```

## Repository Structure

- **plugin.video.cumination/** - Main Cumination addon (current version: 1.1.181)
  - `default.py` - Entry point, initializes URL dispatcher and loads sites
  - `resources/lib/adultsite.py` - Base class for all site implementations
  - `resources/lib/url_dispatcher.py` - Routing system using decorators
  - `resources/lib/utils.py` - HTTP fetching, BeautifulSoup helpers, UI utilities
  - `resources/lib/sites/` - Individual site modules (139 sites)
  - `resources/lib/sites/soup_spec.py` - Declarative BeautifulSoup configuration
- **plugin.video.uwc/** - Ultimate Whitecream addon (legacy, superseded by Cumination)
- **repository.dobbelina/** - Repository addon files
- **build_repo_addons.py** - Build script for packaging addons
- **addons.xml** - Repository index of available addons
- **addons.xml.md5** - MD5 checksum of addons.xml
- **tests/** - Pytest test suite with fixtures and Kodi mocks
- **MODERNIZATION.md** - Comprehensive modernization roadmap (BeautifulSoup migration, testing, networking, UX improvements)

## Building and Packaging

### Build Addon Packages

```bash
# Build all addons
python build_repo_addons.py

# Build specific addon
python build_repo_addons.py --addons plugin.video.cumination

# Build and update repository index
python build_repo_addons.py --update-index
```

The build script:
- Creates ZIP files with proper Kodi folder structure
- Excludes `.git`, `.github`, `__pycache__`, and `*.zip` files
- Uses forward-slash paths (POSIX) as required by Kodi
- Outputs to current directory by default
- Can update `addons.xml` and `addons.xml.md5` with `--update-index`

### Version Updates

When updating addon version:
1. Edit `plugin.video.cumination/addon.xml` and change version attribute
2. Run `python build_repo_addons.py --addons plugin.video.cumination --update-index`
3. Commit changes including the new ZIP and updated `addons.xml`/`addons.xml.md5`

## Cumination Addon Architecture

### Core Framework

**URL Dispatcher Pattern**: The addon uses a custom URL dispatcher system (`url_dispatcher.py`) for routing:
- Functions are registered with `@site.register()` or `@url_dispatcher.register()` decorators
- Modes are strings like `"sitename.functionname"` that route to specific functions
- The dispatcher introspects function signatures to extract and validate parameters
- Function registry is shared across all instances via class-level dictionaries
- When Kodi calls `plugin://plugin.video.cumination/?mode=pornhub.List&url=...`, the dispatcher:
  1. Parses the mode string to extract site name and function name
  2. Looks up the registered function in the class-level registry
  3. Extracts parameters from the query string
  4. Calls the function with extracted parameters

**AdultSite Base Class** (`adultsite.py`):
- Inherits from `URL_Dispatcher`
- Base class for all site implementations
- Maintains WeakSet of all site instances for dynamic site discovery
- Provides registration decorators for site-specific functions
- Each site gets its own isolated namespace for mode routing
- Supports `default_mode` to mark entry point function
- Supports `clean_mode` to mark functions that don't require age verification

**CustomSite Class** (`customsite.py`):
- Extends AdultSite for user-added custom sites
- Stores metadata in SQLite database
- Dynamically loads from filesystem at runtime
- Sites stored in `customSitesDir` and imported via `importlib`

### Site Implementation Pattern

Sites are implemented in `plugin.video.cumination/resources/lib/sites/`:

```python
from resources.lib.adultsite import AdultSite
from resources.lib import utils

site = AdultSite('sitename', '[COLOR hotpink]Display Name[/COLOR]',
                 'https://site.url/', 'icon.png', 'about_file')

@site.register(default_mode=True)
def Main():
    # Entry point for the site
    site.add_dir('Categories', url, 'Categories', site.img_cat)
    site.add_dir('Search', url, 'Search', site.img_search)
    List(site.url)
    utils.eod()

@site.register()
def List(url):
    # Parse and list videos
    listhtml = utils.getHtml(url)
    # Extract videos with BeautifulSoup (preferred) or regex (legacy)
    soup = utils.parse_html(listhtml)
    items = soup.select('.video-item')
    for item in items:
        # Extract video metadata
        site.add_download_link(name, url, 'Playvid', img, desc)
    # Handle pagination
    utils.eod()

@site.register()
def Playvid(url, name):
    # Extract video stream URL
    return videourl
```

### Key Components

**Entry Point** (`default.py`):
- Initializes URL dispatcher
- Loads all site modules from `resources/lib/sites/` via `from resources.lib.sites import *`
- Handles custom site loading via `importlib.import_module()`
- Implements main menu (`INDEX()`) and site list (`site_list()`)
- Sites are auto-discovered via `AdultSite.get_sites()` using WeakSet
- **Auto-discovery mechanism**: When a site module is imported, the `site = AdultSite(...)` instantiation automatically registers the site instance in the WeakSet. No manual registration needed.

**Utilities** (`utils.py`):
- HTTP requests with caching (`getHtml`)
- BeautifulSoup helpers (`parse_html`, `safe_get_attr`, `safe_get_text`, `soup_videos_list`)
- Cookie management
- Dialog and progress UI helpers
- Cloudflare bypass integration
- Video URL extraction helpers

**Favorites System** (`favorites.py`):
- SQLite database for storing favorite videos
- Custom lists functionality
- Integration with Kodi's context menu
- Custom site management (enable/disable/list)

**Video Resolution** (`resolveurl` integration):
- Uses `script.module.resolveurl` for supported hosts
- Custom decrypters in `resources/lib/decrypters/` for proprietary players
- Playback handled by returning videourl from Playvid functions

## BeautifulSoup Migration (Active Project)

**Current Status**: 65/137 sites migrated (47.4% complete)

The codebase is undergoing a systematic migration from regex-based HTML parsing to BeautifulSoup4. This is tracked in **MODERNIZATION.md** along with all other modernization efforts including HTTP gateway unification, test coverage expansion, repository structure improvements, and UX enhancements.

### Why BeautifulSoup?

- Sites break 8-10 times per year with regex parsing
- BeautifulSoup is resilient to HTML formatting/whitespace changes
- Graceful degradation (one video failure doesn't crash entire list)
- More readable and maintainable code
- Estimated 70% reduction in site breakage

### Migration Phases

1. **Phase 1: High Priority Sites** (8/10 completed - 80%) - pornhub, xvideos, xnxx, spankbang, xhamster, eporner, hqporner, porntrex
2. **Phase 2: Live Cam Sites** (4/4 completed - 100%) ✅ - chaturbate, stripchat, streamate, naked (API-based sites excluded)
3. **Phase 3: Medium Priority Sites** (20/20 completed - 100%) ✅ - All medium-priority sites migrated
4. **Phase 4: JAV Sites** (20/20 completed - 100%) ✅ - All JAV sites migrated
5. **Phase 5: Hentai/Anime Sites** (10/10 completed - 100%) ✅ - ALL SITES COMPLETED: hentaidude, hentaihavenco, hentai-moon, hentaistream, heroero, animeidhentai, rule34video, taboofantazy, hanime, erogarga
6. **Phase 6: International Sites** (0/15 completed)
7. **Phase 7: Niche & Specialty Sites** (5/30 completed - 17%) - reallifecam, camwhoresbay, cambro, erome, thothub completed
8. **Phase 8: Remaining Sites** (1/44 completed - 2%)

See **MODERNIZATION.md** for complete site-by-site tracking and detailed progress.

### Migration Pattern

**BEFORE (Regex)**:
```python
match = re.compile(r'<div class="item">.*?href="([^"]+)".*?title="([^"]+)"', re.DOTALL).findall(html)
for url, title in match:
    site.add_download_link(title, url, 'Playvid', img, desc)
```

**AFTER (BeautifulSoup)**:
```python
soup = utils.parse_html(html)
items = soup.select('.item, [class*="item"]')

for item in items:
    link = item.select_one('a')
    url = utils.safe_get_attr(link, 'href')
    title = utils.safe_get_attr(link, 'title')
    img_tag = item.select_one('img')
    img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-lazy'])

    site.add_download_link(title, url, 'Playvid', img, desc)
```

### Helper Functions

**BeautifulSoup Helpers** (utils.py):

1. **`parse_html(html)`** - Parse HTML string into BeautifulSoup object
2. **`safe_get_attr(element, attr, fallback_attrs=None, default='')`** - Get attribute with fallbacks for lazy-loading images
3. **`safe_get_text(element, default='', strip=True)`** - Get text content safely
4. **`soup_videos_list(site, soup, selectors, ...)`** - Shared BeautifulSoup video listing helper
   - Accepts selectors dict for items, url, title, thumbnail, pagination
   - Handles base URL normalization
   - Automatically adds directory items or download links
   - Returns extracted data for custom processing

### SoupSiteSpec Pattern (Advanced)

For sites with complex selector requirements, use the `SoupSiteSpec` dataclass to declaratively configure `soup_videos_list`:

```python
from resources.lib.sites.soup_spec import SoupSiteSpec

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        'items': ['a.video-item', 'a[href*="/videos/"]'],
        'url': {'attr': 'href'},
        'title': {
            'selector': 'img',
            'attr': 'alt',
            'fallback_selectors': [None]
        },
        'thumbnail': {
            'selector': 'img',
            'attr': 'src',
            'fallback_attrs': ['data-src', 'data-lazy']
        },
        'pagination': {
            'selectors': [{'query': 'a[rel="next"]', 'scope': 'soup'}],
            'attr': 'href',
            'label': 'Next Page',
            'mode': 'List'
        }
    },
    play_mode='Playvid'
)

@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup)
    utils.eod()
```

See `plugin.video.cumination/resources/lib/sites/anybunny.py` for a reference implementation.

### When Migrating a Site

1. Check MODERNIZATION.md for migration status and priority
2. Use BeautifulSoup pattern shown above
3. Test: listing, pagination, categories, search, playback
4. Update MODERNIZATION.md status to ✅ **COMPLETED**
5. Commit with format: `feat: migrate [sitename] to BeautifulSoup`

Reference implementation: `plugin.video.cumination/resources/lib/sites/pornhub.py`

## Creating a New Site

To add a new site to the addon:

1. **Create site module** in `plugin.video.cumination/resources/lib/sites/[sitename].py`:
   ```python
   from resources.lib.adultsite import AdultSite
   from resources.lib import utils

   site = AdultSite('sitename', '[COLOR hotpink]Site Display Name[/COLOR]',
                    'https://example.com/', 'sitename.png', 'sitename')

   @site.register(default_mode=True)
   def Main():
       site.add_dir('List Videos', site.url, 'List', site.img_cat)
       utils.eod()

   @site.register()
   def List(url):
       html = utils.getHtml(url)
       soup = utils.parse_html(html)
       # Parse and add videos
       utils.eod()

   @site.register()
   def Playvid(url, name):
       # Extract video URL
       return videourl
   ```

2. **Add site icon** (optional): Place a PNG image in `plugin.video.cumination/resources/media/`

3. **Create test fixtures** in `tests/fixtures/[sitename]/`:
   - Save sample HTML pages for testing

4. **Write tests** in `tests/sites/test_[sitename].py`:
   ```python
   def test_sitename_list():
       # Test video listing parser
       pass
   ```

5. **Test the site**:
   - Run: `pytest tests/sites/test_[sitename].py -v`
   - Install and test in Kodi

6. **Update documentation**:
   - Add to MODERNIZATION.md if part of migration
   - Update CHANGES file for version notes

## Dependencies

Cumination addon requires these Kodi modules:
- `script.module.six` - Python 2/3 compatibility
- `script.module.kodi-six` - Kodi Python compatibility layer
- `script.module.resolveurl` - Video host URL resolver
- `script.module.resolveurl.xxx` - Adult site URL resolvers
- `script.common.plugin.cache` - Caching system
- `script.module.websocket` - WebSocket support (for live cams)
- `script.module.inputstreamhelper` - HLS/DASH stream support
- `script.module.requests` - HTTP library
- `script.module.beautifulsoup4` - HTML parsing (added in v1.1.165)

## Code Style Notes

- Python 2/3 compatible (uses `six` library)
- Migrating from regex to BeautifulSoup for HTML parsing
- URL dispatcher pattern instead of traditional routing
- Decorator-based function registration
- SQLite for persistence (favorites, custom sites)
- Kodi-specific UI via `xbmcgui`, `xbmcplugin`, `xbmcaddon`

## Common Patterns

**HTML Fetching**:
```python
listhtml = utils.getHtml(url, headers=hdr)
```

**Video Extraction (BeautifulSoup - preferred)**:
```python
soup = utils.parse_html(html)
items = soup.select('.video-item')
for item in items:
    link = item.select_one('a')
    url = utils.safe_get_attr(link, 'href')
    title = utils.safe_get_attr(link, 'title')
    site.add_download_link(title, url, 'Playvid', img)
```

**Video Extraction (Regex - legacy)**:
```python
match = re.compile(r'pattern', re.DOTALL | re.IGNORECASE).findall(html)
for url, img, title in match:
    site.add_download_link(title, url, 'Playvid', img)
```

**Pagination**:
```python
nextpage = re.compile(r'<a href="([^"]+)"[^>]*>Next').findall(html)
if nextpage:
    site.add_dir('Next Page', nextpage[0], 'List', site.img_next)
```

**Video Playback**:
```python
@site.register()
def Playvid(url, name):
    videourl = extract_video_url(url)
    return videourl  # Kodi handles playback
```

## Integration with Kodi

- Addons are installed via repository.dobbelina
- Repository hosted at https://dobbelina.github.io
- Auto-updates when new versions are pushed to master branch
- Users install repository ZIP, then install addons from repo

## Common Issues

**Cloudflare Protection**: Sites with Cloudflare require:
- FlareSolverr integration (`flaresolverr.py`)
- Or cloudflare bypass (`cloudflare.py`)

**Video Player Selection**: Some sites use custom players (KVS, Uppod, etc.):
- Decrypters in `resources/lib/decrypters/`
- JavaScript crypto implementations in `resources/lib/jscrypto/`

**M3U8 Streams**: HLS streams require:
- `script.module.inputstreamhelper`
- Proper MIME type and headers

**Site Not Appearing in List**: If a new site module doesn't appear:
- Verify the module is in `resources/lib/sites/`
- Ensure `site = AdultSite(...)` is instantiated at module level
- Check that a function is decorated with `@site.register(default_mode=True)`
- Verify the module is imported via `from resources.lib.sites import *`

**Tests Failing with Kodi Import Errors**:
- Ensure you're running tests from repository root
- Check that `tests/conftest.py` contains Kodi mock fixtures
- Verify `sys.path` manipulation in conftest.py includes addon paths

## Git Workflow

- Main branch: `master`
- Create commits with descriptive messages
- Commit message format: `feat:`, `chore:`, `fix:` prefixes
- Include version numbers in commit messages for addon updates
- For pull requests from forks, see `docs/fork_pr_workflow.md`

## Testing

### Automated Testing

The project has a pytest-based test suite for parsing and utility functions:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=plugin.video.cumination/resources/lib --cov-report=term-missing

# Run specific test file
pytest tests/sites/test_pornkai.py

# Run tests for a specific function
pytest tests/test_utils.py::test_parse_html -v

# Run linting
ruff check plugin.video.cumination/resources/lib/

# Auto-fix linting issues
ruff check --fix plugin.video.cumination/resources/lib/
```

**Test Structure**:
- `tests/conftest.py` - Pytest fixtures and Kodi mocks (xbmc, xbmcaddon, xbmcvfs, xbmcplugin)
- `tests/test_utils.py` - Tests for BeautifulSoup helper functions
- `tests/sites/test_*.py` - Site-specific parsing tests
- `tests/fixtures/` - HTML fixtures from actual sites for regression testing

**When migrating a site to BeautifulSoup**:
1. Add HTML fixture file in `tests/fixtures/[sitename]/`
2. Create test file in `tests/sites/test_[sitename].py`
3. Test parsing functions with fixtures before live testing
4. Run tests: `pytest tests/sites/test_[sitename].py -v`
5. Verify code quality: `ruff check plugin.video.cumination/resources/lib/sites/[sitename].py`

### Manual Testing

For full integration testing:
1. Install addon in Kodi test environment
2. Navigate to the site in the addon UI
3. Test video playback, search, pagination, categories
4. Verify graceful error handling (missing elements don't crash)

### CI/CD Pipeline

GitHub Actions automatically:
- Runs on push to `master` branch or merged PRs
- Builds addon packages via `build_repo_addons.py`
- Generates `addons.xml` and `addons.xml.md5`
- Uploads build artifacts for 7 days
- Workflow: `.github/workflows/build-addons.yml`
