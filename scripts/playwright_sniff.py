import sys
from playwright.sync_api import sync_playwright


def run_sniff(url, wait_time=10):
    print(f"[*] Starting Playwright sniffer for: {url}")

    with sync_playwright() as playwright:
        # Launch the browser - headless=True for now to avoid GUI issues in terminal, change if needed
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        video_urls = []

        # Intercept responses
        def handle_response(response):
            # Capture video extensions
            if any(
                ext in response.url.lower()
                for ext in [".mp4", ".m3u8", ".ts", ".m4s", "manifest"]
            ):
                if response.url not in video_urls:
                    print(f"[>>] Found Video/Stream URL: {response.url}")
                    video_urls.append(response.url)

        page.on("response", handle_response)

        try:
            # Navigate to the target
            print("[*] Navigating...")
            page.goto(url, wait_until="load", timeout=60000)

            # Wait a bit for Cloudflare or lazy-loaders
            page.wait_for_timeout(5000)

            # Check for common play buttons to click
            play_selectors = [
                "button.vjs-big-play-button",
                ".play-button",
                "#play-button",
                ".vjs-play-control",
                "video",  # Sometimes just clicking the video element works
                ".play-icon",
            ]

            for selector in play_selectors:
                try:
                    if page.locator(selector).is_visible():
                        print(f"[*] Found play button ({selector}), clicking...")
                        page.click(selector)
                        break
                except:
                    continue

            print(f"[*] Waiting {wait_time}s for more network activity...")
            page.wait_for_timeout(wait_time * 1000)

        except Exception as e:
            print(f"[!] Error during execution: {e}")
        finally:
            print("\n[*] Finished.")
            browser.close()
            return video_urls


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://en.luxuretv.com/"
    run_sniff(target_url)
