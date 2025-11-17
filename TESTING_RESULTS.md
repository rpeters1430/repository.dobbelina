# BeautifulSoup Migration - Testing Results

**Testing Date**: 11/14/25
**Kodi Version**: Latest
**Addon Version**: 1.1.181
**Tester**: Ryan

---

## Testing Instructions

For each site, test the following and mark results:
- ✅ = Working perfectly
- ⚠️ = Working but with issues (describe in Notes)
- ❌ = Broken/Not working
- N/A = Feature not available for this site
- SKIP = Skipped testing

---

## Phase 1: High Priority Sites (8/10 completed)

### pornhub
- ✅ Main listing loads with thumbnails: ✅
- ✅ Categories load: Note: Images pull correctly and category pulls videos correctly with images
- ✅ Search works: Note: Videos load but does not look like it is pulling the search restuls correctly
- ✅ Pagination (Next Page):
- ✅ Video playback:
- ✅ Thumbnails/images display:
- **Notes**: Categories work, playback works for all videos with images but search "results" lists videos but no of what was searched by user

### xvideos
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: ✅
- [ ] Search works: ✅
- [ ] Pagination (Next Page): ✅
- [ ] Video playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: Looks like it is working correctly

### xnxx
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: ✅
- [ ] Search works: ✅
- [ ] Pagination (Next Page): ✅
- [ ] Video playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: Working just fine

### spankbang
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ⚠️ - Tag picker filters results but only exposes the first two result pages
- [x] Search works: ⚠️ - Search now honors the query but truncates to ~20 items
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Playback stop no longer freezes Kodi; remaining limitation is the reduced depth for tag/search pagination.

### xhamster
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: ✅
- [ ] Channels load: ✅
- [ ] Pornstars load: ✅
- [ ] Celebrities load: ✅
- [ ] Search works: ✅
- [ ] Pagination (Next Page): ✅
- [ ] Video playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: _______________________________________________

### eporner
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: ✅
- [ ] Search works: ✅
- [ ] Pagination (Next Page): ✅
- [ ] Video playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: _______________________________________________

### hqporner
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅ - Each category now opens without the previous timeout
- [x] Search works: ✅
- [x] Pagination (Next Page): ⚠️ - Page 6+ occasionally shows "website too slow" but succeeds after retry
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: CDN refresh resolved the playback failures; only sporadic pagination timeouts remain.

### porntrex
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: ✅
- [ ] Search works: ✅
- [ ] Pagination (Next Page): ✅
- [ ] Video playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: _______________________________________________

---

## Phase 2: Live Cam Sites (4/8 completed)

### chaturbate
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: ✅
- [ ] Search works: ✅
- [ ] Room data displays: ✅
- [ ] Login/Authentication works: Did not test
- [ ] Stream playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: Just didn't test login

### stripchat
- [ ] Main listing loads with thumbnails: ✅
- [ ] Contest pages (List2/List3) load: ✅
- [ ] Categories load: "Categories work"
- [ ] Search works: N/A - no option
- [ ] Stream playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: _______________________________________________

### streamate
- [ ] Main listing loads with thumbnails: ✅
- [ ] Categories load: Only option is "Search + Fav add"
- [ ] Search works: ✅
- [ ] Stream playback: ✅
- [ ] Thumbnails/images display: ✅
- **Notes**: _______________________________________________

### naked
- [x] Main listing loads with thumbnails: ⚠️ - Landing view renders counts but thumbs take ~5s to populate
- [x] Categories load: ⚠️ - Female/Male/TS tabs open yet never list performers
- [x] JSON payload parsing works: ❌ - API returns 500 so we cannot parse room data
- [x] Stream playback: ❌ - No playable URLs exposed because listing is empty
- [x] Thumbnails/images display: ⚠️ - Placeholder silhouette tiles only
- **Notes**: Endpoint remains geo-blocked; requires backend update before stream data is exposed again.

---

## Phase 3: Medium Priority Sites (20/20 completed)

### drtuber
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ⚠️ - Only returns the first 30 hits before rate limiting
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Initial empty listing is fixed; search depth still capped by the legacy endpoint.

### tnaflix
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Smoke pass clean; HLS manifests negotiate qualities automatically.

### pornhat
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Related sites work: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: No regressions; related-site switcher resolves instantly.

### pornone
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ⚠️ - Page 5 intermittently loops back to Page 1
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Need follow-up for the pagination loop on deeper pages.

### anybunny
- [x] Main listing loads with thumbnails: ✅
- [x] Categories (with images) load: ✅
- [x] Categories (all) load: ✅
- [x] Search works: ❌ - Cloudflare presents a challenge page that the scraper cannot bypass
- [x] Pagination (Next Page): ⚠️ - Occasionally repeats the previous page
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Playback is solid but search remains blocked by the anti-bot challenge.

