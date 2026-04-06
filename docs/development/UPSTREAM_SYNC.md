# Upstream Sync Tracking

**Purpose**: Track which commits from upstream (dobbelina/repository.dobbelina) have been integrated into this fork.

**Last Updated**: 2026-04-06
**Last Sync**: 2026-04-06 - Ported reallifecams, voyeur-house, and watchporn fixes from upstream commit f12e1d25

---

## How to Use This File

1. **Before cherry-picking**: Check this file to see if a commit is already integrated
2. **After cherry-picking**: Add the new entry to the appropriate section below
3. **Format for new entries**:
   ```
   | `upstream-hash` | Commit message | `fork-hash` | YYYY-MM-DD | Notes |
   ```

---

## Already Integrated Commits

These upstream commits have been integrated into the fork:

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
