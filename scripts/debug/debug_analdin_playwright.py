
import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Try to mimic the environment where it might fail
        browser = await p.chromium.launch(headless=True)
        # Use a generic User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = "https://www.analdin.com/latest-updates/"
        print(f"Visiting {url}...")
        
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            print(f"Status: {response.status}, Final URL: {page.url}")
            
            # Take a screenshot
            await page.screenshot(path="analdin_debug.png")
            
            # Check for Cloudflare-like elements
            content = await page.content()
            if "just a moment" in content.lower() or "checking your browser" in content.lower():
                print("Detected challenge page in rendered HTML")
            
            # Look for video items using the site module's selectors
            items = await page.eval_on_selector_all(
                ".list-videos .item, .list-videos .item-video, .list-videos .video-item, .item", 
                "elements => elements.length"
            )
            print(f"Found {items} items using '.list-videos .item'")
            
            # Look for video links directly
            links = await page.eval_on_selector_all(
                "a[href*='/videos/']",
                "elements => elements.length"
            )
            print(f"Found {links} links matching 'a[href*=\"/videos/\"]'")
            
            if items == 0 and links > 0:
                print("Selector '.list-videos .item' failed but direct links found!")
                # Print some example link parents to see what classes they have
                parents = await page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a[href*="/videos/"]')).slice(0, 5);
                    return links.map(a => {
                        let p = a.parentElement;
                        let trace = [];
                        for (let i = 0; i < 3; i++) {
                            if (p) {
                                trace.push({tag: p.tagName, class: p.className, id: p.id});
                                p = p.parentElement;
                            }
                        }
                        return {href: a.href, trace: trace};
                    });
                }""")
                for p in parents:
                    print(f"Link: {p['href']}")
                    for t in p['trace']:
                        print(f"  Parent: {t['tag']} class='{t['class']}' id='{t['id']}'")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
