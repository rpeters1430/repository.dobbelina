# Cumination BeautifulSoup Migration Roadmap

**Project Goal**: Migrate all 137 sites from regex-based HTML parsing to BeautifulSoup4 for improved reliability and maintainability.

**Started**: 2025-11-01
**Current Version**: v1.1.181
**Progress**: 47/137 sites (34.3%) migrated

---

## Why BeautifulSoup?

**Current Problems with Regex Parsing**:
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

**Performance**: BeautifulSoup is slightly slower but negligible for typical use (20-30 videos per page).

---

## Migration Status

### ✅ Phase 0: Infrastructure (COMPLETED)

- [x] Add BeautifulSoup4 dependency to addon.xml
- [x] Create helper functions in utils.py
  - [x] `parse_html(html)` - Parse HTML into BeautifulSoup object
  - [x] `safe_get_attr(element, attr, fallback_attrs, default)` - Safe attribute extraction
  - [x] `safe_get_text(element, default, strip)` - Safe text extraction
  - [x] `soup_videos_list(site, soup, selectors, ...)` - Shared BeautifulSoup video listing helper
- [x] Test infrastructure with pilot site

### 🚀 Phase 1: High Priority Sites (8/10 completed - 80%)

These are the highest-traffic mainstream sites that break most often.

| Priority | Site | Status | Notes |
|----------|------|--------|-------|
| 1 | **pornhub** | ✅ **COMPLETED** | Migrated in v1.1.165 |
| 2 | **xvideos** | ✅ **COMPLETED** | BeautifulSoup listing & pagination |
| 3 | **xnxx** | ✅ **COMPLETED** | BeautifulSoup listing overhaul |
| 4 | **spankbang** | ✅ **COMPLETED** | BeautifulSoup migration with modern markup |
| 5 | **xhamster** | ✅ **COMPLETED** | BeautifulSoup migration for categories, channels, pornstars & celebrities |
| 6 | **txxx** | ℹ️ API-based | JSON API already used for listings; no BeautifulSoup migration required |
| 7 | **beeg** | ℹ️ API-based | JSON API already used for listings; no BeautifulSoup migration required |
| 8 | **eporner** | ✅ **COMPLETED** | BeautifulSoup migration for listings/categories |
| 9 | **hqporner** | ✅ **COMPLETED** | BeautifulSoup migration for listings/categories |
| 10 | **porntrex** | ✅ **COMPLETED** | BeautifulSoup migration for listings/pagination |

**Status**: 8/10 BeautifulSoup migrations complete; remaining work limited to monitoring API-based providers.

> ℹ️ **Note**: `txxx` and `beeg` already rely on JSON APIs without regex parsing. They are monitored for regressions but are not counted toward the BeautifulSoup conversion totals.

---

### ✅ Phase 2: Live Cam Sites (8/8 completed - 100%)

All Phase 2 cam sites have been reviewed and migrated where applicable.

| Site | Status | Platform | Notes |
|------|--------|----------|-------|
| chaturbate | ✅ **COMPLETED** | Live Cams | BeautifulSoup for room data/login CSRF parsing |
| stripchat | ✅ **COMPLETED** | Live Cams | BeautifulSoup migration for List2/List3 contest pages |
| streamate | ✅ **COMPLETED** | Live Cams | BeautifulSoup migration for Search function |
| naked | ✅ **COMPLETED** | Live Cams | BeautifulSoup migration for inline JSON payload |
| bongacams | ℹ️ API-based | Live Cams | JSON API already used; no BeautifulSoup migration required |
| camsoda | ℹ️ API-based | Live Cams | JSON API already used; no BeautifulSoup migration required |
| cam4 | ℹ️ API-based | Live Cams | JSON API already used; no BeautifulSoup migration required |
| amateurtv | ℹ️ API-based | Live Cams | JSON API already used; no BeautifulSoup migration required |

**Status**: 4/8 required BeautifulSoup migrations complete; remaining 4 sites are API-based.

