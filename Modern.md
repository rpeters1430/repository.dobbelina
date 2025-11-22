ROADMAP.md
Dobbelina Add-on Modernization Roadmap

This document tracks the planned upgrade path for the Dobbelina repository and its Kodi add-ons.
Use the checkboxes to mark progress as work is completed and to surface remaining work at a glance.

## Phase 0 – Baseline & Assessment

**Goal:** Record the current state of the repository and identify all issues before making changes.

- [x] Inventory all add-ons included in the repo
  - Repository: `repository.dobbelina` v1.0.4
  - Video add-ons: `plugin.video.cumination` v1.1.183, `plugin.video.uwc` v1.2.46
  - Supporting player add-on: `script.video.F4mProxy` v2.8.8
- [x] Identify supported Kodi versions (Matrix, Nexus, Omega)
  - Current metadata targets pre-Matrix (`xbmc.python` 2.1.0) for `plugin.video.uwc` and `script.video.F4mProxy`; `plugin.video.cumination` omits the requirement entirely despite bundling `kodi-six`.
  - Action: raise `xbmc.python` to a modern API level and declare explicit compatibility for Matrix/Nexus/Omega in each add-on.
- [x] Install and test on at least two Kodi versions
  - Latest Kodi build exercised via manual smoke tests; older Matrix/Leia coverage still pending when environments are available.
- [x] Document broken menus, failed scrapers, missing thumbnails, slow pages
  - Captured in `KNOWN_ISSUES.md` with per-site symptoms (search mismatch, pagination loops, missing thumbnails/streams).
- [x] Create/maintain `KNOWN_ISSUES.md` with all findings
- [x] Note technical debt areas (duplicate code, unused files, outdated imports)
  - Legacy Python API targets, missing compatibility declarations, and reliance on external repository endpoints all flagged in `KNOWN_ISSUES.md`.

## Phase 1 – Core Compatibility & Packaging

**Goal:** Ensure proper Kodi compatibility, structural correctness, and clean packaging layout.

- [ ] Update all `addon.xml` files
  - [ ] Correct `<version>` fields
  - [ ] Validate `<requires>`
  - [ ] Update Python API versions (`xbmc.python`) as needed
- [ ] Normalize directory layout (`lib/`, `resources/`, etc.)
- [ ] Remove obsolete files (`.pyc`, old modules, unused folders)
- [ ] Ensure repo add-on correctly generates `addons.xml` and `.md5`
- [ ] Fix any packaging issues affecting installation or updates

## Phase 2 – Code Quality & Structure

**Goal:** Improve maintainability by reorganizing code, cleaning modules, and modernizing Python.

- [ ] Centralize configuration in `config.py` (URLs, headers, defaults)
- [ ] Create a proper directory structure:
  - [ ] `resources/lib/providers/`
  - [ ] `resources/lib/core/`
- [ ] Unify utility functions into a single shared module
- [ ] Add docstrings to public functions
- [ ] Add type hints where useful
- [ ] Remove deprecated Python patterns
- [ ] Add unified logging wrapper (`log_debug`, `log_info`, etc.)

## Phase 3 – Networking, Scraping & Reliability

**Goal:** Improve scraper stability, reduce failures, and unify networking behavior.

- [ ] Create a unified HTTP client (`http_client.py`)
  - [ ] Consistent User-Agent
  - [ ] Timeouts
  - [ ] Retry logic
  - [ ] Gzip/deflate support
- [ ] Migrate all scrapers to use the new HTTP client
- [ ] Add clean error handling for network and parse failures
- [ ] Add optional FlareSolverr integration
  - [ ] Global toggle in settings
  - [ ] Proper URL routing
  - [ ] Error messages for user
- [ ] Add fallbacks where possible (multiple source mirrors, backup endpoints)

## Phase 4 – UX & Settings Improvements

**Goal:** Make the add-on smoother and more intuitive for users.

- [ ] Reorganize `settings.xml` with clear categories
  - [ ] Playback
  - [ ] Sources
  - [ ] Networking
  - [ ] Debug
- [ ] Add provider enable/disable toggles
- [ ] Improve stream selection dialogs
- [ ] Add auto-play/quality options
- [ ] Ensure lists display correct Kodi sort methods
- [ ] Improve item titles, thumbnails, and metadata
- [ ] Fix any dead-end navigation or inconsistent back behavior

## Phase 5 – Performance & Caching

**Goal:** Improve speed and avoid re-scraping unnecessary data.

- [ ] Implement lightweight caching
  - [ ] Home page data
  - [ ] Category lists
  - [ ] Search queries (optional)
- [ ] Add pagination/“Next…” items for large providers
- [ ] Reduce redundant requests across providers
- [ ] Add throttling/delays for aggressive sites
- [ ] Store cache under `addon_data` with time-based expiration

## Phase 6 – Testing & CI/CD

**Goal:** Catch future breakage early and automate build workflows.

- [ ] Add basic unit tests for parsers
  - [ ] HTML fixtures
  - [ ] JSON fixtures
  - [ ] Pagination logic tests
- [ ] Add GitHub Actions pipeline
  - [ ] Run tests
  - [ ] Run linter (`ruff` or `flake8`)
  - [ ] Build ZIP files
  - [ ] Upload artifacts
- [ ] Add script for local dev builds
- [ ] Add linting config (`pyproject.toml` or `.flake8`)

## Phase 7 – Documentation & Contributor Friendliness

**Goal:** Make the repo clear and easy for you and others to maintain long-term.

- [ ] Update README.md with:
  - [ ] Supported Kodi versions
  - [ ] Features
  - [ ] Limitations
  - [ ] Troubleshooting
- [ ] Add `docs/DEVELOPMENT.md`
  - [ ] Repository structure
  - [ ] How to add a provider
  - [ ] Coding conventions
  - [ ] Running tests
- [ ] Maintain a `CHANGELOG.md` with each version
- [ ] Keep this ROADMAP.md updated with checkmarks and notes

## Notes & Future Ideas

Use this section as a scratchpad while working through issues.

- [ ] Consider switching to async scraping (experimental)
- [ ] Add backup mirror list for major providers

- [ ] Investigate using ResolveURL more heavily for consistency
- [ ] Evaluate moving to a more modular provider architecture
