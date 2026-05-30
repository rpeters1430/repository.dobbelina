import asyncio
import json
from playwright.async_api import async_playwright


def _extract_initial_room_dossier(content):
    marker = "initialRoomDossier"
    marker_index = content.find(marker)
    if marker_index == -1:
        return None
    quote_start = content.find('"', marker_index)
    if quote_start == -1:
        return None
    escaped = False
    chars = []
    for ch in content[quote_start + 1 :]:
        if escaped:
            chars.append(ch)
            escaped = False
            continue
        if ch == "\\":
            chars.append(ch)
            escaped = True
            continue
        if ch == '"':
            return "".join(chars)
        chars.append(ch)
    return None


async def run():
    url = "https://chaturbate.com/minji_snow/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a mobile user agent as the addon does
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4"
        )
        page = await context.new_page()
        print(f"Visiting {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            content = await page.content()
            
            # Look for initialRoomDossier
            initial_room_dossier = _extract_initial_room_dossier(content)
            if initial_room_dossier:
                print("SUCCESS: Found initialRoomDossier")
                # In real code we use unicode-escape, here we just check if it looks right
                print("Dossier length:", len(initial_room_dossier))
                
                # Check for m3u8 links in the dossier or page
                if "hls_source" in content:
                    print("SUCCESS: Found 'hls_source' in page content")
                
                # Try to extract the HLS link if possible
                # The data is escaped JSON in a string
                try:
                    import codecs
                    raw_data = initial_room_dossier
                    decoded_data = codecs.decode(raw_data, 'unicode-escape')
                    dossier = json.loads(decoded_data)
                    hls_url = dossier.get("hls_source")
                    print(f"Extracted HLS URL: {hls_url}")
                except Exception as e:
                    print(f"Could not parse dossier JSON: {e}")
            else:
                print("FAILURE: initialRoomDossier NOT found")
                # Let's see what script tags ARE there
                scripts = await page.locator("script").all()
                print(f"Found {len(scripts)} script tags.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
