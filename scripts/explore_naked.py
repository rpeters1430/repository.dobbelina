import sys
import json
from playwright.sync_api import sync_playwright

def run(url):
    print("[*] Exploring Naked.com: {}".format(url))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Capture all JSON API calls
        def handle_response(response):
            try:
                ct = response.headers.get("content-type", "").lower()
                if "application/json" in ct:
                    try:
                        data = response.json()
                        # If it looks like a model list
                        if "models" in str(data).lower() or "items" in str(data).lower():
                            print("\n[API FOUND] {}".format(response.url))
                            print(json.dumps(data, indent=2)[:500] + "...")
                    except:
                        pass
            except:
                pass

        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="load", timeout=60000)
            print("[*] Page loaded. Title: {}".format(page.title()))
            
            # Take a screenshot to see where search might be
            import os
            if not os.path.exists("results"): os.makedirs("results")
            page.screenshot(path="results/naked_home.png")
            
            # Try to find a search input or button
            search_selectors = ['input[type="search"]', 'input[placeholder*="Search"]', '.search-btn', 'i.fa-search', 'button:has-text("Search")']
            for s in search_selectors:
                try:
                    if page.locator(s).count() > 0:
                        print("[*] Found potential search element: {}".format(s))
                except:
                    continue
            
            # Wait for dynamic content
            page.wait_for_timeout(5000)
            
            # Scroll down to trigger more loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(5000)
            
        except Exception as e:
            print("[!] Error: {}".format(e))
        finally:
            browser.close()

if __name__ == "__main__":
    run("https://www.naked.com/")
