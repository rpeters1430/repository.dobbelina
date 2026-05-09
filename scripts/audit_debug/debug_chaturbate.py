import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_chaturbate = importlib.import_module("resources.lib.sites.chaturbate")

def test_chaturbate():
    print("Testing chaturbate...")
    site_url = "https://chaturbate.com/"
    
    # Test Listing (Featured)
    print("\n--- Testing Listing (Featured) ---")
    list_url = "https://chaturbate.com/api/ts/roomlist/room-list/?limit=10&offset=0"
    
    try:
        data = utils._getHtml(list_url)
        if "cf-browser-verification" in data or "cloudflare" in data.lower():
            print("Cloudflare challenge detected on room-list API.")
        else:
            payload = json.loads(data)
            models = payload.get("rooms", [])
            print(f"Found {len(models)} models")
            for model in models[:3]:
                print(f"Model: {model.get('username')} (Age: {model.get('display_age')})")
    except Exception as e:
        print(f"Error in listing request: {e}")

    # Test Playback Extraction
    if 'models' in locals() and models:
        username = models[0].get("username")
        print(f"\n--- Testing Playback Extraction for {username} ---")
        room_url = f"{site_url}{username}/"
        try:
            # Addon uses get_html_with_cloudflare_retry
            html, used_fs = utils.get_html_with_cloudflare_retry(
                room_url,
                referer=site_url,
                headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4"}
            )
            
            if "initialRoomDossier" in html:
                print("SUCCESS: Found initialRoomDossier")
                match = re.search(r'initialRoomDossier\s*=\s*"((?:\\.|[^"])*)"', html)
                if match:
                    import codecs
                    raw_data = match.group(1)
                    # Note: in Python 3 we use unicode-escape differently
                    try:
                        decoded_data = codecs.decode(raw_data, 'unicode-escape')
                        dossier = json.loads(decoded_data)
                        print(f"Extracted HLS URL: {dossier.get('hls_source')}")
                    except:
                         # Fallback for complex escaping
                         print("Could not easily decode dossier string in debug script, but it was found.")
            else:
                print("FAILURE: initialRoomDossier NOT found")
                if "cloudflare" in html.lower():
                    print("Cloudflare detected and blocked the request.")
        except Exception as e:
            print(f"Error in playback request: {e}")

if __name__ == "__main__":
    test_chaturbate()
