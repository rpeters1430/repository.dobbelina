
from playwright.sync_api import sync_playwright

def run(url):
    print("[*] Deep analysis of Naked.com: {}".format(url))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            # Log all URLs that look like they might contain data
            r_url = response.url.lower()
            if any(x in r_url for x in ["api", "data", "list", "models", "get", "query"]):
                print("[URL] {}".format(response.url))

        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="load", timeout=60000)
            page.wait_for_timeout(5000)
            
            # Find all text on page to see if models are listed
            body_text = page.evaluate("document.body.innerText")
            print("[*] Body text length: {}".format(len(body_text)))
            
            # Check for specific model data in scripts
            scripts = page.locator("script").all_inner_texts()
            print("[*] Found {} script tags".format(len(scripts)))
            for i, s in enumerate(scripts):
                if "models" in s.lower():
                    print("[*] Script {} contains 'models'".format(i))
                    print(s[:200] + "...")

        except Exception as e:
            print("[!] Error: {}".format(e))
        finally:
            browser.close()

if __name__ == "__main__":
    run("https://www.naked.com/live/girls/")
