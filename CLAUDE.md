# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Kodi addon repository for adult content. The primary addon is **Cumination** (`plugin.video.cumination`), providing access to ~170 adult video sites through Kodi's plugin system. This is a fork that tracks upstream (dobbelina/repository.dobbelina).

Other addons in the repo: `plugin.video.uwc` (legacy fork), `repository.dobbelina` (repo installer), `script.video.F4mProxy` (HLS/F4M helper).

## Commands

```bash
# Setup (or run ./setup.sh which handles system deps + venv)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-test.txt

# Tests
python run_tests.py                              # All tests (recommended - cross-platform)
python run_tests.py --site pornhub -v            # Single site test
python run_tests.py --coverage                   # With coverage
pytest tests/sites/test_pornhub.py -v            # Direct pytest
pytest tests/test_utils.py::test_parse_html -v   # Single test function

# Lint
ruff check plugin.video.cumination/resources/lib/
ruff check --fix plugin.video.cumination/resources/lib/

# Build
python build_repo_addons.py --addons plugin.video.cumination
python build_repo_addons.py --update-index       # Also regenerates addons.xml + md5

# Upstream sync
python scripts/sync_manager.py --report   # Regenerate docs/development/UPSTREAM_TRIAGE.md (grouped, categorized)
python scripts/sync_manager.py            # Interactive: review pending commits, cherry-pick with tracking
python scripts/sync_manager.py --dry-run  # Preview without cherry-picking or writing to UPSTREAM_SYNC.md
```

## Architecture

### Request Flow

Kodi calls `plugin://plugin.video.cumination/?mode=sitename.Function&url=...` → `default.py` parses the URL → `URL_Dispatcher` looks up the registered function → calls it with extracted params.

### Core Components

- **`basics.py`** - Loaded first; defines global addon constants and paths (`addon`, `addon_handle`, `cookiePath`, `favoritesdb`, `profileDir`, `imgDir`, etc.). Imported by both `utils.py` and `adultsite.py`.
- **`url_dispatcher.py`** - Routes mode strings to decorated functions. Registry is class-level (shared across instances).
- **`adultsite.py`** - `AdultSite` base class. Maintains a `WeakSet` of all instances for auto-discovery. Each site gets an isolated mode namespace.
- **`default.py`** - Entry point. Imports `resources.lib.sites.*` which triggers module-level `AdultSite(...)` instantiation, auto-registering each site.
- **`utils.py`** - HTTP (`getHtml`), BeautifulSoup helpers (`parse_html`, `safe_get_attr`, `safe_get_text`, `soup_videos_list`), Kodi UI utilities.
- **`sites/__init__.py`** - Auto-discovers all `.py` files in the directory as site modules. No manual `__all__` maintenance needed. Sites listed in `EXCLUDED_SITE_MODULES` (e.g. `luxuretv.py`, `missav.py`, `stripchat.py`) are intentionally hidden from the Kodi listing but still exist on disk.
- **`sites/soup_spec.py`** - `SoupSiteSpec` dataclass for declarative selector-based video listing.
- **`favorites.py`** - SQLite-backed favorites and custom site management.
- **`http_timeouts.py`** - Named timeout constants: `SHORT`=5s, `MANIFEST`=8s, `CONNECT`=10s, `PREFETCH`=12s, `MEDIUM`=15s, `DEFAULT`=30s, `LONG`=60s. Use these instead of magic numbers in site modules.
- **`decrypters/`** / **`jscrypto/`** - Custom video player decryption (KVS, Uppod, etc.)
- **`playwright_helper.py`** (in lib/) - Dev/debug tool only; same restriction as Playwright — never use in site modules. For test-time Playwright use `tests/utils/playwright_helper.py` instead.

### Site Module Pattern

Every site in `resources/lib/sites/` follows this structure:

```python
from resources.lib.adultsite import AdultSite
from resources.lib import utils

site = AdultSite('sitename', '[COLOR hotpink]Display Name[/COLOR]',
                 'https://site.url/', 'icon.png', 'about_file')

@site.register(default_mode=True)
def Main():
    site.add_dir('Categories', site.url, 'Categories', site.img_cat)
    List(site.url)
    utils.eod()

@site.register()
def List(url):
    soup = utils.parse_html(utils.getHtml(url))
    for item in soup.select('.video-item'):
        link = item.select_one('a')
        site.add_download_link(
            utils.safe_get_attr(link, 'title'),
            utils.safe_get_attr(link, 'href'),
            'Playvid',
            utils.safe_get_attr(item.select_one('img'), 'src', ['data-src', 'data-lazy']))
    utils.eod()

@site.register()
def Playvid(url, name):
    return videourl  # Kodi handles playback
```

For declarative selector-based sites, see `SoupSiteSpec` in `sites/soup_spec.py` (reference: `sites/anybunny.py`).

### Test Structure

