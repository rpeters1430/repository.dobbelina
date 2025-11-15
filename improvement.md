# IMPROVEMENT_STATUS

## Progress Tracker for Modernization & Upgrade Plan

This document summarizes the planned improvements for the project and the current status of each.
It is intended to help track ongoing migration work, repository upgrades, and development workflow refinements.

---

## 1. BeautifulSoup Migration

**Goal**

Standardize all site parsing using `BeautifulSoup`, `SoupSiteSpec`, and shared utilities such as `soup_videos_list`.

**Completed**

- Implemented `SoupSiteSpec` dataclass for unified site configurations.
- Added `utils.parse_html`, `safe_get_attr`, `make_http_timeout`, and other soup helpers.
- Updated multiple site modules to use the new `SoupSiteSpec` pattern.
- Added fixtures and parsing tests for migrated sites (anybunny, pornkai, others).
- Updated `ROADMAP.md` to track migration progress.

**Still Needed**

- Continue migrating remaining sites (~100+ not yet converted).
- Replace remaining regex-based parsers with soup-based implementations.
- Expand fixture HTML files for each migrated site.
- Add tests for each new migrated site before marking it complete.

---

## 2. HTTP / Networking Layer

**Goal**

Centralize all HTTP fetching into a single gateway function with consistent behavior and optional FlareSolverr support.

**Completed**

- Solid `FlareSolverrManager` implemented with retries, backoff, and session handling.
- Network helpers exist but are distributed across modules.

**Still Needed**

- Create a unified function, e.g. `fetch_url(url, headers=None, use_flaresolverr=False, ...)`.
- Route all site modules (new and migrated) through this function.
- Add a simple site-capability registry (e.g., `{site_name: {"requires_cf": True}}`).
- Unify timeouts, retries, user-agent rotation, and logging inside the gateway.

---

## 3. Testing Infrastructure

**Goal**

Ensure stable, automated tests that protect parser behavior and detect upstream site changes.

**Completed**

- Pytest suite in place.
- Kodi API mocks added (`xbmc`, `xbmcaddon`, `xbmcvfs`, plugin mocks, storage server).
- Test fixtures for soup-based sites.
- Tests for parsing listing pages and validating output structure.
- CI runs tests on every push/PR.

**Still Needed**

- Add coverage reporting using `pytest-cov`.
- Add static analysis/linting (e.g., `ruff` or `flake8`).
- Expand tests for:
  - Video detail pages
  - Pagination behavior
  - Error-handling paths

---

## 4. Repository & Addon Build Structure

**Goal**

Use a standardized `zips/` directory structure compatible with Kodi repo hosting.

**Completed**

- Existing build script (`build_repo_addons.py`) generates addon zips.
- GitHub Actions workflow (`build-addons.yml`) collects zips and uploads them as artifacts.

**Still Needed**

- Update build script to output zips in the structure:

  ```text
  zips/
    plugin.video.cumination/<version>/*.zip
    repository.dobbelina/<version>/*.zip
  addons.xml
  addons.xml.md5
  ```

- Update `repository.dobbelina/addon.xml` to use the new `datadir` layout.
- Commit the generated `addons.xml` and `.md5` to the repo during release builds.
- Optionally auto-publish zips via GitHub Releases.

---

## 5. Settings & User Experience Improvements

**Goal**

Make settings clearer, grouped logically, and easier for users to understand.

**Completed**

- Debug and advanced settings are already grouped near the bottom of the settings menu.
- Settings work and are readable.

**Still Needed**

- Rearrange settings into structured groups:
  - General
  - Playback
  - Network
  - Debug / Developer
- Add descriptive help text for all settings.
- Improve string organization inside `resources/language/`.

---

## 6. Code Cleanup & Organization

**Goal**

Modernize code patterns, simplify helpers, and improve maintainability.

**Completed**

- Strong central soup parser.
- Modularized site parsing helpers.
- Multiple Python 2 compatibility remnants already removed.
- DB query security fixed (parameterized queries).

**Still Needed**

- Add module-level docstrings to complex modules.
- Consolidate duplicate code patterns inside site modules.
- Create helper wrappers such as:
  - `add_directory_item()`
  - `build_listitem()`
- Gradually update formatting to modern Python (f-strings, simplified imports).

---

## 7. Documentation & Contributor Experience

**Goal**

Make the project easier to develop, test, and contribute to.

**Completed**

- Updated `README.md`.
- Updated `TESTING_GUIDE.md`.
- Updated `ROADMAP.md`.
- Documented dev workflows and testing methods.

**Still Needed**

- Add a dedicated `CONTRIBUTING.md` with:
  - Branching workflow
  - Coding standards
  - How to build zips
  - How to run tests
- Link all documentation sections clearly from `README.md`.

---

## Summary Table

| Area                      | Status                         |
| ------------------------- | ------------------------------ |
| BeautifulSoup Migration   | In Progress — Good Momentum    |
| HTTP Gateway Unification  | Not Started                    |
| Test Coverage / Linting   | Partially Complete             |
| Repository `zips/` Layout | Not Started                    |
| Settings UX               | In Progress                    |
| Code Cleanup              | In Progress                    |
| Documentation             | Partially Complete             |