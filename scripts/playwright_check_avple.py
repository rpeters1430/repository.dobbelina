from playwright.sync_api import sync_playwright
import time

def check_site():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = context.new_page()
        try:
            print("Navigating to https://avple.tv/ ...")
            page.goto("https://avple.tv/", timeout=60000)
            time.sleep(10) # Wait for CF
            print(f"Title: {page.title()}")
            content = page.content()
            if "__NEXT_DATA__" in content:
                print("Found __NEXT_DATA__")
            else:
                print("__NEXT_DATA__ NOT found")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_site()
