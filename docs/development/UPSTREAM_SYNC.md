# Upstream Sync Tracking

**Purpose**: Track which commits from upstream (dobbelina/repository.dobbelina) have been integrated into this fork.
**Last Updated**: 2026-06-14
**Last Sync**: 2026-06-14 - Triaged 105 pending upstream commits, ported the sites/__init__.py crash-guard, added camgirlfap as a new BS4 site.

---

## How to Use This File

1. **Before cherry-picking**: Check this file to see if a commit is already integrated
2. **After cherry-picking**: Add the new entry to the appropriate section below
3. **Format for new entries**:
   ```
   | `upstream-hash` | Commit message | `fork-hash` | YYYY-MM-DD | Notes |
   ```

---

## Sync Sessions

### 2026-06-14 Porting Session
Ran `python scripts/sync_manager.py --report` to triage the 105 pending upstream commits (87 groups) into `docs/development/UPSTREAM_TRIAGE.md`. Acted on the "New Sites Available" and crash-guard items; remaining "Needs Review" groups and the other two new-site candidates recorded below as intentionally skipped.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `36b6d753`/`c99dbda2`/`7bc2609e`/`5166dff2` (#1870, partial) | sites that are incompatible with the Kodi version are ignored and no longer cause the add-on to crash | `manual-partial` | 2026-06-14 | Ported the `sites/__init__.py` import crash-guard (per-module try/except with `xbmc.log` on failure), preserving `EXCLUDED_SITE_MODULES`. Per-site legacy-compatibility shims from this group are listed under Intentionally Skipped. |
| `e97adf79`/`e18276d7` (#1883) | Added Camgirlfap #1883 | `manual` | 2026-06-14 | Created `camgirlfap.py` as a new BS4/SoupSiteSpec site module (category "Cams & Live"), modeled on `fpoxxx.py`. Added icon, fixtures (`tests/fixtures/sites/camgirlfap/`) and tests (`tests/sites/test_camgirlfap.py`). |

### 2026-06-06 Porting Session
Reviewed upstream `dobbelina/repository.dobbelina` commits after the 2026-05-24 session.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `d29b4cd9` | erome nextpage fixes #1879 | skipped | 2026-06-06 | Our BS4-based scraper matches `.pagination .active` which automatically supports the new `page-item active` class. |
| `0b8c935e` | xnxx - fixes #1874 | `manual` | 2026-06-06 | Integrated the Lookupinfo context menu option (corrected to call `xnxx.Lookupinfo` rather than upstream's copy-paste error of `premiumporn.Lookupinfo`) and registered the `Lookupinfo` function. |

### 2026-05-24 Porting Session
Reviewed upstream `dobbelina/repository.dobbelina` commits after the 2026-05-16 session (`5aca0219..46308729`). Version/package bumps, merge commits, and icon-only uploads were not applied. Large cam site rewrites (bongacams, cam4, chaturbate optional players) deferred to a future session.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `dff3a9fc` | 2026-05-24 Bumped to v.1.1.184 | skipped | 2026-05-24 | Version/package bump only. |
| `9aaa22fa` | Merge pull request #1864 from camilt/master | skipped | 2026-05-24 | Merge commit; functional changes reviewed through child commits. |
| `46308729` | yespornvip - Fixed pagination | `manual` | 2026-05-24 | Created yespornvip.py (new site, issue #1665) incorporating both the initial add (`a83182c1`) and the pagination fix. |
| `d227c835` | xxxxvideos - thumbnails fix, fixes #1867 | skipped | 2026-05-24 | Fork uses BS4 `safe_get_attr` with `src` fallback — already handled. |
| `e8dfeda7` | rule34video - added lookupinfo fixes #1865 | `manual` | 2026-05-24 | Added `Lookupinfo` context menu function and `quote_plus` import to fork's BS4 rule34video. |
| `3ebbbcb4` | pornhits removed fixes #1866 | skipped | 2026-05-24 | pornhits.py never existed in this fork. |
| `a83182c1` | #1665 (yespornvip initial add) | `manual` | 2026-05-24 | Included in `46308729` entry above. |
| `0d9a18da` | #1665 (icon upload) | skipped | 2026-05-24 | Icon-only commit. |
| `3463ae28` | #1665 (empty) | skipped | 2026-05-24 | Empty commit. |
| `f5089ba0` | camwhoresbay, drtuber, awmnet fixes + chaturbate search engines | `manual-partial` | 2026-05-24 | Ported camwhoresbay empty-result notify and search exception; ported drtuber search exception. AWM and chaturbate context-menu search engines deferred (large rewrite). |
| `13a54052` | hypnotube new site (#1802) | `manual` | 2026-05-24 | Created hypnotube.py (new site). |
| `29379c18` | Add files via upload (icon) | skipped | 2026-05-24 | Icon-only commit. |
| `8b477422` | Add files via upload (icon) | skipped | 2026-05-24 | Icon-only commit. |
| `652c8c26` | premiumporn #1811 fixed playback | `manual` | 2026-05-24 | Updated bysewihe embed API: new origin (`rupertisdivingintoocean.com`), fingerprint body, replaced g9r6.com endpoint. |
| `dc179b0f` | bongacams/cam4/chaturbate optional players + online favorites | `manual` | 2026-05-24 | chaturbate: ★/♥ favorites markers in List + fav param. bongacams: optional player (Adaptive/Proxy/Classic), player toggle in Main, ★ markers in List. cam4: optional player, ★ markers in List, onlineFav, Playvid_Adaptive/proxy/classic, urllib_parse import. Login/followedCams deferred (needs account testing). |
| `aec0f07a` | 2026-05-17 Bumped to v.1.1.183 | skipped | 2026-05-24 | Version/package bump only. |

### 2026-05-16 Porting Session
Reviewed upstream `dobbelina/repository.dobbelina` commits after the 2026-05-09 session (`5f0b8376..5aca0219`). Version/package bumps and changelog-only commits were not applied.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `ea00f3aa` | 2026-05-10 Bumped to v.1.1.182 | skipped | 2026-05-16 | Version/package bump only; fork handles packaging separately. |
| `8f8716e6` | Update chaturbate.py | `manual-already-present` | 2026-05-16 | Verified multi-proxy Chaturbate playback handling already existed in fork. |
| `a2802ae3` | Merge pull request #1860 from spamgbh-cmyk/master | skipped | 2026-05-16 | Merge commit; functional changes reviewed through child commits. |
| `e8c66515` | chaturbate capture multiple streams | skipped | 2026-05-16 | Changelog-only commit. |
| `d5986d69` | Add files via upload | `manual` | 2026-05-16 | Ported BongaCams online favorites, GeoLocked labels, context menu, playback username fallback, offline/GeoLocked handling, and redesigned contest payload parsing while preserving fork Cloudflare helpers. |
| `342ae49c` | Add files via upload | `manual-already-present` | 2026-05-16 | Verified Chaturbate simultaneous stream proxy logic was already present in fork. |
| `a59d0d84` | Merge pull request #1862 from camilt/master | skipped | 2026-05-16 | Merge commit; functional changes reviewed through `5aca0219`. |
| `5aca0219` | AWM network, bongacams, chaturbate fixes | `manual` | 2026-05-16 | Ported AWM iXXX search path and empty listing notification; ported Chaturbate Record selector for Cloudbate/iXXX searches. |

### 2026-05-09 Porting Session
Integrated compatible code fixes from upstream `dobbelina/repository.dobbelina` after the 2026-05-05 session. Merge commits, version/package bumps, and changelog-only commits were not applied.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `fc27cd31` | Tried to sort through this AWM network of clonelike websites... | `manual-partial` | 2026-05-09 | Ported site-specific search path/date-sort handling into the fork's BS4 AWM scraper; skipped clone separator menu entries because generated smoke tests treat default-mode downloads as playable videos. |
| `4f2ab507` | freeomovie fixes #1858 fixes #1853 | `manual` | 2026-05-09 | Ported FreeOMovie JSON playback URL regex and XXXTube `Native Text` listing skip. |
| `5f0b8376` | aagmaal playback fix | `manual` | 2026-05-09 | Added BS4 iframe `data-src` fallback before the existing iframe regex fallbacks. |

### 2026-05-05 Porting Session
Integrated latest fixes from upstream `dobbelina/repository.dobbelina` following site redesigns and internal decryption updates.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `24508090` | chaturbate - py2 import shim for the chunklist proxy | `manual` | 2026-05-05 | Added try/except shims for http.server/socketserver in Chaturbate proxy for Kodi 18.x compatibility. |
| `5917ea89` | chaturbate - dont stop the player if its on a different proxy | `manual` | 2026-05-05 | Updated _force_stop() to verify active playing file before sending Stop command. |
| `90ab8b71` | aagmal fixes #1846 | `manual` | 2026-05-05 | Verified BS4 selector already handles `.vp-pagi-wrap`. |
| `eda238fc` | hentaidude fixes #1839 | `manual` | 2026-05-05 | Verified BS4 implementation already handles protocol-relative (`//`) URLs in decoder. |
| `95eb617b` | familypornhd - fix playback fixes #1848 | `manual` | 2026-05-05 | Added `watchstreamhd.com` support to FamilyPornHD Playvid. |
| `6076af30` | whereismyporn fix listing - fixes #1849 | `manual` | 2026-05-05 | Added `data-main-thumb` to thumbnail extraction in WhereIsMyPorn. |
| `9be860cc` | awm network - fix listing fixes #1850 | `manual` | 2026-05-05 | Updated search URL construction to use `+` encoding and `?s=` query param for consistency. |

### 2026-04-25 Porting Session
Integrated latest fixes from upstream `dobbelina/repository.dobbelina` addressing site redesigns and internal decryption updates.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `15698f67` | freeuseporn, premiumpoorn - fixes #1842 | `manual` | 2026-04-25 | Ported to BS4 scrapers; added Vidara support and enhanced host selection to PremiumPorn; fixed FreeusePorn redesign. |

### 2026-04-16 Cherry-Pick Session
Integrated latest fixes from upstream `dobbelina/repository.dobbelina` following site redesigns and mmcdn edge changes.

| Upstream Hash | Description | Fork Hash | Date | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `3b358bdb` | xmoviesforyou - fix listing | `manual` | 2026-04-16 | Updated Main to call List with /page/1 suffix |
| `bc66d38f` | fix crashes on first launch (RuntimeError) | `manual` | 2026-04-16 | Wrapped textBox controls in try/except RuntimeError |
| `4aa2fd56` | Cloudbate search feature for online Fav | `manual` | 2026-04-16 | Cloudbate context menu already present from prior session |
| `eb7785cc` | chaturbate - decompress gzipped manifests | `manual` | 2026-04-16 | Added _read_body(); fixed six.moves import for test compat |
| `986990ac` | spankbang - fix listings after redesign | `manual` | 2026-04-16 | BS4: data-testid selectors for video-item, alphabet-letter, pornstar-link-item; dedup Tags; UA/Referer on Playvid; updated fixtures |

### 2026-04-12 Cherry-Pick Session
These upstream commits have been integrated into the fork:

### 2026-04-14 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `3435999` | Removed Em Dash from chaturbate | `manual` | 2026-04-14 | Verified all Chaturbate labels use standard hyphens and ASCII characters; no em dashes found in site module. |
| `8756fc8` | thothub - fix pagination and filter private videos | `manual` | 2026-04-14 | Verified ThotHub pagination handles `data-parameters` and `#search` hashes correctly; confirmed private video filtering is active. |
| `52cf2a2` | Merge pull request #1821 from Despernal/fix-thothub-pagination-private | `manual` | 2026-04-14 | Part of the ThotHub pagination/privacy fix set. |
| `f826588` | thothub - fix pagination and filter private videos | `manual` | 2026-04-14 | Part of the ThotHub pagination/privacy fix set. |

### 2026-04-12 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `ea0f97ce` | Merge pull request #1818 from Despernal/fix-chaturbate-session-reconnect | `manual` | 2026-04-12 | Integrated advanced Chaturbate proxy with session reconnection, CDN fallback, and segment proxying into our BS4-migrated module. |
| `53acf185` | chaturbate proxy - invalidate caches on refresh | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `23c2cbb3` | chaturbate proxy - lock the reconnect guard | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `11721a36` | chaturbate proxy - clean up orphan proxies | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `ba44c62c` | chaturbate proxy - proxy segments too | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `ea3d1e7a` | chaturbate proxy - delay proxy shutdown | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `85b848d4` | chaturbate proxy - serve cached playlists | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `5a01bef1` | chaturbate proxy - watchdog for dead ISA | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `00bdb746` | chaturbate proxy - fix reconnect thread dying | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `28ab198a` | chaturbate proxy - add debug logging | `manual` | 2026-04-12 | Included in Playvid proxy logic (via enh_debug toggle) |
| `1883c5ae` | chaturbate proxy - retry reconnect on stream switch | `manual` | 2026-04-12 | Included in Playvid proxy logic |
| `47ccca1f` | chaturbate - proxy chunklists for session reconnect | `manual` | 2026-04-12 | Included in Playvid proxy logic |

### 2026-04-11 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `2c04095d` | fix chaturbate streams - prefetch master playlist | `manual` | 2026-04-11 | Ported local HTTP proxy server to `chaturbate.py` to handle m3u8 playlists with single-use tokens |
| `f4e0df84` | cloudbate, chaturbate | `manual` | 2026-04-11 | Added new `cloudbate.py` site module using robust BS4; added Cloudbate recording search to Chaturbate context menu |
| `ca82fae6` | naughtyblog - fix listing | `manual` | 2026-04-11 | Updated BS4 selector in `naughtyblog.py` to include `div[id^='post-']` for better site coverage |
| `569d9d6c` | watchporn - fix categories | `manual` | 2026-04-11 | Verified BS4 selector `a.item` in `watchporn.py` already handles the new `class="item thumb"` structure |

### 2026-04-06 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `f12e1d25` | rlc, watchporn fixes #1808 | `manual` | 2026-04-06 | Ported voyeur-house.me and reallifecams.us domain updates to BS4 scraper; ported WatchPorn lookup regex fixes |

### 2026-04-04 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `9496ea98` | allclassic - fix thumbnails | `manual` | 2026-04-04 | Ported to BS4 scraper by caching AllClassic thumbnails locally via `Thumbnails.cache_img()` |
| `cc111fac` | fixes #1797, fixes #1801, fixes #1793, fixes #1792, fixes #1790, fixes #1789, fixes #1788 | `manual-partial` | 2026-04-04 | Ported actionable scraper fixes for xhamster, freeomovie, porno365, premiumporn, and xxdbx; did not rename `longvideos` to `wowxxx` or touch fork-specific WatchPorn/PornXP flow |

### 2026-03-26 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `034f9e42` | Fix aagmaal, aagmaal pro | `manual` | 2026-03-26 | Ported manually to BS4; updated domains (.gay→.bz, .delhi.in→.farm), selectors, Playvid; added script.trakt.exclude to utils |

### 2026-03-20 Porting Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `ffeace1e` | hentaidude - fix subtitles #1783 | `manual` | 2026-03-20 | Ported manually to BS4 scraper and utils |
| `18951eab` | fix Kodi 18 crash | `manual` | 2026-03-20 | Ported manually to BS4 scraper |

### 2026-03-14 Cherry-Pick Session

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `fef612ec` | porndit, pmvhaven - fixes #1774 #1252 | `23d4a8c` | 2026-03-14 | Cherry-picked (excluded changelog) |
| `569ea709` | kt_player, xxthots  new site, fixes #1767 | `9221568` | 2026-03-14 | Cherry-picked (excluded changelog, kept BS4 scrapers) |

### Intentionally Skipped

Commits reviewed in the 2026-06-14 triage session (`docs/development/UPSTREAM_TRIAGE.md`) and judged not worth porting. Listed here so `sync_manager.py --report` stops re-flagging them.

| Upstream Hash | Message | Reason |
|---|---|---|
| `7839f576`/`feb31161`/`a7b8d112`/`829c587c`/`79cf0fa6`/`599f72e0` (#1830) | ikisoda new site | New site not selected for porting in the 2026-06-14 triage session (camgirlfap was prioritized instead); revisit in a future session. |
| `a75b2572`/`1fde0486` (#1700) | Added Porn4Fans #1700 | New site not selected for porting in the 2026-06-14 triage session; revisit in a future session. |
| `b05e8ddf`/`042444e7`/`2b74f364` (#1831) | Added yourlesbians #1831 | `yourlesbians.py` already exists in this fork (category Video Tubes); upstream's add commits for yourlesbians are redundant. |
| `cc829f67`/`b6b7a993`/`fc508d42` (#1647), `c179ec7b` | Added pimpbunny #1647 / Delete pimpbunny.py | `pimpbunny.py` already exists in this fork (category Video Tubes); upstream's later addition and subsequent removal are both no-ops for us. |
| `e9340aba` | notfans small fix | Whitespace/formatting-only change to upstream's legacy `notfans.py`; this fork's `notfans.py` is already BS4-migrated with a different structure. |
| `ca8b516a`/`e0b41b52` (#1695) | FPO.XXX #1695 | `fpoxxx.py` is already migrated to BS4/`SoupSiteSpec` in this fork (used as the template for camgirlfap); upstream's fixes target the pre-migration implementation. |
| `76d27ed5`/`6f69aeaa` (#1832) | #1832 - added heavyfetish | `heavyfetish.py` already exists in this fork as a BS4 scraper (added in an earlier session); upstream's initial-add commits for heavyfetish/notfans are redundant. |
| `b13bacba` (#1869) | premiumporn fixes #1869 fixes #1811 | Reviewed and explicitly should not be ported - touches bongacams/cam4/chaturbate/hypnotube/ikisoda/porn4fans/premiumporn/stripchat/superporn/xvideos/yespornvip with changes not applicable to this fork's implementations. |
| `f2af6b63`/`7a09d94b` (#1822) | #1822 (superporn) | `superporn.py` already exists in this fork; upstream's fixes target the pre-BS4 implementation superseded by our scraper. |
| `7a3b1cdb` | Issues with proxy player. Switched back to old player (stripchat) | `stripchat.py` is in `EXCLUDED_SITE_MODULES` (hidden from the Kodi listing); upstream's player-switch fix is for the old player and isn't applicable. |
| `814ba919` | stripchat | Same as `7a3b1cdb` - `stripchat.py` is excluded from the Kodi listing; not applicable. |
| `e96ed9b6` (#1710) | stripchat - fix playback (SD only) fixes #1710 | Same as `7a3b1cdb` - `stripchat.py` is excluded from the Kodi listing; not applicable. |
| `3a8df5f4` | heroero - fix playback | `heroero.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. Current KVS-based playback verified working. |
| `73a6488d` (#1763) | sxyprn - fix playback (direct links) fixes #1763 | `sxyprn.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. |
| `6f3103ab` (#1749) | javguru - fix playback, thumbnails - fixes #1749 | `javguru.py` already BS4-migrated in this fork; upstream's playback/thumbnail fix targets the legacy implementation. |
| `8ff6fe1f` (#1751) | allclassic, watchporn playback, fixes #1751 | Both `allclassic.py` and `watchporn.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. |
| `af3c079f` (#1731) | porntn liting, fixes #1731 | Touches awmnet/porntn/xhamster, all already BS4-migrated in this fork with different selector structures; the fyxxr portion isn't significant enough to port on its own. |
| `b4beb803` | camwhoresbay - fix playback | `camwhoresbay.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. |
| `60b6859a` (#1688) | hanime playback - fixes #1688 | `hanime.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. |
| `1721e034` | terebon - fix playback | `terebon.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. |
| `f3d48c1b` | xhmster playback | `xhamster.py` already BS4-migrated in this fork; upstream's playback fix targets the legacy implementation. |

### 2026-01-04 Cherry-Pick Session