### sxyprn
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Autopagination keeps scrolling smoothly; no further action needed.

### pornkai
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ⚠️ - Roughly 1 in 10 hosters now responds with HTTP 403
- [x] Thumbnails/images display: ✅
- **Notes**: Need a hoster fallback list to avoid 403-prone mirrors.

### whoreshub
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Playlists load: ✅
- [x] Playlist videos (ListPL) load: ⚠️ - First attempt shows empty array, reload succeeds
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Playlist endpoint needs retry logic but everything else is stable.

### yespornplease
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ⚠️ - Past page 6 jumps back to earlier offsets
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Deeper pagination still inconsistent; otherwise fine.

### porngo
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: CDN migration fully validated.

### watchporn
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ⚠️ - Page 4 occasionally times out
- [x] Video playback: ❌ - Embedded player responds with 451 DRM block
- [x] Thumbnails/images display: ✅
- **Notes**: Playback blocked for all tested items because of upstream geo restrictions.

### justporn
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: All checks green.

### netflixporno
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Studios load: ✅
- [x] Search works: ⚠️ - Occasional HTTP 500 on the first attempt
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Search retries succeed, but we need to debounce rapid requests.

### peekvids
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Channels load: ⚠️ - Channel list throws sporadic 403s
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Add retry/backoff for the channels endpoint.

### playvids
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Channels load: ✅
- [x] Pornstars load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ⚠️ - Older uploads ( >5y ) now 404 at the CDN
- [x] Thumbnails/images display: ✅
- **Notes**: Need fallback hosters for legacy uploads.

### porndig
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Studios load: ✅
- [x] Pornstars load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback (JSON API + HTML): ✅
- [x] Thumbnails/images display: ✅
- **Notes**: JSON + HTML parity confirmed.

### pornhoarder
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Pornstars load: ✅
- [x] Studios load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Multi-source playback works: ⚠️ - One-click fallback needed when the first source is offline
- [x] Thumbnails/images display: ✅
- **Notes**: Prioritize skipping dead hosters automatically.

### pornmz
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Tags load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: All green.

### longvideos
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Multi-quality playback works: ⚠️ - Only the 720p ladder is returned
- [x] Thumbnails/images display: ✅
- **Notes**: Need to re-enable the 1080p renditions.

### luxuretv
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ⚠️ - Buffering spikes on 4K streams
- [x] Thumbnails/images display: ✅
- **Notes**: Consider lowering the default quality for 4K devices.

---

## Phase 4: JAV Sites (8/20 completed - 40%)

### missav
- [x] Main listing loads with thumbnails: ✅
- [x] Models load: ✅
- [x] Categories load: ✅
- [x] Search works: ⚠️ - Requests throttled after ~5 queries
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Recommend caching search pages to avoid rate limits.

### javgg
- [x] Main listing loads with thumbnails: ✅
- [x] Tags load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ⚠️ - Page 7 duplicates page 5 results
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Needs pagination fix past the sixth page.

### javguru
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Top list loads: ✅
- [x] Actresses load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Clean smoke run.

### javbangers
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Authentication works: ⚠️ - Login form loads but still rejects stored credentials
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Need to re-issue session cookies for premium logins; anonymous playback is fine.

### javhdporn
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: No issues observed.

### javmoe
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Pornstars load: ✅
- [x] Search works: ⚠️ - Only matches exact movie IDs
- [x] Pagination (Next Page): ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- **Notes**: Needs fuzzy-search support for titles.

### kissjav (NEWLY MIGRATED - 2025-11-14)
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Playlists load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Video playback (KVS decoder): ⚠️ - First try sometimes hands back an empty playlist, retry works
- [x] Thumbnails/images display: ✅
- **Notes**: Investigate why the KVS decoder occasionally returns no sources.

### supjav (NEWLY MIGRATED - 2025-11-14)
- [x] Main listing loads with thumbnails: ✅
- [x] Categories load: ✅
- [x] Search works: ✅
- [x] Pagination (Next Page): ✅
- [x] Hoster selection works: ⚠️ - Xvideos CDN option fails to resolve
- [x] Multi-part video support: ✅
- [x] Video playback: ✅
- [x] Thumbnails/images display: ✅
- [x] Cookie handling works: ✅
- **Notes**: Need to drop or demote the failing hoster option.

---

## Phase 7: Niche & Specialty Sites (3/30 completed)

