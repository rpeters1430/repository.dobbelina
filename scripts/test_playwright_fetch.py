import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from resources.lib.playwright_helper import fetch_with_playwright, take_screenshot
from bs4 import BeautifulSoup

def test_site(name, url, wait_for="networkidle"):
    print(f"\n--- Testing {name} ({url}) ---")
    try:
        html = fetch_with_playwright(url, wait_for=wait_for, timeout=60000)
        print(f"Successfully fetched {len(html)} bytes")
        
        # Take screenshot for debugging if Cloudflare detected
        if "Cloudflare" in html or "Just a moment" in html:
            screenshot_path = f"results/{name.lower().replace(' ', '_')}_cf.png"
            print(f"Cloudflare detected, taking screenshot to {screenshot_path}...")
            take_screenshot(url, screenshot_path)
        
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        print(f"Page Title: {title}")
        
        # Check for Cloudflare markers
        if "Cloudflare" in html or "Just a moment" in html:
            print("⚠️ Cloudflare challenge detected in HTML output!")
        else:
            print("✅ No obvious Cloudflare challenge in rendered HTML.")
            
        # Sample content check (luxuretv specific)
        if "luxuretv" in url:
            videos = soup.select('.content, [class*="content"]')
            print(f"Found {len(videos)} video items.")
        
        # Sample content check (missav specific)
        if "missav" in url:
            videos = soup.select("a[href][alt]")
            print(f"Found {len(videos)} video items.")

    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")

if __name__ == "__main__":
    test_site("LuxureTV", "https://en.luxuretv.com/")
    test_site("Miss AV", "https://missav.ws/en/new", wait_for="load")
    test_site("AnyBunny Search", "https://www.anybunny.com/search/videos/tits", wait_for="load")