- `tests/conftest.py` - Kodi mocks (xbmc, xbmcaddon, xbmcvfs, xbmcplugin) and sys.path setup
- `tests/fixtures/sites/` - Saved HTML from real sites for regression testing
- `tests/sites/test_*.py` - Site-specific parsing tests (hand-written, one per site)
- `tests/smoke_generated/test_smoke_*.py` - Auto-generated smoke tests (run against live sites); regenerate with `python scripts/generate_smoke_tests.py`
- `tests/test_utils.py` - BeautifulSoup helper tests

## Creating a New Site

1. Create `plugin.video.cumination/resources/lib/sites/[sitename].py` using the pattern above
2. Add icon PNG to `resources/media/` (optional)
3. Save HTML fixtures to `tests/fixtures/sites/`
4. Write tests in `tests/sites/test_[sitename].py`
5. Run: `pytest tests/sites/test_[sitename].py -v`

The module is auto-discovered — no changes to `__init__.py` needed. To intentionally hide a site from the Kodi listing without deleting it, add its filename to `EXCLUDED_SITE_MODULES` in `sites/__init__.py`.

If the site doesn't appear in Kodi: verify `AdultSite(...)` is at module level and a function has `@site.register(default_mode=True)`.

## BeautifulSoup

All new sites must use BeautifulSoup exclusively — use `parse_html()`, `safe_get_attr()`, `safe_get_text()`, and `soup_videos_list()` from utils. Reference implementation: `sites/pornhub.py`.

Find sites missing tests:
```bash
comm -23 <(grep -l "parse_html" plugin.video.cumination/resources/lib/sites/*.py | xargs -n1 basename | sed 's/.py//' | sort) <(ls tests/sites/test_*.py | xargs -n1 basename | sed 's/test_//' | sed 's/.py//' | sort)
```

## Dev Scripts (`scripts/`)

Standalone scripts for development and debugging — all use Playwright or `requests` directly (not the Kodi runtime):

- `live_smoke_test.py` / `smoke_check.py` / `run_smoke_tests.py` - Live-fetch site health checks; outputs to `results/` and `smoke_results/`
- `smoke_report_diff.py` - Diff two smoke result files to spot regressions
- `generate_smoke_tests.py` - Regenerate `tests/smoke_generated/` from current site inventory
- `generate_status_metrics.py` - Recompute status metrics written to `docs/status/STATUS_METRICS.md`
- `sniff_stripchat.py` - Stripchat-specific stream/API probing
- `playwright_sniff.py` / `playwright_listing_probe.py` - Playwright-based network sniffing for Cloudflare-protected sites
- `codegen.py` - Scaffold boilerplate for a new site module

## Version Updates

1. Edit version in `plugin.video.cumination/addon.xml` line 1
2. Run `python build_repo_addons.py --addons plugin.video.cumination --update-index`
3. Commit the modified `addon.xml`, new ZIP, updated `addons.xml` and `addons.xml.md5`

## Git Conventions

- Branch: `master`
- Commit prefixes: `feat:`, `fix:`, `chore:`
- Cherry-picks from upstream: always use `-x` flag, update `docs/development/UPSTREAM_SYNC.md`

## Upstream Commit Triage

`scripts/sync_manager.py` is the single tool for deciding which upstream (`dobbelina/repository.dobbelina`) commits matter to this fork.

- `--report` fetches upstream, groups pending commits by referenced issue number, and writes `docs/development/UPSTREAM_TRIAGE.md` with four sections:
  - **New Sites Available** - upstream added a site module we don't have at all
  - **Needs Review** - touches a site we have that isn't BS4-migrated yet, or the message mentions playback/decrypt/m3u8/hls/drm
  - **Likely Already Covered** - only touches BS4-migrated sites we already have; spot-check and skip
  - **Auto-Skip** - no site module changes (README/changelog/icon/version-bump, or removal of a site we never carried)
- Interactive mode (no flags) walks through non-BS4-only commits, lets you cherry-pick (`-x`) and auto-updates `docs/development/UPSTREAM_SYNC.md`.
- A commit is considered "already handled" if its hash appears in `UPSTREAM_SYNC.md` or in any local commit's "cherry picked from commit ..." trailer - check there before re-reviewing.

## Custom Agents

A `project-upgrade-planner` agent is available in `.claude/agents/project-upgrade-planner.md`. Use it when planning project-wide modernization, assessing technical debt, or creating a comprehensive upgrade roadmap.

## Common Issues

- **Cloudflare**: Use `flaresolverr.py` or `cloudflare.py` integration
- **HLS/M3U8**: Requires `inputstream.adaptive` (not always bundled on Linux)
- **Kodi import errors in tests**: Run from repo root with `python run_tests.py`; check `conftest.py` mocks
- **Lazy-loading images**: Check `data-src`, `data-lazy`, `data-original` attributes via `safe_get_attr` fallbacks
- **Playwright**: Only for tests and development-time site exploration. Never use Playwright in site modules — it is not available in the Kodi runtime environment