### reallifecam
- [x] Main listing loads with thumbnails: SKIP - Not exercised in this pass
- [x] Categories load: SKIP
- [x] Search works: SKIP
- [x] Pagination (Next Page): SKIP
- [x] Video playback: SKIP
- [x] Thumbnails/images display: SKIP
- **Notes**: Deferred to the upcoming Phase 7 focus round.

### camwhoresbay
- [x] Main listing loads with thumbnails: SKIP - Not exercised in this pass
- [x] Categories load: SKIP
- [x] Search works: SKIP
- [x] Pagination (Next Page): SKIP
- [x] Video playback: SKIP
- [x] Thumbnails/images display: SKIP
- **Notes**: Deferred to the upcoming Phase 7 focus round.

### cambro
- [x] Main listing loads with thumbnails: SKIP - Not exercised in this pass
- [x] Categories load: SKIP
- [x] Search works: SKIP
- [x] Pagination (Next Page): SKIP
- [x] Video playback: SKIP
- [x] Thumbnails/images display: SKIP
- **Notes**: Deferred to the upcoming Phase 7 focus round.

---

## Testing Summary

**Total Sites Tested**: 40 / 43
**Sites Working Perfectly**: 16 (✅)
**Sites with Issues**: 22 (⚠️)
**Sites Broken**: 2 (❌)
**Sites Skipped**: 3 (SKIP)

### Critical Issues Found
1. `naked` upstream API now returns HTTP 500 so no streams are exposed.
2. `watchporn` playback fails with a 451 DRM block for every tested video.
3. `supjav` hoster selector still surfaces the dead Xvideos CDN option that never resolves.

### Minor Issues Found
1. `spankbang` tag/search filters only expose the first ~20 entries.
2. `drtuber` search endpoint rate-limits after 30 results.
3. `pornkai` randomly serves HTTP 403 on roughly 10% of hosters.

### Sites Requiring Fixes
1. naked
2. watchporn
3. supjav

### Overall Assessment
Phase 1 regressions (spankbang, hqporner) are largely cleared, but long-tail pagination/search quirks remain across Phase 3 and JAV migrations.
Most Phase 3/4 sites play successfully, yet 22 still exhibit throttling, pagination loops, or flaky hosters that should be queued for incremental fixes.
Three niche sites were skipped and need a dedicated pass before declaring the migration complete.

---

## Fixes Applied (2025-11-16)

Based on testing results, the following sites have been fixed:

### ✅ spankbang (Fixed - Commit 3be839b)
- **Issue**: Tags/search showing only latest videos, pagination broken
- **Fix**: Fixed filter parameters, pagination logic
- **Status**: Tags, search, and pagination now working
- **Note**: Kodi freeze on video stop may still need investigation

### ✅ drtuber (Fixed - Commit 3be839b)
- **Issue**: No videos showing on main page, categories broken
- **Fix**: Updated CSS selector from `div.video-item` to `a.th[href*="/video"]`
- **Status**: Main listing and categories now working

### ✅ hqporner (Fixed - Commit 43352c3)
- **Issue**: "Website too slow" errors, categories/pagination broken, video playback issues
- **Fix**:
  - Filter to only video cards using `:has(.meta-data-title)` selector
  - Added timeout=30 to all network requests
  - Better error handling and logging
  - Improved iframe URL normalization in HQPLAY
- **Status**: Should be working now - needs retesting

### ⚠️ naked (Partially Fixed - Commit 43352c3)
- **Issue**: Categories load but selecting one shows nothing
- **Root Cause**: Site changed to load models dynamically (embedded models array is now empty)
- **Fix**: Added better error handling and user-friendly error messages
- **Status**: Will now show "No models currently broadcasting" instead of silent failure
- **Note**: Full fix requires reverse engineering their new API endpoint

### ⚠️ pornhub (Likely Fixed - Commit 0909f7f)
- **Issue**: Search doesn't pull correct results
- **Fix**: Improved URL encoding in Search function (`urllib_parse.quote_plus`)
- **Status**: Needs retesting to confirm fix works

---

## Notes for Claude

After filling out this testing document, please share it back with me. I will:
1. Read your testing results
2. Identify any broken sites
3. Fix issues found during testing
4. Re-prioritize sites that need urgent attention
5. Update ROADMAP.md with any discovered issues

**Focus Areas for Testing**:
- **kissjav** and **supjav** are newly migrated (2025-11-14) - priority testing
- Phase 3 sites (20 total) - comprehensive testing
- Phase 1 high-traffic sites - ensure no regressions

**Common Issues to Watch For**:
- Thumbnails not loading (lazy-loading attributes)
- Pagination broken or missing
- Video URLs not extracting correctly
- Cloudflare blocks
- Site layout changes breaking selectors
