# Upstream Sync Tracking

**Purpose**: Track which commits from upstream (dobbelina/repository.dobbelina) have been integrated into this fork.
**Last Updated**: 2026-04-16
**Last Sync**: 2026-04-16 - Ported Chaturbate gzipped manifest fix, Spankbang full redesign fix (Tags/Models/Models_alphabet + UA/Referer), XMoviesForYou listing fix, and textBox crash fix.

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

### 2026-01-04 Cherry-Pick Session