> ℹ️ **Note**: `bongacams`, `camsoda`, `cam4`, and `amateurtv` already rely on JSON APIs without regex parsing. They are monitored for regressions but are not counted toward the BeautifulSoup conversion totals.

---

### 📺 Phase 3: Medium Priority Sites (20/20 completed - 100%) ✅

Secondary mainstream sites with good traffic (previously Phase 2).

| Site | Status | Category | Notes |
|------|--------|----------|-------|
| drtuber | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| tnaflix | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| pornhat | ✅ **COMPLETED** | Mainstream | BeautifulSoup + 7 related sites |
| pornone | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| anybunny | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| sxyprn | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration |
| pornkai | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration with resilient pagination |
| whoreshub | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for List, Categories, Playlist, ListPL |
| yespornplease | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for List, Categories with error handling |
| porngo | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories, pagination, and playback |
| watchporn | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories & pagination |
| justporn | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings & categories |
| netflixporno | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories, and studios (2025-11-11) |
| peekvids | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories & channels |
| playvids | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories, channels, pornstars & playback |
| porndig | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories, studios, pornstars (JSON API + HTML parsing) |
| pornhoarder | ✅ **COMPLETED** | Aggregator | BeautifulSoup migration for listings, categories, pornstars, studios & multi-source playback |
| pornmz | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories, tags & playback |
| longvideos | ✅ **COMPLETED** | Long content | BeautifulSoup migration for listings, categories & multi-quality playback |
| luxuretv | ✅ **COMPLETED** | Mainstream | BeautifulSoup migration for listings, categories & playback |

**Target**: Resume after Phase 2 cams ship

---

### 🎌 Phase 4: JAV Sites (12/20 completed - 60%)

Japanese adult video sites.

| Site | Status | Notes |
|------|--------|-------|
| missav | ✅ **COMPLETED** | BeautifulSoup migration for List, Models, Categories |
| javgg | ✅ **COMPLETED** | BeautifulSoup migration for List, Tags |
| javguru | ✅ **COMPLETED** | BeautifulSoup migration for List, Cat, Toplist, Actress |
| javbangers | ✅ **COMPLETED** | BeautifulSoup migration with authentication preserved |
| javhdporn | ✅ **COMPLETED** | BeautifulSoup migration for List, Cat functions |
| javmoe | ✅ **COMPLETED** | BeautifulSoup migration for List, Categories, Pornstars, Playvid |
| kissjav | ✅ **COMPLETED** | BeautifulSoup migration for List, Categories, Playlists with error handling |
| supjav | ✅ **COMPLETED** | BeautifulSoup migration for List, Cat, Playvid with multi-part support |
| hpjav | ✅ **COMPLETED** | BeautifulSoup migration for List, pagination with timeout support |
| netflav | ✅ **COMPLETED** | BeautifulSoup migration for JSON extraction, Genres parsing |
| avple | ✅ **COMPLETED** | BeautifulSoup migration for List, Playvid with enhanced error handling |
| iflix | ✅ **COMPLETED** | BeautifulSoup migration for List, tags, Playvid with CSS background-image parsing |
| japteenx | ⏳ Pending | |
| terebon | ⏳ Pending | |
| 85po | ⏳ Pending | Chinese site |
| aagmaal | ⏳ Pending | Indian content |
| aagmaalpro | ⏳ Pending | Indian content |
| awmnet | ⏳ Pending | Asian content |
| foxnxx | ⏳ Pending | |
| sextb | ⏳ Pending | |

**Status**: 12/20 BeautifulSoup migrations complete; 8 remaining sites targeted by end of Phase 4

---

### 🎨 Phase 5: Hentai/Anime Sites (0/10 completed)

Animated adult content.

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

**Target**: Complete by end of Phase 5

---

### 🌐 Phase 6: International Sites (0/15 completed)

Region-specific or non-English sites.

