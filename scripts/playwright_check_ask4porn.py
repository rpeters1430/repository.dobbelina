from playwright.sync_api import sync_playwright
import time

def check_site():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        try:
            print("Navigating to https://ask4porn.cc/ ...")
            page.goto("https://ask4porn.cc/", timeout=60000)
            time.sleep(5) # Wait for CF
            print(f"Status: {page.title()}")
            content = page.content()
            print(f"Content length: {len(content)}")
            print(content[:1000])
            if "thumb-block" in content:
                print("Found thumb-block")
            else:
                print("thumb-block NOT found")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_site()
