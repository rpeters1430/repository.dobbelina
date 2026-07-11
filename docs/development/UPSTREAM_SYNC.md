# Upstream Sync Tracking

**Purpose**: Track which commits from upstream (dobbelina/repository.dobbelina) have been integrated into this fork.
**Last Updated**: 2026-06-17
**Last Sync**: 2026-06-17 - Reviewed latest upstream commits, imported ikisoda with the upstream player quality fix, and recorded redundant BS4-covered fixes.

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

### 2026-06-17 Porting Session
Reviewed newest upstream commits after the 2026-06-14 triage session. Imported the upstream `ikisoda` site module and icon, including the latest quality-selection player fix, then adjusted list item ordering so automated playback checks select a real video before the settings control. Spot-checked the newest `freeuseporn`, `camcaps`/`reallifecam`/`porndish`, and `yourlesbians` upstream changes against this fork's current implementations.

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `7839f576`/`feb31161`/`a7b8d112`/`829c587c`/`79cf0fa6`/`599f72e0` (#1830), `bcecf6f6` | ikisoda #1830 / Small fix + changed player for better resolution | `manual` | 2026-06-17 | Imported `ikisoda.py` and `ikisoda.png` from upstream, including the latest quality-selection playback changes. Moved the non-playable "Change per page" control after video entries so live smoke `list,play` samples an actual video. Verified `py_compile` and live `ikisoda list,play` PASS. |
| `994701cc` | freeuseporn #1886 | `manual-already-covered` | 2026-06-17 | Upstream relaxes a legacy regex. This fork already uses `SoupSiteSpec` selectors for FreeusePorn; normal `main,list,play` live smoke PASS. |
| `a57c567a` | camcaps listing - fixes #1888 | `manual-already-covered` | 2026-06-17 | Porndish icon change is already present; Reallifecam/Camcaps listing is already BS4-based and handles flexible duration text. Live smoke for `reallifecam` and `porndish` PASS. |
| `b05e8ddf`/`042444e7`/`2b74f364` (#1831) | Added yourlesbians #1831 | `manual-already-covered` | 2026-06-17 | Rechecked during latest upstream review. This fork's `yourlesbians.py` already exists and live `list,play` PASS, so upstream's add/rewrite remains redundant. |

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
| `51a4da69` | camcaps fixes #1904 | Already modernly handled under reallifecam.py |
| `fad5cb73` | delete cam4.py | Retained working cam4.py implementation in our fork |
| `fdec806e` | Cam4 added Tags and filter by country | Retained working cam4.py implementation in our fork |
| `9f2ec98a` | #1890 (myporntape) | New site, skip regex implementation |
| `d078f264` | Bongacams fixes for Adaptive and Proxy player | Skipped due to conflicts/deferred cam player rewrites |
| `9917addc` | added site myporntape | New site, skip regex implementation |
| `267cb29e` | MyPornTape #1890 | New site, skip regex implementation |
| `8d7b487f` | MyPornTape #1890 | New site, skip regex implementation |
| `242d6706` | Fixed compatibility issues PY2+3 (cam4) | Retained working cam4.py implementation in our fork |
| `5ca9af98` | xnxx | Redundant, xnxx.png already exists and site is BS4-migrated |
| `496aec2f` | Compatibility issues with PY2 (cam4) | Retained working cam4.py implementation in our fork |
| `920bdb8c` | AWM network search fix | AWM network sites are already migrated to BS4 on our fork |
| `e6bb2487` | Update README | Upstream README change - skip |
| `46d996d2` | Updated README | Upstream README change - skip |
| `75389f3b` | Update README | Upstream README change - skip |
| `86bbcf14` | Enhance README | Upstream README change - skip |
| `d658ea5d` | Revise README | Upstream README change - skip |
| `627e95c3` | added site Thothub.tube | Thothub is already BS4-migrated in our fork |
| `e8ebd05c` | #1739 (easynews) | Easynews not implemented or used in our fork |
| `f4c5a437` | iflix - removed | Iflix not implemented or used in our fork |
| `b5ae7b69` | bubba, cambro, yespornplease removed | Not implemented or used in our fork |
| `71d13989` | vintagetube - removed | Vintagetube not implemented or used in our fork |
| `86d995a6` | hanime fixes #1686 | Hanime not implemented or used in our fork |
| `d47192d5` | camsoda #1685 | Camsoda not implemented or used in our fork |
| `80c5f5c9` | porndish | Fork has BeautifulSoup migration |
| `a42bd474` | pornhub - fixes #1907 | Fork has BeautifulSoup migration |
| `41b7c24f` | fullporner - fix listing | Fork has BeautifulSoup migration |
| `79ab0d2e` | noodlemagazine fixes #1905 | Fork has BeautifulSoup migration |
| `b936cfe3` | taboofantazy, tabootoobe fixes #1898 fixes #1899 | Fork has BeautifulSoup migration |
| `f0d1f0d7` | camcaps - nextpage fixes #1894 | Fork has BeautifulSoup migration |
| `ff9ea1b5` | awmnet #1892 | Fork has BeautifulSoup migration |
| `57423ce2` | Delete plugin.video.cumination/resources/lib/sites/xnxx.py | Fork has BeautifulSoup migration |
| `d6120389` | Excluded interactive items that cannot be played | Fork has BeautifulSoup migration |
| `b728f8a2` | xnxx fixes #1881 | Fork has BeautifulSoup migration |
| `f63e38a5` | hitprn fixes #1878 | Fork has BeautifulSoup migration |
| `1a7e69f1` | uflash removed - fixes #1877 | Fork has BeautifulSoup migration |
| `37023abb` | Reverted to original @12asdfg12 | Fork has BeautifulSoup migration |
| `2eaf2aaf` | 85po - fixes #1875 | Fork has BeautifulSoup migration |
| `6896c431` | hentaistream fixes #1872 | Fork has BeautifulSoup migration |
| `007f1622` | #1873 | Fork has BeautifulSoup migration |
| `37dc2461` | #1872 | Fork has BeautifulSoup migration |
| `f1bea989` | Update spankbang.py | Fork has BeautifulSoup migration |
| `f5534bdd` | fixes #1835 | Fork has BeautifulSoup migration |
| `39d6fc79` | Spankbang & Chaturbate fixes | Fork has BeautifulSoup migration |
| `7df873be` | fix chaturbate streams - prefetch master playlist for single-use tokens | Fork has BeautifulSoup migration |
| `ae675dbb` | Add thothub.tube | Fork has BeautifulSoup migration |
| `1a167fb7` | Fix Chaturbate | Fork has BeautifulSoup migration |
| `3461ae2f` | hentaidude - fixes #1779 | Fork has BeautifulSoup migration |
| `e1b93b42` | erome fixes #1782 | Fork has BeautifulSoup migration |
| `6e16879c` | anybunny - fixes #1773 | Fork has BeautifulSoup migration |
| `ebf141f7` | speedporn - fixes #1770 | Fork has BeautifulSoup migration |
| `ef8811de` | xmoviesforyou - fix page numbers, goto page | Fork has BeautifulSoup migration |
| `e90da9b7` | hqporner - fix thumbnails fixes #1769 | Fork has BeautifulSoup migration |
| `68e4ef97` | pornkai - fixes #1760 | Fork has BeautifulSoup migration |
| `2ad68a13` | simpvids - name chaged to camcaps - fixes #1757 | Fork has BeautifulSoup migration |
| `3e995d97` | hentaidude - fix listing - fixes #1750 | Fork has BeautifulSoup migration |
| `0d683b26` | freshporno - fix domain fixes #1748 | Fork has BeautifulSoup migration |
| `b075cbdf` | luxuretv - fix nextpage | Fork has BeautifulSoup migration |
| `004f106f` | luxuretv - fix nextpage, fixes #1734 | Fork has BeautifulSoup migration |
| `673fe9b8` | fix module load error on TvOS #1724 | Fork has BeautifulSoup migration |
| `8eae561a` | fullxcinema | Fork has BeautifulSoup migration |
| `3a98f37d` | Python 2 fixes #1722 fixes #1663 | Fork has BeautifulSoup migration |
| `c11caeb6` | pornhoarder fixes #1713 | Fork has BeautifulSoup migration |
| `31644dcc` | pornhub fixes #1712 | Fork has BeautifulSoup migration |
| `53a9dfe3` | whoreshub fixes #1715 | Fork has BeautifulSoup migration |
| `d92bd04d` | tnaflix fixes #1718 | Fork has BeautifulSoup migration |
| `0509d5b0` | premiumporn - fixes #1714 | Fork has BeautifulSoup migration |
| `51c39fb2` | porntn fixes #1720 | Fork has BeautifulSoup migration |
| `afe1ff04` | celebsroulette, awmnet | Fork has BeautifulSoup migration |
| `90d2f5af` | pornxp - domain change - fixes #1711 | Fork has BeautifulSoup migration |
| `b4daafcf` | fixes | Fork has BeautifulSoup migration |
| `d522cedb` | awmnet - fix listing | Fork has BeautifulSoup migration |
| `122e9555` | freepornvideos - new site | Fork has BeautifulSoup migration |
| `e40d58df` | camcaps site name change | Fork has BeautifulSoup migration |
| `a34c0a78` | terebon - fix listing | Fork has BeautifulSoup migration |
| `67bd60fe` | tokyomotion - new site fixes #1689 | Fork has BeautifulSoup migration |
| `9722f3eb` | camwhoresbay - fix next page | Fork has BeautifulSoup migration |






















































Commits reviewed in the 2026-06-14 triage session (`docs/development/UPSTREAM_TRIAGE.md`) and judged not worth porting. Listed here so `sync_manager.py --report` stops re-flagging them.

| Upstream Hash | Message | Reason |
|---|---|---|
| `a75b2572`/`1fde0486` (#1700) | Added Porn4Fans #1700 | New site not selected for porting in the 2026-06-14 triage session; revisit in a future session. |
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
