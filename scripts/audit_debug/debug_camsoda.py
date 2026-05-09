import sys
import os
import re
import importlib
import json
import random

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_camsoda = importlib.import_module("resources.lib.sites.camsoda")

def test_camsoda():
    print("Testing camsoda...")
    site_url = "https://www.camsoda.com"
    
    # Test Listing (Female)
    print("\n--- Testing Listing (Female) ---")
    list_url = f"{site_url}/api/v1/browse/react?gender-hide=c,t,m&p=1"
    
    data = utils._getHtml(list_url)
    try:
        jd = json.loads(data)
        camgirls = jd.get("userList", [])
        print(f"Found {len(camgirls)} cams")
        for cam in camgirls[:3]:
            print(f"Cam: {cam.get('username')} (Status: {cam.get('status')})")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Data snippet: {str(data)[:200]}")

    # Test Playback Extraction
    if camgirls:
        username = camgirls[0].get("username")
        print(f"\n--- Testing Playback Extraction for {username} ---")
        video_api_url = f"{site_url}/api/v1/chat/react/{username}?username=guest_{random.randrange(100, 55555)}"
        try:
            response_data = utils._getHtml(video_api_url)
            if "cf-browser-verification" in response_data or "cloudflare" in response_data.lower():
                print("Cloudflare challenge detected on chat API. Playback test skipped.")
            else:
                response = json.loads(response_data)
                data = response.get("stream")
                if data and len(data.get("edge_servers", [])) > 0:
                    videourl = (
                        "https://"
                        + random.choice(data["edge_servers"])
                        + "/"
                        + data["stream_name"]
                        + "_v1/index.ll.m3u8?token="
                        + data["token"]
                    )
                    print(f"Found stream URL: {videourl}")
                else:
                    print(f"Model Offline or Error: {response.get('error')}")
        except Exception as e:
            print(f"Error in playback request: {e}")

if __name__ == "__main__":
    test_camsoda()
