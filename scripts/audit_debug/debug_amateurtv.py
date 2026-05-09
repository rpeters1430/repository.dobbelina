import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_amateurtv = importlib.import_module("resources.lib.sites.amateurtv")

def test_amateurtv():
    print("Testing amateurtv...")
    site_url = "https://www.amateur.tv/"
    
    # Test Listing (Females)
    print("\n--- Testing Listing (Females) ---")
    genre = "w"
    page = 1
    cam_url = f"{site_url}v3/readmodel/cache/filteredcams?genre=[%22{genre}%22]&page={page}"
    print(f"Fetching {cam_url}")
    
    html = utils.getHtml(cam_url, site_url)
    if not html:
        print("Failed to fetch cam list")
        return
    
    try:
        data = json.loads(html)
        cams = data.get("cams", {})
        nodes = cams.get("nodes") or []
        print(f"Found {len(nodes)} cams")
        for cam in nodes[:3]:
            model = cam.get("user")
            name = model.get("username")
            online = cam.get("online")
            print(f"Cam: {name} (Online: {online})")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")

    # Test Playback Extraction
    if nodes:
        first_cam = nodes[0].get("user").get("username")
        print(f"\n--- Testing Playback Extraction for {first_cam} ---")
        show_url = f"{site_url}v3/readmodel/show/{first_cam}/en"
        show_html = utils.getHtml(show_url, site_url)
        try:
            show_data = json.loads(show_html)
            vurls = show_data.get("videoTechnologies")
            if vurls:
                vurl = vurls.get("fmp4-hls") or vurls.get("hls") or vurls.get("hls-fmp4")
                if vurl:
                    print(f"Found HLS stream: {vurl}")
                else:
                    print(f"HLS stream not found in videoTechnologies: {vurls.keys()}")
            else:
                print("videoTechnologies not found in response")
        except Exception as e:
            print(f"Failed to parse Show JSON: {e}")

if __name__ == "__main__":
    test_amateurtv()
