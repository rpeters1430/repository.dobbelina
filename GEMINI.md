# Project Context: Dobbelina Repository (Cumination)

## Project Overview

This project hosts the **Dobbelina Repository** and its primary addon, **Cumination**. Cumination is a video addon for Kodi that aggregates content from various adult video sites.

The project is currently undergoing a significant **modernization effort** to improve reliability, maintainability, and code quality.

### Key Components

*   **`plugin.video.cumination/`**: The core video addon. It scrapes video sites and presents them in Kodi.
*   **`repository.dobbelina/`**: The repository addon that allows users to install and auto-update Cumination.
*   **`script.video.F4mProxy/`**: A helper script for handling specific stream types (F4M/HLS).
*   **`plugin.video.uwc/`**: Another video addon ("Ultimate Whitecream" legacy/fork).
*   **`build_repo_addons.py`**: Custom Python script to package addons into ZIP files and update the repository index (`addons.xml`).

### Technologies

*   **Language:** Python 3 (compatible with Kodi Matrix/Nexus/Omega).
*   **Framework:** Kodi Addon API (`xbmc`, `xbmcaddon`, `xbmcplugin`, etc.).
*   **Dependencies:** `BeautifulSoup4` (parsing), `requests` (networking), `resolveurl` (stream resolution).
*   **Testing:** `pytest`, `pytest-cov`.
*   **Linting:** `ruff`.
*   **CI/CD:** GitHub Actions.

## Status & Roadmap

**Current Phase:** Phase 1 - BeautifulSoup Migration & Phase 5 - Testing Infrastructure.

The primary goal is to migrate all site scrapers from fragile Regex patterns to robust **BeautifulSoup4** parsing.

*   **Tracking:** See `MODERNIZATION.md` for detailed roadmap and `PROJECT_STATUS.md` for recent progress.
*   **Known Issues:** See `KNOWN_ISSUES.md`.

## Development Workflow

### 1. Environment Setup

The project uses a `requirements-test.txt` for development dependencies.

```bash
# Install development dependencies
python -m pip install -r requirements-test.txt
```

### 2. Building

To build the addons into deployable ZIP files:

```bash
# Build all addons in the current directory
python build_repo_addons.py

# Build a specific addon
python build_repo_addons.py --addons plugin.video.cumination

# Build and update the repository index (addons.xml & md5)
python build_repo_addons.py --out . --update-index
```

### 3. Testing

Tests are crucial, especially when migrating sites. The project uses `pytest` with mocked Kodi modules.

```bash
# Run the full test suite
pytest

# Run tests for a specific site (e.g., AnyBunny)
pytest tests/sites/test_anybunny.py

# Run with coverage report
pytest --cov=plugin.video.cumination/resources/lib --cov-report=term-missing

# Lint the code
ruff check plugin.video.cumination/resources/lib/
```

**Key Testing Concepts:**
*   **Fixtures:** Store HTML samples in `tests/fixtures/` to test parsers against real site data without network requests.
*   **Mocks:** `tests/conftest.py` provides mocks for `xbmc`, `xbmcaddon`, etc., allowing code to run outside Kodi.

### 4. Migration Guide (Regex -> BeautifulSoup)

When migrating a site (e.g., `site_xyz.py`):

1.  **Analyze:** Look at the existing Regex logic in `plugin.video.cumination/resources/lib/sites/`.
2.  **Refactor:** Use `utils.parse_html()`, `utils.safe_get_attr()`, and `SoupSiteSpec` to rewrite the scraping logic.
3.  **Capture:** Save a sample HTML page from the site to `tests/fixtures/sites/site_xyz_list.html`.
4.  **Test:** Create a new test file `tests/sites/test_site_xyz.py` that asserts the parser correctly extracts titles, URLs, and thumbnails from the fixture.

## Directory Structure

*   `plugin.video.cumination/resources/lib/sites/`: Individual site scraper modules.
*   `plugin.video.cumination/resources/lib/utils.py`: Shared utilities and BeautifulSoup helpers.
*   `tests/`: Unit and integration tests.
*   `.github/workflows/`: CI automation.

## Conventions

*   **Code Style:** Follow PEP 8. Use `ruff` to catch errors (especially avoiding bare `except:`).
*   **Commits:** Use semantic prefixes (e.g., `feat:`, `fix:`, `refactor:`).
*   **Version Control:** `addon.xml` version must be bumped when releasing.
