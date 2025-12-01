"""
Playwright helper utilities for testing JavaScript-heavy sites.

This module provides utilities for testing sites that require JavaScript execution,
such as those with:
- Dynamic content loading
- Cloudflare protection
- React/Vue/Angular frameworks
- Lazy-loaded images

Usage:
    from tests.utils.playwright_helper import fetch_with_playwright

    html = fetch_with_playwright('https://example.com/videos')
    soup = BeautifulSoup(html, 'html.parser')
"""

from playwright.sync_api import sync_playwright
from typing import Optional, Dict


def fetch_with_playwright(
    url: str,
    wait_for: str = 'networkidle',
    wait_for_selector: Optional[str] = None,
    timeout: int = 30000,
    headers: Optional[Dict[str, str]] = None
) -> str:
    """
    Fetch HTML content using Playwright (headless Chromium).

    Args:
        url: The URL to fetch
        wait_for: When to consider navigation complete ('networkidle', 'load', 'domcontentloaded')
        wait_for_selector: Optional CSS selector to wait for before returning
        timeout: Timeout in milliseconds (default: 30s)
        headers: Optional HTTP headers dict

    Returns:
        str: The fully-rendered HTML content

    Example:
        >>> html = fetch_with_playwright(
        ...     'https://example.com/videos',
        ...     wait_for_selector='.video-item'
        ... )
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> videos = soup.select('.video-item')
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Set headers if provided
        if headers:
            context.set_extra_http_headers(headers)
        else:
            # Default user agent
            context.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

        page = context.new_page()

        try:
            # Navigate to the URL
            page.goto(url, wait_until=wait_for, timeout=timeout)

            # Wait for specific selector if provided
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=timeout)

            # Get the fully-rendered HTML
            html = page.content()

            return html

        finally:
            browser.close()


def take_screenshot(
    url: str,
    output_path: str,
    wait_for_selector: Optional[str] = None,
    full_page: bool = True
) -> None:
    """
    Take a screenshot of a page (useful for debugging failed tests).

    Args:
        url: The URL to screenshot
        output_path: Path to save the screenshot (e.g., 'debug.png')
        wait_for_selector: Optional CSS selector to wait for
        full_page: Whether to capture the full scrollable page

    Example:
        >>> take_screenshot(
        ...     'https://example.com/videos',
        ...     'tests/debug/videos_page.png',
        ...     wait_for_selector='.video-item'
        ... )
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until='networkidle')

            if wait_for_selector:
                page.wait_for_selector(wait_for_selector)

            page.screenshot(path=output_path, full_page=full_page)
            print(f"Screenshot saved to: {output_path}")

        finally:
            browser.close()


if __name__ == '__main__':
    # Quick test
    html = fetch_with_playwright('https://example.com')
    print(f"Fetched {len(html)} bytes")
    print("✅ Playwright helper is working!")
