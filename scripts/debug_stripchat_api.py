import sys
import json
from playwright.sync_api import sync_playwright

def run(url):
    print("[*] Analyzing API traffic for: {}".format(url))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a mobile User-Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        def handle_response(response):
            try:
                ct = response.headers.get("content-type", "").lower()
                if "application/json" in ct:
                    try:
                        data = response.json()
                        # Look for stream info in JSON
                        if "stream" in str(data).lower() or "hls" in str(data).lower():
                            print("\n[API JSON] {}".format(response.url))
                            print(json.dumps(data, indent=2)[:1000])
                    except:
                        pass
                
                if ".m3u8" in response.url:
                    print("\n[M3U8] {}".format(response.url))
                    try:
                        text = response.text()
                        if "#EXT-X-MOUFLON" in text:
                            print(" >> Contains MOUFLON (Proprietary)")
                        else:
                            print(" >> Standard HLS Manifest!")
                            print(text[:500])
                    except:
                        pass
            except:
                pass

        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(10000)
        finally:
            browser.close()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://stripchat.com/RussianWoman"
    run(target)
