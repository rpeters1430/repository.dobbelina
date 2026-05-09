import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_beeg = importlib.import_module("resources.lib.sites.beeg")

def test_beeg():
    print("Testing beeg...")
    site_url = "https://store.externulls.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = "https://store.externulls.com/facts/tag?id=27173&limit=48&offset=0"
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    try:
        data = json.loads(html)
        print(f"Found {len(data)} videos")
        for v in data[:3]:
            # Get name from file data
            name = "Video"
            for d in v["file"]["data"]:
                if d["cd_column"] == "sf_name":
                    name = d["cd_value"]
            print(f"Video: {name} -> {v['file']['id']}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = site_url + 'tag/recommends?type=other&slug=index'
    cat_html = utils.getHtml(cat_url, site_url)
    try:
        cat_data = json.loads(cat_html)
        print(f"Found {len(cat_data)} categories")
        for cat in cat_data[:3]:
            print(f"Category: {cat.get('tg_name')}")
    except Exception as e:
        print(f"Error parsing Category JSON: {e}")

    # Test Playback Extraction
    if data:
        video_id = data[0]['file']['id']
        tag_id = 27173 # Default tag id
        print(f"\n--- Testing Playback Extraction for {video_id} ---")
        api_url = f"https://store.externulls.com/facts/file/{video_id}?tag={tag_id}"
        video_json = utils.getHtml(api_url, site_url)
        try:
            v_data = json.loads(video_json)
            hls = v_data.get("hls_resources") or v_data.get("file", {}).get("hls_resources")
            if hls:
                print(f"Found HLS resources: {list(hls.keys())}")
            else:
                print("No HLS resources found")
        except Exception as e:
            print(f"Error parsing Video JSON: {e}")

if __name__ == "__main__":
    test_beeg()