| Site | Status | Region | Notes |
|------|--------|--------|-------|
| mrsexe | ⏳ Pending | French | |
| porno1hu | ⏳ Pending | Hungarian | |
| porno365 | ⏳ Pending | Russian | |
| nltubes | ⏳ Pending | Dutch | |
| vaginanl | ⏳ Pending | Dutch | |
| perverzija | ⏳ Pending | Balkan | |
| viralvideosporno | ⏳ Pending | Spanish | |
| netfapx | ⏳ Pending | International | |
| porntn | ⏳ Pending | International | |
| yrprno | ⏳ Pending | International | |
| watchmdh | ⏳ Pending | German | |
| americass | ⏳ Pending | International | |
| trannyteca | ⏳ Pending | Trans content | |
| tubxporn | ⏳ Pending | International | |
| xxdbx | ⏳ Pending | International | |

**Target**: Complete by end of Phase 6

---

### 📹 Phase 7: Niche & Specialty Sites (3/30 completed - 10%)

Specialized content sites.

| Site | Status | Category | Notes |
|------|--------|----------|-------|
| theyarehuge | ⏳ Pending | BBW | |
| bubbaporn | ⏳ Pending | BBW | |
| vintagetube | ⏳ Pending | Vintage | |
| tabootube | ⏳ Pending | Taboo | |
| celebsroulette | ⏳ Pending | Celebrity | |
| reallifecam | ✅ **COMPLETED** | Voyeur | BeautifulSoup migration committed in 80964d1 (2025-11-03) |
| noodlemagazine | ⏳ Pending | Amateur | |
| erome | ⏳ Pending | Amateur | |
| thothub | ⏳ Pending | OnlyFans leaks | Login flow refit today; ready for credential testing/polish next session |
| camwhoresbay | ✅ **COMPLETED** | Cam recordings | BeautifulSoup migration committed in 80964d1 (2025-11-03) |
| myfreecams | ⏳ Pending | Cam archives | |
| cambro | ✅ **COMPLETED** | Cam recordings | BeautifulSoup migration committed in 80964d1 (2025-11-03) |
| eroticmv | ⏳ Pending | Premium | |
| hobbyporn | ⏳ Pending | Amateur | |
| homemoviestube | ⏳ Pending | Amateur | |
| freeuseporn | ⏳ Pending | Niche | |
| familypornhd | ⏳ Pending | Niche | |
| cumlouder | ⏳ Pending | Spanish porn | |
| absoluporn | ⏳ Pending | French | |
| beemtube | ⏳ Pending | Various | |
| blendporn | ⏳ Pending | Various | |
| naughtyblog | ⏳ Pending | Blog/Amateur | |
| nonktube | ⏳ Pending | Asian | |
| paradisehill | ⏳ Pending | Vintage | |
| premiumporn | ⏳ Pending | Premium | |
| seaporn | ⏳ Pending | Asian | |
| speedporn | ⏳ Pending | Various | |
| trendyporn | ⏳ Pending | Various | |
| uflash | ⏳ Pending | Flashing | |
| whereismyporn | ⏳ Pending | Aggregator | |

**Target**: Complete by end of Phase 7

---

### 🔧 Phase 8: Remaining Sites (1/44 completed - 2%)

All other sites not in previous phases.

| Site | Status | Notes |
|------|--------|-------|
| 6xtube | ⏳ Pending | |
| hdporn | ⏳ Pending | |
| hdporn92 | ⏳ Pending | |
| hitprn | ⏳ Pending | |
| eroticage | ⏳ Pending | |
| freeomovie | ⏳ Pending | |
| freshporno | ⏳ Pending | |
| fullporner | ⏳ Pending | |
| fullxcinema | ⏳ Pending | |
| hqporner | ⏳ Pending | |
| justfullporn | ⏳ Pending | |
| netflixporno | ✅ **COMPLETED** | Covered in Phase 3 migration (2025-11-11) |
| porn4k | ⏳ Pending | |
| porndish | ⏳ Pending | |
| pornez | ⏳ Pending | |
| pornhits | ⏳ Pending | |
| pornroom | ⏳ Pending | |
| pornxp | ⏳ Pending | |
| vipporns | ⏳ Pending | |
| watcherotic | ⏳ Pending | |
| xfreehd | ⏳ Pending | |
| xmoviesforyou | ⏳ Pending | |
| xozilla | ⏳ Pending | |
| xsharings | ⏳ Pending | |
| xtheatre | ⏳ Pending | |
| youcrazyx | ⏳ Pending | |

