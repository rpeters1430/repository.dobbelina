#!/usr/bin/env python3
"""Debug anybunny video playback with Playwright."""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


def debug_anybunny_video(video_url: str):
    """Debug anybunny video page and try to extract video stream."""
    print(f"[*] Debugging anybunny video: {video_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible for debugging
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)

        video_urls = []
        requests = []

        def handle_response(response):
            r_url = response.url.lower()
            # Look for video files
            if any(ext in r_url for ext in [".mp4", ".m3u8", ".ts", ".m4s"]):
                if "/thumb" not in r_url and "/image" not in r_url and ".jpg" not in r_url:
                    print(f"[+] VIDEO URL: {response.url}")
                    video_urls.append(response.url)

        def handle_request(request):
            requests.append(request.url)

        page.on("response", handle_response)
        page.on("request", handle_request)

        try:
            print("[*] Navigating to page...")
            page.goto(video_url, wait_until="load", timeout=60000)

            print("[*] Waiting for page to load...")
            page.wait_for_timeout(3000)

            # Get page HTML to inspect
            html = page.content()

            # Look for video player elements
            print("\n[*] Looking for player elements...")

            # Check for pjsdiv (custom player)
            pjsdiv_count = page.locator('pjsdiv').count()
            print(f"  - Found {pjsdiv_count} pjsdiv elements")

            # Check for standard video tags
            video_count = page.locator('video').count()
            print(f"  - Found {video_count} video elements")

            # Check for iframes
            iframe_count = page.locator('iframe').count()
            print(f"  - Found {iframe_count} iframe elements")

            # Look for play buttons
            play_selectors = [
                "pjsdiv",
                "video",
                "button.vjs-big-play-button",
                ".play-button",
                "#play-button",
                ".vjs-play-control",
                ".play-icon",
                "[class*='play']",
                "[id*='play']"
            ]

            print("\n[*] Trying to find and click play button...")
            clicked = False

            for selector in play_selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    if count > 0:
                        print(f"  - Found {count} elements matching: {selector}")
                        # Try to click the first visible one
                        for i in range(count):
                            try:
                                elem = elements.nth(i)
                                if elem.is_visible(timeout=1000):
                                    print(f"    - Clicking element {i}...")
                                    elem.click(timeout=5000)
                                    clicked = True
                                    page.wait_for_timeout(2000)
                                    break
                            except Exception as e:
                                print(f"    - Could not click element {i}: {e}")
                                continue
                        if clicked:
                            break
                except Exception as e:
                    continue

            if not clicked:
                print("  - No clickable play button found, trying iframes...")
                # Try clicking in iframes
                for i, frame in enumerate(page.frames):
                    if frame == page.main_frame:
                        continue
                    print(f"  - Checking iframe {i}...")
                    for selector in play_selectors[:5]:  # Try top selectors in iframes
                        try:
                            elem = frame.locator(selector).first
                            if elem.is_visible(timeout=1000):
                                print(f"    - Clicking {selector} in iframe {i}...")
                                elem.click()
                                clicked = True
                                page.wait_for_timeout(2000)
                                break
                        except:
                            continue
                    if clicked:
                        break

            # Wait for video to load
            print("\n[*] Waiting for video to load...")
            page.wait_for_timeout(5000)

            # Try to extract video source from HTML
            print("\n[*] Searching HTML for video sources...")

            # Look for source tags
            source_match = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if source_match:
                print(f"  - Found <source> tags: {len(source_match)}")
                for src in source_match:
                    if any(ext in src.lower() for ext in ['.mp4', '.m3u8']):
                        print(f"    - {src}")

            # Look for video URLs in scripts
            video_match = re.findall(r'https?://[^\s\'"]+\.(?:mp4|m3u8)', html, re.IGNORECASE)
            if video_match:
                print(f"  - Found video URLs in HTML: {len(set(video_match))}")
                for url in set(video_match):
                    print(f"    - {url}")

            print("\n[*] All captured video URLs:")
            if video_urls:
                for url in video_urls:
                    print(f"  - {url}")
            else:
                print("  - None captured")

            print("\n[*] Press Enter to close browser...")
            input()

        except Exception as e:
            print(f"[!] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

        return video_urls


if __name__ == "__main__":
    # Test with a sample anybunny video URL
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        # You'll need to provide a real video URL
        test_url = input("Enter anybunny video URL: ")

    if test_url:
        results = debug_anybunny_video(test_url)
        print(f"\n[*] Final results: {len(results)} video URLs found")
