import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_cam4 = importlib.import_module("resources.lib.sites.cam4")

def test_cam4():
    print("Testing cam4...")
    site_url = "https://www.cam4.com/"
    
    # Test Listing (Female)
    print("\n--- Testing Listing (Female) ---")
    gender_params = "&gender=female&broadcastType=female_group&broadcastType=solo&broadcastType=male_female_group"
    list_url = f"{site_url}api/directoryCams?directoryJson=true&online=true&url=true&orderBy=VIDEO_QUALITY{gender_params}&page=1&resultsPerPage=60"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML%2C like Gecko) Mobile/15E148"
    }
    
    data = utils._getHtml(list_url, headers=headers)
    try:
        payload = json.loads(data)
        cams = payload.get("users", [])
        print(f"Found {len(cams)} cams")
        for cam in cams[:3]:
            print(f"Cam: {cam.get('username')} (HD: {cam.get('hdStream')})")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Data snippet: {str(data)[:200]}")

    # Test Playback Extraction
    if cams:
        username = cams[0].get("username")
        print(f"\n--- Testing Playback Extraction for {username} ---")
        video_info_url = f"{site_url}rest/v1.0/profile/{username}/streamInfo"
        try:
            response = utils._getHtml(video_info_url)
            if "cf-browser-verification" in response or "cloudflare" in response.lower():
                print("Cloudflare challenge detected on streamInfo. Playback test skipped.")
            else:
                video_json = json.loads(response)
                video_url = video_json.get("cdnURL")
                print(f"Found stream URL: {video_url}")
        except Exception as e:
            print(f"Error in playback request: {e}")

if __name__ == "__main__":
    test_cam4()
