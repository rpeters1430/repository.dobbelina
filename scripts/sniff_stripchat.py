
import sys
import time
from playwright.sync_api import sync_playwright

def run_sniff(url, wait_time=15):
    print(f"[*] Starting Stripchat sniffer for: {url}")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        streams = []

        def handle_response(response):
            if ".m3u8" in response.url or ".mp4" in response.url:
                if not any(x in response.url for x in ["/thumbs/", "/images/"]):
                    print(f"[>>] Found Potential Stream: {response.url}")
                    streams.append(response.url)

        page.on("response", handle_response)

        try:
            page.goto(url, wait_until="load", timeout=60000)
            print("[*] Page loaded, waiting for auto-play or clicking...")
            page.wait_for_timeout(5000)
            
            # Common cam site play button selectors
            play_selectors = ["video", ".vjs-big-play-button", ".play-button", "pjsdiv"]
            for selector in play_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        print(f"[*] Clicking {selector}...")
                        page.locator(selector).first.click()
                        page.wait_for_timeout(2000)
                except:
                    continue

            print(f"[*] Waiting {wait_time}s for network activity...")
            page.wait_for_timeout(wait_time * 1000)

        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            browser.close()
            
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://stripchat.com/D-O-L-L-Y-M-A-U"
    run_sniff(target)
