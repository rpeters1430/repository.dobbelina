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

# Try to import stealth - it's optional but recommended
HAS_STEALTH = False
stealth_sync = None

try:
    from playwright_stealth import Stealth
    stealth_obj = Stealth()
    stealth_sync = stealth_obj.apply_stealth_sync
    HAS_STEALTH = True
except ImportError:
    pass

# Fallback if stealth not available
if not HAS_STEALTH:
    def stealth_sync(page):
        """Dummy stealth function if playwright-stealth not available."""
        pass


def fetch_with_playwright(
    url: str,
    wait_for: str = "networkidle",
    wait_for_selector: Optional[str] = None,
    timeout: int = 30000,
    headers: Optional[Dict[str, str]] = None,
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
            context.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )

        page = context.new_page()
        stealth_sync(page)

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
    full_page: bool = True,
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
        stealth_sync(page)

        try:
            page.goto(url, wait_until="networkidle")

            if wait_for_selector:
                page.wait_for_selector(wait_for_selector)

            page.screenshot(path=output_path, full_page=full_page)
            print(f"Screenshot saved to: {output_path}")

        finally:
            browser.close()


def fetch_with_playwright_and_network(
    url: str,
    wait_for: str = "networkidle",
    wait_for_selector: Optional[str] = None,
    timeout: int = 30000,
    headers: Optional[Dict[str, str]] = None,
) -> (str, list):
    """
    Fetch HTML content and network requests using Playwright (headless Chromium).
    """
    requests = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        )
        context.clear_cookies()

        if headers:
            context.set_extra_http_headers(headers)

        page = context.new_page()
        stealth_sync(page)

        def handle_request(request):
            requests.append({"url": request.url, "headers": request.headers})

        page.on("request", handle_request)

        try:
            page.goto(url, wait_until=wait_for, timeout=timeout)

            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=timeout)

            html = page.content()

            return html, requests

        finally:
            browser.close()


def sniff_video_url(
    url: str,
    play_selectors: Optional[list] = None,
    timeout: int = 30000,
    wait_after_click: int = 3000,
    debug: bool = False,
    exclude_domains: Optional[list] = None,
) -> Optional[str]:
    """
    Navigate to a URL, perform optional clicks (to trigger players),
    and sniff the network for the first video stream URL.

    Args:
        url: The video page URL
        play_selectors: List of CSS selectors to try clicking (play buttons, player containers)
        timeout: Navigation timeout in milliseconds
        wait_after_click: How long to wait after clicking for video to load (ms)
        debug: Print debug information
        exclude_domains: List of domains to ignore (e.g., ['ads.com', 'tracking.net'])

    Returns:
        The first video URL found, or None
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)

        found_url = [None]
        all_video_urls = []

        def handle_response(response):
            r_url = response.url.lower()
            if any(ext in r_url for ext in [".mp4", ".m3u8"]) and not any(x in r_url for x in ["/thumbs/", "/images/", ".jpg", ".png", "/thumb/", "/image/"]):
                
                # Check exclusion list
                if exclude_domains and any(domain.lower() in r_url for domain in exclude_domains):
                    return

                if response.url not in all_video_urls:
                    all_video_urls.append(response.url)
                    if not found_url[0]:
                        found_url[0] = response.url
                        if debug:
                            print(f"[sniff] Found video URL: {response.url}")

        page.on("response", handle_response)

        try:
            if debug:
                print(f"[sniff] Navigating to: {url}")
            page.goto(url, wait_until="load", timeout=timeout)
            page.wait_for_timeout(3000)  # Wait for JS to settle and lazy-loaded scripts

            if play_selectors:
                clicked = False
                for selector in play_selectors:
                    if found_url[0]:
                        break

                    try:
                        # Try main page first
                        elements = page.locator(selector)
                        count = elements.count()

                        if debug:
                            print(f"[sniff] Trying selector '{selector}': found {count} elements")

                        for i in range(count):
                            try:
                                elem = elements.nth(i)
                                if elem.is_visible(timeout=2000):
                                    if debug:
                                        print(f"[sniff] Clicking element {i} ({selector})...")
                                    elem.click(timeout=5000)
                                    clicked = True
                                    page.wait_for_timeout(wait_after_click)
                                    if found_url[0]:
                                        break
                            except Exception as e:
                                if debug:
                                    print(f"[sniff] Could not click element {i}: {e}")
                                continue

                        if clicked and found_url[0]:
                            break

                        # Try iframes if main page didn't work
                        if not clicked:
                            for frame_idx, frame in enumerate(page.frames):
                                if frame == page.main_frame:
                                    continue
                                try:
                                    target = frame.locator(selector).first
                                    if target.is_visible(timeout=1000):
                                        if debug:
                                            print(f"[sniff] Clicking in iframe {frame_idx}...")
                                        target.click()
                                        clicked = True
                                        page.wait_for_timeout(wait_after_click)
                                        break
                                except:
                                    continue

                        if found_url[0]:
                            break

                    except Exception as e:
                        if debug:
                            print(f"[sniff] Error with selector '{selector}': {e}")
                        continue

            # Wait a bit more for the request to fire
            max_wait_loops = 20
            for i in range(max_wait_loops):
                if found_url[0]:
                    break
                page.wait_for_timeout(500)

            if debug:
                print(f"[sniff] Total video URLs found: {len(all_video_urls)}")
                for vid_url in all_video_urls:
                    print(f"[sniff]   - {vid_url}")

            return found_url[0]

        finally:
            browser.close()


if __name__ == "__main__":
    # Quick test
    html = fetch_with_playwright("https://example.com")
    print(f"Fetched {len(html)} bytes")
    print("✅ Playwright helper is working!")
