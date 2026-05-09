import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_avple = importlib.import_module("resources.lib.sites.avple")

def test_avple():
    print("Testing avple...")
    site_url = "https://avple.tv/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    try:
        soup = utils.parse_html(html)
        script_tag = soup.select_one('script#__NEXT_DATA__')
        if script_tag:
            data = json.loads(script_tag.string)
            props = data.get("props", {}).get("pageProps", {})
            indexListObj = props.get("indexListObj", {})
            print(f"Found {len(indexListObj)} groups of videos")
            for key, videos in indexListObj.items():
                if isinstance(videos, list):
                    print(f"Group {key}: {len(videos)} videos")
                    for v in videos[:3]:
                        print(f"Video: {v.get('title')} -> {v.get('_id')}")
        else:
            print("script#__NEXT_DATA__ not found")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}search?page=1&sort=date&key={search_keyword}"
    search_html = utils.getHtml(search_url, site_url)
    if search_html:
        search_soup = utils.parse_html(search_html)
        search_script = search_soup.select_one('script#__NEXT_DATA__')
        if search_script:
            search_data = json.loads(search_script.string)
            search_videos = search_data.get("props", {}).get("pageProps", {}).get("indexListObj", {}).get("obj", [])
            print(f"Found {len(search_videos)} search results")
        else:
            print("Search JSON not found")

    # Test Playback Extraction
    # If we have a video ID from listing
    video_id = "670498ec856b3594b297b41e" # Sample ID if listing fails or to be sure
    print(f"\n--- Testing Playback Extraction for {video_id} ---")
    video_url = f"{site_url}video/{video_id}"
    video_html = utils.getHtml(video_url, site_url)
    if video_html:
        match = re.search(r"source\s*=\s*'([^']+)", video_html)
        if match:
            print(f"Found video source: {match.group(1)}")
        else:
            print("Video source not found in script tags")

if __name__ == "__main__":
    test_avple()
