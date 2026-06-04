---
name: kodi-test-patterns
description: Best practices for writing pytest suites with mocked Kodi modules and managing HTML fixtures for scraper testing. Use when writing tests for new sites or debugging existing scrapers.
---

# Kodi Test Patterns

This skill provides patterns for testing Kodi addons outside of the Kodi environment using mocks and fixtures.

## Testing Architecture

- **Pytest**: The primary testing framework.
- **Mocks**: `tests/conftest.py` automatically stubs `xbmc`, `xbmcgui`, etc.
- **Fixtures**: Saved HTML files in `tests/fixtures/` simulate site responses.

## Writing a Site Test

### 1. Capture Fixture
Save the HTML of the site list and video pages to `tests/fixtures/sites/<site>_list.html`.

### 2. Create Test File
Create `tests/sites/test_<site>.py`.

```python
import pytest
from plugin.video.cumination.resources.lib.sites import site_mysite
from tests.conftest import fixture_mapped_get_html

@pytest.fixture
def mock_mysite(monkeypatch):
    url_map = {
        'mysite.com/videos': 'sites/mysite_list.html',
        'mysite.com/watch': 'sites/mysite_video.html'
    }
    fixture_mapped_get_html(monkeypatch, site_mysite, url_map)

def test_mysite_index(mock_mysite):
    site = site_mysite.Mysite()
    # Call the method that scrapes the list
    site.INDEX({})
    
    # Assertions depend on how your site module adds items.
    # Usually you verify if items were added to the mock dispatcher.
```

## Common Assertions

- **Item Count**: Verify that the expected number of videos were parsed.
- **Metadata**: Check that titles, thumbnails, and URLs are extracted correctly.
- **Pagination**: Verify that the "Next Page" link was found and registered.

## Debugging Tests

- **Network Blocked**: The test suite blocks all live network requests by default. If a test fails with "Network access attempted", you must map the URL to a fixture in `url_map`.
- **Mocking Settings**: You can override addon settings in your test using `monkeypatch`:
  ```python
  monkeypatch.setattr('resources.lib.basics.addon.getSetting', lambda key: 'true')
  ```

## Running Tests

```bash
# Run all tests
pytest

# Run a specific site test
pytest tests/sites/test_mysite.py

# See log output
pytest -s tests/sites/test_mysite.py
```