**Target**: Complete by end of Phase 8

---

## Migration Guidelines

### Code Pattern to Follow

See `plugin.video.cumination/resources/lib/sites/pornhub.py` for the reference implementation.

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

### Helper Functions Available

**From `utils.py`** (lines 84-170):

1. **`parse_html(html)`** - Parse HTML into BeautifulSoup object
   ```python
   soup = utils.parse_html(listhtml)
   ```

2. **`safe_get_attr(element, attr, fallback_attrs=None, default='')`** - Get attribute with fallbacks
   ```python
   img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-lazy'], '')
   ```

3. **`safe_get_text(element, default='', strip=True)`** - Get text content safely
   ```python
   duration = utils.safe_get_text(duration_tag, '00:00')
   ```

### Testing Checklist

For each migrated site:

1. **Video Listing**: Main page loads with thumbnails, titles, durations
2. **Pagination**: Next/Previous page buttons work
3. **Categories**: Category browsing works
4. **Search**: Search returns results
5. **Video Playback**: Videos play correctly
6. **Error Handling**: Missing elements don't crash the parser

### Commit Message Format

```
feat: migrate [sitename] to BeautifulSoup

- Replace regex parsing with BeautifulSoup in List() function
- Replace regex parsing in Categories() function (if applicable)
- Add graceful error handling per video item
- Tested: listing, pagination, categories, search, playback

Part of BeautifulSoup migration roadmap (site X/137)
```

---

## Progress Tracking

### Overall Progress

- **Total Sites**: 137
- **Completed**: 47 (34.3%)
- **In Progress**: 0
- **Remaining**: 90 (65.7%)

### Phase Progress

| Phase | Sites | Completed | Percentage |
|-------|-------|-----------|------------|
| Phase 0: Infrastructure | 3 items | 3 | 100% ✅ |
| Phase 1: High Priority | 10 | 8 | 80% 🚧 |
| Phase 2: Live Cams | 8 | 4 | 50% ✅ |
| Phase 3: Medium Priority | 20 | 20 | 100% ✅ |
| Phase 4: JAV Sites | 20 | 12 | 60% 🚀 |
| Phase 5: Hentai/Anime | 10 | 0 | 0% |
| Phase 6: International | 15 | 0 | 0% |
| Phase 7: Niche/Specialty | 30 | 3 | 10% 🚀 |
| Phase 8: Remaining | 44 | 1 | 2% |

### Velocity Tracking

