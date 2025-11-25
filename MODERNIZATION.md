# Cumination Modernization Roadmap

**Project Goal**: Systematically modernize the Cumination Kodi addon for improved reliability, maintainability, and user experience.

**Started**: 2025-11-01
**Current Version**: v1.1.183
**Overall Progress**: Phase 0 ✅ Complete | Phase 1 🚀 In Progress (BeautifulSoup: 57/137 sites - 41.6%)

---

## Table of Contents

1. [Phase 0: Baseline & Assessment](#phase-0--baseline--assessment) ✅
2. [Phase 1: BeautifulSoup Migration](#phase-1--beautifulsoup-migration) 🚀
3. [Phase 2: Core Compatibility & Packaging](#phase-2--core-compatibility--packaging)
4. [Phase 3: Code Quality & Structure](#phase-3--code-quality--structure)
5. [Phase 4: Networking & HTTP Gateway](#phase-4--networking--http-gateway)
6. [Phase 5: Testing Infrastructure](#phase-5--testing-infrastructure)
7. [Phase 6: UX & Settings Improvements](#phase-6--ux--settings-improvements)
8. [Phase 7: Performance & Caching](#phase-7--performance--caching)
9. [Phase 8: Documentation & Contributor Experience](#phase-8--documentation--contributor-experience)

---

## Phase 0 – Baseline & Assessment ✅

**Goal**: Record the current state and identify all issues before making changes.

**Status**: ✅ **COMPLETED**

- [x] Inventory all add-ons included in the repo
  - Repository: `repository.dobbelina` v1.0.4
  - Video add-ons: `plugin.video.cumination` v1.1.183, `plugin.video.uwc` v1.2.46
  - Supporting player add-on: `script.video.F4mProxy` v2.8.8
- [x] Identify supported Kodi versions (Matrix, Nexus, Omega)
  - Current metadata targets pre-Matrix (`xbmc.python` 2.1.0) for legacy addons
  - Action: raise `xbmc.python` to modern API level for Matrix/Nexus/Omega compatibility
- [x] Install and test on at least two Kodi versions
- [x] Document broken menus, failed scrapers, missing thumbnails, slow pages
  - Captured in `KNOWN_ISSUES.md` with per-site symptoms
- [x] Create/maintain `KNOWN_ISSUES.md` with all findings
- [x] Note technical debt areas (duplicate code, unused files, outdated imports)

---

## Phase 1 – BeautifulSoup Migration 🚀

**Goal**: Migrate all 137 sites from regex-based HTML parsing to BeautifulSoup4 for improved reliability.

**Status**: 🚀 **IN PROGRESS** - 57/137 sites (41.6%) migrated

### Why BeautifulSoup?

**Current Problems with Regex**:
- Sites break 8-10 times per year when HTML structure changes
- Complex regex patterns are hard to read and maintain
- Whitespace/attribute order changes break parsers
- One parsing failure crashes entire video list

**Benefits of BeautifulSoup**:
- Resilient to HTML formatting changes
- Graceful degradation (one video failure doesn't crash all)
- More readable and maintainable code
- CSS selectors easier than complex regex
- Estimated 70% reduction in site breakage

### Migration Sub-Phases

#### ✅ Sub-Phase 0: Infrastructure (COMPLETED)

- [x] Add BeautifulSoup4 dependency to addon.xml
- [x] Create helper functions in utils.py
  - [x] `parse_html(html)` - Parse HTML into BeautifulSoup object
  - [x] `safe_get_attr(element, attr, fallback_attrs, default)` - Safe attribute extraction
  - [x] `safe_get_text(element, default, strip)` - Safe text extraction
  - [x] `soup_videos_list(site, soup, selectors, ...)` - Shared video listing helper
- [x] Create `SoupSiteSpec` dataclass for declarative configurations
- [x] Test infrastructure with pilot sites

#### 🚀 Sub-Phase 1: High Priority Sites (8/10 completed - 80%)

Highest-traffic mainstream sites that break most often.

| Priority | Site | Status | Notes |
|----------|------|--------|-------|
| 1 | pornhub | ✅ **COMPLETED** | Migrated in v1.1.165 |
| 2 | xvideos | ✅ **COMPLETED** | BeautifulSoup listing & pagination |
| 3 | xnxx | ✅ **COMPLETED** | BeautifulSoup listing overhaul |
| 4 | spankbang | ✅ **COMPLETED** | BeautifulSoup migration with modern markup |
| 5 | xhamster | ✅ **COMPLETED** | BeautifulSoup for categories, channels, pornstars & celebrities |
| 6 | txxx | ℹ️ API-based | JSON API already used; no migration needed |
| 7 | beeg | ℹ️ API-based | JSON API already used; no migration needed |
| 8 | eporner | ✅ **COMPLETED** | BeautifulSoup for listings/categories |
| 9 | hqporner | ✅ **COMPLETED** | BeautifulSoup for listings/categories |
| 10 | porntrex | ✅ **COMPLETED** | BeautifulSoup for listings/pagination |

#### ✅ Sub-Phase 2: Live Cam Sites (4/4 completed - 100%) ✅

| Site | Status | Notes |
|------|--------|-------|
| chaturbate | ✅ **COMPLETED** | BeautifulSoup for room data/login CSRF parsing |
| stripchat | ✅ **COMPLETED** | BeautifulSoup for List2/List3 contest pages |
| streamate | ✅ **COMPLETED** | BeautifulSoup for Search function |
| naked | ✅ **COMPLETED** | BeautifulSoup for inline JSON payload |

> ℹ️ API-based sites (bongacams, camsoda, cam4, amateurtv) excluded from migration count

#### ✅ Sub-Phase 3: Medium Priority Sites (20/20 completed - 100%) ✅

| Site | Status | Category | Notes |
|------|--------|----------|-------|
| drtuber | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| tnaflix | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| pornhat | ✅ **COMPLETED** | Mainstream | BeautifulSoup + 7 related sites |
| pornone | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| anybunny | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| sxyprn | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| pornkai | ✅ **COMPLETED** | Mainstream | BeautifulSoup with resilient pagination |
| whoreshub | ✅ **COMPLETED** | Mainstream | BeautifulSoup for List, Categories, Playlist, ListPL |
| yespornplease | ✅ **COMPLETED** | Mainstream | BeautifulSoup for List, Categories with error handling |
| porngo | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories, pagination, playback |
| watchporn | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories & pagination |
| justporn | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings & categories |
| netflixporno | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories, studios |
| peekvids | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories & channels |
| playvids | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories, channels, pornstars & playback |
| porndig | ✅ **COMPLETED** | Mainstream | BeautifulSoup (JSON API + HTML parsing) |
| pornhoarder | ✅ **COMPLETED** | Aggregator | BeautifulSoup for listings, categories, pornstars, studios & multi-source playback |
| pornmz | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories, tags & playback |
| longvideos | ✅ **COMPLETED** | Long content | BeautifulSoup for listings, categories & multi-quality playback |
| luxuretv | ✅ **COMPLETED** | Mainstream | BeautifulSoup for listings, categories & playback |

#### ✅ Sub-Phase 4: JAV Sites (20/20 completed - 100%) ✅

| Site | Status | Notes |
|------|--------|-------|
| missav | ✅ **COMPLETED** | BeautifulSoup for List, Models, Categories |
| javgg | ✅ **COMPLETED** | BeautifulSoup for List, Tags |
| javguru | ✅ **COMPLETED** | BeautifulSoup for List, Cat, Toplist, Actress |
| javbangers | ✅ **COMPLETED** | BeautifulSoup with authentication preserved |
| javhdporn | ✅ **COMPLETED** | BeautifulSoup for List, Cat functions |
| javmoe | ✅ **COMPLETED** | BeautifulSoup for List, Categories, Pornstars, Playvid |
| kissjav | ✅ **COMPLETED** | BeautifulSoup for List, Categories, Playlists with error handling |
| supjav | ✅ **COMPLETED** | BeautifulSoup for List, Cat, Playvid with multi-part support |
| hpjav | ✅ **COMPLETED** | BeautifulSoup for List, pagination with timeout support |
| netflav | ✅ **COMPLETED** | BeautifulSoup for JSON extraction, Genres parsing |
| avple | ✅ **COMPLETED** | BeautifulSoup for List, Playvid with enhanced error handling |
| iflix | ✅ **COMPLETED** | BeautifulSoup with CSS background-image parsing |
| japteenx | ✅ **COMPLETED** | BeautifulSoup for List, Pornstars, Tags with pagination |
| foxnxx | ✅ **COMPLETED** | BeautifulSoup for List, Lookupinfo with context menus |
| sextb | ✅ **COMPLETED** | BeautifulSoup for List, Categories, Studios, Actress with pagination |
| terebon | ✅ **COMPLETED** | BeautifulSoup for List, Cat, Tags, Sites with pagination (2025-11-22) |
| 85po | ✅ **COMPLETED** | BeautifulSoup for List with quality normalization (2025-11-22) |
| aagmaal | ✅ **COMPLETED** | BeautifulSoup for List, List2, Categories (2025-11-22) |
| aagmaalpro | ✅ **COMPLETED** | BeautifulSoup for List, List2, Categories with pagination loops (2025-11-22) |
| awmnet | ✅ **COMPLETED** | BeautifulSoup for List, Tags, Categories (48-site network) (2025-11-22) |

#### ⏳ Sub-Phase 5: Hentai/Anime Sites (0/10 completed)

| Site | Status | Notes |
|------|--------|-------|
| hanime | ⏳ Pending | Popular hentai site |
| hentaidude | ⏳ Pending | |
| hentaihavenco | ⏳ Pending | |
| hentai-moon | ⏳ Pending | |
| hentaistream | ⏳ Pending | |
| heroero | ⏳ Pending | |
| animeidhentai | ⏳ Pending | |
| erogarga | ⏳ Pending | |
| rule34video | ⏳ Pending | |
| taboofantazy | ⏳ Pending | |

#### ⏳ Sub-Phase 6: International Sites (0/15 completed)

| Site | Status | Region |
|------|--------|--------|
| mrsexe | ⏳ Pending | French |
| porno1hu | ⏳ Pending | Hungarian |
| porno365 | ⏳ Pending | Russian |
| nltubes | ⏳ Pending | Dutch |
| vaginanl | ⏳ Pending | Dutch |
| perverzija | ⏳ Pending | Balkan |
| viralvideosporno | ⏳ Pending | Spanish |
| netfapx | ⏳ Pending | International |
| porntn | ⏳ Pending | International |
| yrprno | ⏳ Pending | International |
| watchmdh | ⏳ Pending | German |
| americass | ⏳ Pending | International |
| trannyteca | ⏳ Pending | Trans content |
| tubxporn | ⏳ Pending | International |
| xxdbx | ⏳ Pending | International |

#### 🚀 Sub-Phase 7: Niche & Specialty Sites (5/30 completed - 17%)

| Site | Status | Category |
|------|--------|----------|
| reallifecam | ✅ **COMPLETED** | Voyeur |
| camwhoresbay | ✅ **COMPLETED** | Cam recordings |
| cambro | ✅ **COMPLETED** | Cam recordings |
| theyarehuge | ⏳ Pending | BBW |
| bubbaporn | ⏳ Pending | BBW |
| tabootube | ⏳ Pending | Taboo |
| celebsroulette | ⏳ Pending | Celebrity |
| noodlemagazine | ⏳ Pending | Amateur |
| erome | ✅ **COMPLETED** | Amateur |
| thothub | ✅ **COMPLETED** | OnlyFans leaks |
| myfreecams | ⏳ Pending | Cam archives |
| eroticmv | ⏳ Pending | Premium |
| hobbyporn | ⏳ Pending | Amateur |
| homemoviestube | ⏳ Pending | Amateur |
| freeuseporn | ⏳ Pending | Niche |
| familypornhd | ⏳ Pending | Niche |
| cumlouder | ⏳ Pending | Spanish porn |
| absoluporn | ⏳ Pending | French |
| beemtube | ⏳ Pending | Various |
| blendporn | ⏳ Pending | Various |
| naughtyblog | ⏳ Pending | Blog/Amateur |
| nonktube | ⏳ Pending | Asian |
| paradisehill | ⏳ Pending | Vintage |
| premiumporn | ⏳ Pending | Premium |
| seaporn | ⏳ Pending | Asian |
| speedporn | ⏳ Pending | Various |
| trendyporn | ⏳ Pending | Various |
| uflash | ⏳ Pending | Flashing |
| whereismyporn | ⏳ Pending | Aggregator |

#### ⏳ Sub-Phase 8: Remaining Sites (1/44 completed - 2%)

See full list in original ROADMAP.md (24 additional sites to migrate)

### Migration Guidelines

**Reference Implementation**: `plugin.video.cumination/resources/lib/sites/pornhub.py`

**Code Pattern**:

```python
# BEFORE (Regex)
match = re.compile(r'<div class="item">.*?href="([^"]+)".*?title="([^"]+)"', re.DOTALL).findall(html)
for url, title in match:
    site.add_download_link(title, url, 'Playvid', img, desc)

# AFTER (BeautifulSoup)
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

**Testing Checklist**:
1. Video listing loads with thumbnails, titles, durations
2. Pagination works (Next/Previous)
3. Categories browsing works
4. Search returns results
5. Video playback works
6. Missing elements don't crash parser

**Commit Format**:
```
feat: migrate [sitename] to BeautifulSoup

- Replace regex parsing with BeautifulSoup in List() function
- Replace regex parsing in Categories() function
- Add graceful error handling per video item
- Tested: listing, pagination, categories, search, playback

Part of BeautifulSoup migration roadmap (site X/137)
```

### Progress Tracking

| Phase | Sites | Completed | Percentage |
|-------|-------|-----------|------------|
| Sub-Phase 0: Infrastructure | 3 items | 3 | 100% ✅ |
| Sub-Phase 1: High Priority | 10 | 8 | 80% 🚀 |
| Sub-Phase 2: Live Cams | 4 | 4 | 100% ✅ |
| Sub-Phase 3: Medium Priority | 20 | 20 | 100% ✅ |
| Sub-Phase 4: JAV Sites | 20 | 20 | 100% ✅ |
| Sub-Phase 5: Hentai/Anime | 10 | 0 | 0% |
| Sub-Phase 6: International | 15 | 0 | 0% |
| Sub-Phase 7: Niche/Specialty | 30 | 5 | 17% 🚀 |
| Sub-Phase 8: Remaining | 44 | 1 | 2% |
| **TOTAL** | **137** | **57** | **41.6%** |

**Estimated Timeline**:
- At 3 sites/week: ~27 weeks (≈6.2 months) to complete all 80 remaining sites
- At 1 site/week: ~80 weeks (≈1.5 years)

---

## Phase 2 – Core Compatibility & Packaging

**Goal**: Ensure proper Kodi compatibility, structural correctness, and clean packaging layout.

**Status**: ⏳ **PENDING**

- [x] Update all `addon.xml` files
  - [x] Correct `<version>` fields
  - [x] Validate `<requires>`
  - [x] Update Python API versions (`xbmc.python`) as needed
- [ ] Normalize directory layout (`lib/`, `resources/`, etc.)
- [x] Remove obsolete files (`.pyc`, old modules, unused folders)
- [x] Ensure repo add-on correctly generates `addons.xml` and `.md5`
- [x] Fix any packaging issues affecting installation or updates
- [ ] Update build script to use standardized `zips/` directory structure:
  ```
  zips/
    plugin.video.cumination/<version>/*.zip
    repository.dobbelina/<version>/*.zip
  addons.xml
  addons.xml.md5
  ```
- [ ] Update `repository.dobbelina/addon.xml` to use new `datadir` layout
- [ ] Optionally auto-publish zips via GitHub Releases

---

## Phase 3 – Code Quality & Structure

**Goal**: Improve maintainability by reorganizing code, cleaning modules, and modernizing Python.

**Status**: ⏳ **PENDING**

- [ ] Centralize configuration in `config.py` (URLs, headers, defaults)
- [ ] Create a proper directory structure:
  - [ ] `resources/lib/providers/`
  - [ ] `resources/lib/core/`
- [ ] Unify utility functions into a single shared module
- [ ] Add docstrings to public functions
- [ ] Add type hints where useful
- [ ] Remove deprecated Python patterns
- [ ] Add unified logging wrapper (`log_debug`, `log_info`, etc.)
- [ ] Consolidate duplicate code patterns inside site modules
- [ ] Create helper wrappers:
  - [ ] `add_directory_item()`
  - [ ] `build_listitem()`
- [ ] Gradually update formatting to modern Python (f-strings, simplified imports)

---

## Phase 4 – Networking & HTTP Gateway

**Goal**: Centralize all HTTP fetching with consistent behavior and optional FlareSolverr support.

**Status**: ⏳ **PENDING**

### Current State
- ✅ Solid `FlareSolverrManager` implemented with retries, backoff, and session handling
- ⚠️ Network helpers distributed across modules

### Tasks
- [ ] Create unified HTTP client (`http_client.py` or enhanced `utils.getHtml()`)
  - [ ] Consistent User-Agent
  - [ ] Configurable timeouts
  - [ ] Automatic retry logic with exponential backoff
  - [ ] Gzip/deflate support
  - [ ] Cookie persistence
- [ ] Create unified function: `fetch_url(url, headers=None, use_flaresolverr=False, ...)`
- [ ] Route all site modules through the unified gateway
- [ ] Add site-capability registry (e.g., `{site_name: {"requires_cf": True}}`)
- [ ] Migrate all scrapers to use the new HTTP client
- [ ] Add clean error handling for network and parse failures
- [ ] Add FlareSolverr integration
  - [ ] Global toggle in settings
  - [ ] Proper URL routing
  - [ ] User-friendly error messages
- [ ] Add fallbacks where possible (multiple source mirrors, backup endpoints)
- [ ] Unify timeouts, retries, user-agent rotation, and logging

---

## Phase 5 – Testing Infrastructure

**Goal**: Ensure stable, automated tests that protect parser behavior and detect upstream site changes.

**Status**: 🚀 **IN PROGRESS**

### Completed
- [x] Pytest suite in place
- [x] Kodi API mocks added (`xbmc`, `xbmcaddon`, `xbmcvfs`, plugin mocks, storage server)
- [x] Test fixtures for soup-based sites in `tests/fixtures/`
- [x] Tests for parsing listing pages and validating output structure
- [x] CI runs tests on every push/PR via GitHub Actions
- [x] Basic linting with `ruff`

### Still Needed
- [ ] Add coverage reporting using `pytest-cov` in CI
- [ ] Expand static analysis/linting configuration
- [ ] Add tests for:
  - [ ] Video detail pages
  - [ ] Pagination behavior
  - [ ] Error-handling paths
  - [ ] Category listings
  - [ ] Search functionality
- [ ] Add HTML fixtures for all migrated sites
- [ ] Create test file for each migrated site before marking complete
- [ ] Add JSON fixtures for API-based sites
- [ ] Add basic unit tests for all parser functions

**Testing Commands**:
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=plugin.video.cumination/resources/lib --cov-report=term-missing

# Run specific site test
pytest tests/sites/test_[sitename].py -v

# Run linting
ruff check plugin.video.cumination/resources/lib/

# Auto-fix linting issues
ruff check --fix plugin.video.cumination/resources/lib/
```

---

## Phase 6 – UX & Settings Improvements

**Goal**: Make the add-on smoother and more intuitive for users.

**Status**: ⏳ **PENDING**

- [ ] Reorganize `settings.xml` with clear categories
  - [ ] General
  - [ ] Playback
  - [ ] Sources/Providers
  - [ ] Networking
  - [ ] Debug/Developer
- [ ] Add descriptive help text for all settings
- [ ] Improve string organization inside `resources/language/`
- [ ] Add provider enable/disable toggles
- [ ] Improve stream selection dialogs
- [ ] Add auto-play/quality options
- [ ] Ensure lists display correct Kodi sort methods
- [ ] Improve item titles, thumbnails, and metadata
- [ ] Fix any dead-end navigation or inconsistent back behavior

---

## Phase 7 – Performance & Caching

**Goal**: Improve speed and avoid re-scraping unnecessary data.

**Status**: ⏳ **PENDING**

- [ ] Implement lightweight caching
  - [ ] Home page data
  - [ ] Category lists
  - [ ] Search queries (optional)
- [ ] Add pagination/"Next…" items for large providers
- [ ] Reduce redundant requests across providers
- [ ] Add throttling/delays for aggressive sites
- [ ] Store cache under `addon_data` with time-based expiration
- [ ] Use existing `script.common.plugin.cache` more effectively

---

## Phase 8 – Documentation & Contributor Experience

**Goal**: Make the repo clear and easy for maintainers and contributors.

**Status**: 🚀 **IN PROGRESS**

### Completed
- [x] Updated `README.md` with installation and features
- [x] Created `CLAUDE.md` with comprehensive development guide
- [x] Created consolidated `MODERNIZATION.md` (this file)
- [x] Documented dev workflows and testing methods
- [x] Created `KNOWN_ISSUES.md` tracking site-specific problems

### Still Needed
- [ ] Add `CONTRIBUTING.md` with:
  - [ ] Branching workflow
  - [ ] Coding standards
  - [ ] How to build zips
  - [ ] How to run tests
  - [ ] How to add a new site
- [ ] Update `README.md` with:
  - [ ] Supported Kodi versions (Matrix, Nexus, Omega)
  - [ ] Feature list
  - [ ] Known limitations
  - [ ] Troubleshooting section
- [ ] Maintain `CHANGELOG.md` with each version
- [ ] Link all documentation sections clearly from `README.md`
- [ ] Keep this roadmap updated with checkmarks and notes

---

## Notes & Future Ideas

Use this section as a scratchpad while working through issues.

**Performance Experiments**:
- [ ] Consider switching to async scraping (experimental)
- [ ] Add backup mirror list for major providers
- [ ] Investigate using ResolveURL more heavily for consistency

**Architecture Improvements**:
- [ ] Evaluate moving to a more modular provider architecture
- [ ] Consider plugin system for custom site additions
- [ ] Explore automatic site detection/classification

**User Features**:
- [ ] Favorites synchronization across devices
- [ ] Viewing history tracking
- [ ] Resume playback from last position
- [ ] Recommendations based on viewing history

---

## Legend

- ✅ **COMPLETED** - Migrated/implemented and tested
- 🚀 **IN PROGRESS** - Currently being worked on
- ⏳ **PENDING** - Not started yet
- ⚠️ **BLOCKED** - Waiting on dependency or issue resolution
- 🔴 **BROKEN** - Site is broken/offline, skip for now
- ℹ️ **API-based** - Already uses JSON API, no BeautifulSoup migration needed

---

**Last Updated**: 2025-11-22
**Next Review**: After Phase 1 (BeautifulSoup) reaches 75% completion
