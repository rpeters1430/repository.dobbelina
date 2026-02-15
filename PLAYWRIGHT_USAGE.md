# Playwright Usage Guide

## Overview

Playwright is now installed and configured for testing JavaScript-heavy sites. This is useful for sites that:
- Load content dynamically with JavaScript
- Use Cloudflare protection
- Built with React/Vue/Angular frameworks
- Have lazy-loaded images or infinite scroll

## Installation Status

✅ **COMPLETE** - All dependencies installed and tested

- Playwright Python API: v1.56.0
- Chromium browser: Installed (Ubuntu 24.04 fallback for 25.10)
- System dependencies: Installed
- Integration test: Passed

## VS Code MCP Profiles

Playwright MCP is configured for this workspace in [.vscode/mcp.json](.vscode/mcp.json) with two server profiles:

- `playwright`: Headless browser mode (default for automation)
- `playwright-headed`: Headed browser mode (useful for visual debugging)

If a new profile does not appear immediately in VS Code:

1. Run `Developer: Reload Window`
2. Reconnect/restart the MCP server session

## Quick Start

### Using the Helper Function

```python
from tests.utils.playwright_helper import fetch_with_playwright
from bs4 import BeautifulSoup

# Fetch HTML with JavaScript rendered
html = fetch_with_playwright('https://example-site.com/videos')

# Parse with BeautifulSoup as usual
soup = BeautifulSoup(html, 'html.parser')
videos = soup.select('.video-item')
```

### Wait for Specific Content

```python
# Wait for videos to load before returning HTML
html = fetch_with_playwright(
    'https://example-site.com/videos',
    wait_for_selector='.video-item',  # Wait for this selector
    timeout=30000  # 30 second timeout
)
```

### Custom Headers

```python
html = fetch_with_playwright(
    'https://example-site.com/videos',
    headers={
        'User-Agent': 'Custom User Agent',
        'Referer': 'https://example.com'
    }
)
```

### Debug with Screenshots

```python
from tests.utils.playwright_helper import take_screenshot

# Take a screenshot for debugging
take_screenshot(
    'https://example-site.com/videos',
    'tests/debug/site_screenshot.png',
    wait_for_selector='.video-item',
    full_page=True
)
```

## Example: Testing a JavaScript Site

Here's how to create a test for a site that loads content via JavaScript:

```python
# tests/sites/test_javascript_site.py
import pytest
from tests.utils.playwright_helper import fetch_with_playwright
from bs4 import BeautifulSoup


def test_javascript_site_list():
    """Test a site that loads videos via JavaScript."""

    # Fetch with Playwright instead of utils.getHtml()
    html = fetch_with_playwright(
        'https://example-site.com/videos',
        wait_for_selector='.video-item',  # Wait for videos to load
        timeout=30000
    )

    # Parse with BeautifulSoup as usual
    soup = BeautifulSoup(html, 'html.parser')
    videos = soup.select('.video-item')

    # Assertions
    assert len(videos) > 0, "Should find video items"

    first_video = videos[0]
    title = first_video.select_one('.title')
    assert title is not None, "Should have title"
```

## When to Use Playwright vs Regular HTTP

### Use Playwright When:
- ✅ Site loads content via JavaScript/AJAX
- ✅ Site has Cloudflare or similar protection
- ✅ Content appears only after page interaction
- ✅ Images are lazy-loaded
- ✅ Site uses infinite scroll
- ✅ Site requires cookies from browser execution

### Use Regular HTTP (utils.getHtml) When:
- ✅ Site returns complete HTML in response
- ✅ No JavaScript required for content
- ✅ Faster test execution needed
- ✅ Site is API-based

## Performance Notes

Playwright is slower than regular HTTP requests:
- HTTP request: ~100-500ms
- Playwright request: ~1-3 seconds

Use Playwright only when necessary. For most sites in this project, regular HTTP + BeautifulSoup is sufficient.

## Integration with Existing Sites

If you need to add Playwright to an existing site module:

```python
# In plugin.video.cumination/resources/lib/sites/example.py

from resources.lib.adultsite import AdultSite
from resources.lib import utils

# For development/testing only - don't include in production
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

site = AdultSite('example', '[COLOR hotpink]Example[/COLOR]',
                 'https://example.com/', 'example.png', 'example')

@site.register()
def List(url):
    # Try Playwright first if available (for testing)
    if PLAYWRIGHT_AVAILABLE:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle')
            listhtml = page.content()
            browser.close()
    else:
        # Fallback to regular HTTP
        listhtml = utils.getHtml(url)

    soup = utils.parse_html(listhtml)
    # ... rest of parsing logic
```

## Testing the Installation

Run this command to verify everything works:

```bash
source venv/bin/activate
python tests/utils/playwright_helper.py
```

Expected output:
```
Fetched 528 bytes
✅ Playwright helper is working!
```

## Troubleshooting

### Browser Won't Launch
```bash
# Reinstall browsers
source venv/bin/activate
playwright install chromium
```

### Missing System Dependencies
```bash
# Check what's needed
source venv/bin/activate
playwright install-deps chromium --dry-run
```

### Timeout Errors
Increase the timeout parameter:
```python
html = fetch_with_playwright(url, timeout=60000)  # 60 seconds
```

## Resources

- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [Playwright API Reference](https://playwright.dev/python/docs/api/class-playwright)
- Helper: `tests/utils/playwright_helper.py`