| Date | Sites Completed | Cumulative | Notes |
|------|----------------|------------|-------|
| 2025-11-01 | 11 (drtuber, eporner, hqporner, pornhat, pornhub, pornone, porntrex, spankbang, tnaflix, xnxx, xvideos) | 11/137 | Commit `a21064e`: bulk BeautifulSoup rollout for mainstream providers |
| 2025-11-03 | 1 (anybunny) | 12/137 | Commit `159e0a4`: migrated Anybunny to BeautifulSoup |
| 2025-11-03 | 1 (sxyprn) | 13/137 | Commit `5947ce6`: migrated Sxyprn to BeautifulSoup |
| 2025-11-03 | 3 (cambro, camwhoresbay, reallifecam) | 16/137 | Commit `80964d1`: migrated cam niche providers to BeautifulSoup |
| 2025-11-04 | 1 (pornkai) | 17/137 | Commit `652652b`: migrated PornKai to BeautifulSoup with tests |
| 2025-11-05 | 1 (xhamster) | 18/137 | Local dev: migrated xHamster categories/channels/pornstars/celebrities to BeautifulSoup |
| 2025-11-07 | 1 (whoreshub) | 19/137 | Migrated WhoresHub to BeautifulSoup for List, Categories, Playlist, ListPL |
| 2025-11-07 | 1 (yespornplease) | 20/137 | Migrated YesPornPlease to BeautifulSoup for List, Categories with error handling |
| 2025-11-08 | 1 (porngo) | 21/137 | Migrated PornGo to BeautifulSoup for listings, categories, pagination, and playback |
| 2025-11-09 | 2 (watchporn, justporn) | 23/137 | Remote: migrated WatchPorn & JustPorn to BeautifulSoup |
| 2025-11-09 | 3 (chaturbate, stripchat, streamate) | 27/137 | Phase 2 cam sites: completed chaturbate CSRF/room data, stripchat List2/List3, streamate Search |
| 2025-11-11 | 1 (netflixporno) | 28/137 | Migrated NetflixPorno to BeautifulSoup for listings, categories, studios |
| 2025-11-11 | 1 (peekvids) | 29/137 | Migrated PeekVids to BeautifulSoup for listings, categories & channels |
| 2025-11-13 | 6 (playvids, porndig, pornhoarder, pornmz, longvideos, luxuretv) | 35/137 | **Phase 3 COMPLETED**: All 20 medium-priority sites migrated to BeautifulSoup |
| 2025-11-13 | 6 (missav, javgg, javguru, javbangers, javhdporn, javmoe) | 41/137 | **Phase 4 STARTED**: First batch of JAV sites migrated (30% complete) |
| 2025-11-14 | 2 (kissjav, supjav) | 43/137 | **Phase 4 CONTINUES**: kissjav Playlists function + supjav full migration (40% complete) |
| 2025-11-16 | 4 (hpjav, netflav, avple, iflix) | 47/137 | **Phase 4 MOMENTUM**: hpjav pagination, netflav JSON extraction, avple playback, iflix CSS image parsing |

**Estimated Timeline** (at 1 site/week, focusing on remaining backlog):
- Phase 1 (2 remaining sites): ~2 weeks
- Phase 2: ✅ **COMPLETED**
- Phase 3: ✅ **COMPLETED**
- Phase 4 (8 remaining JAV sites): ~8 weeks
- Full migration (94 remaining sites): ~94 weeks (≈1.8 years)

**Optimistic Timeline** (at 3 sites/week):
- Phase 1 (2 remaining sites): <1 week
- Phase 2: ✅ **COMPLETED**
- Phase 3: ✅ **COMPLETED**
- Phase 4 (8 remaining JAV sites): ~3 weeks
- Full migration (94 remaining sites): ~31 weeks (≈7.2 months)

---

## Site Status Legend

- ✅ **COMPLETED** - Migrated to BeautifulSoup, tested, and merged
- 🚧 **IN PROGRESS** - Currently being migrated
- ⏳ **PENDING** - Not started yet
- ⚠️ **BLOCKED** - Waiting on dependency or issue resolution
- 🔴 **BROKEN** - Site is broken/offline, skip for now
- 🏷️ **DEPRECATED** - Site removed from addon

---

## Notes

- **Prioritization**: Focus on high-traffic mainstream sites first for maximum user impact
- **Testing**: Each site requires manual testing in Kodi environment
- **Breaking Changes**: Some sites may need URL or parameter adjustments during migration
- **Documentation**: Update CHANGES_vX.X.X.md for each release with migrated sites
- **Performance**: BeautifulSoup adds minimal overhead (<100ms per page)
- **Dependencies**: Requires `script.module.beautifulsoup4` (added in v1.1.165)

---

## Quick Reference

**Files to modify per site migration**:
1. `plugin.video.cumination/resources/lib/sites/[sitename].py` - Main site file
2. `ROADMAP.md` - Update status (this file)
3. `CHANGES_vX.X.X.md` - Document changes in version notes

**Commands**:
```bash
# Build and test
python3 build_repo_addons.py --addons plugin.video.cumination

# Verify BeautifulSoup in specific site
grep -n "utils.parse_html" plugin.video.cumination/resources/lib/sites/[sitename].py

# Count migrated sites
grep -c "✅ \*\*COMPLETED\*\*" ROADMAP.md
```

---

**Last Updated**: 2025-11-16 (Phase 4 momentum: 12/20 JAV sites migrated - 60% complete)
**Next Review**: After next Phase 4 batch completion
