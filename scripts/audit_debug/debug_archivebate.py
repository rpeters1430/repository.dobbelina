import sys
import os
import re
import importlib
import json
import html as htmlmod

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_archivebate = importlib.import_module("resources.lib.sites.archivebate")

def test_archivebate():
    print("Testing archivebate...")
    site_url = "https://archivebate.com/"
    
    # Test Listing (of first platform)
    print("\n--- Testing Listing (Chaturbate) ---")
    platform_url = "https://archivebate.com/platform/Y2hhdHVyYmF0ZQ=="
    
    # Use the actual function from the module
    fragment, next_url = site_archivebate._livewire_list(platform_url)
    
    if not fragment:
        print("Failed to fetch Livewire fragment")
        return
    
    soup = utils.parse_html(fragment)
    items = soup.select("section.video_item")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        performer = item.select_one('a[href*="/profile/"]')
        name = performer.text.strip() if performer else "Video"
        link = item.select_one('a[href*="/watch/"]')
        watch_url = link["href"]
        print(f"Video: {name} -> {watch_url}")

    # Test Playback Extraction
    if items:
        first_video_url = items[0].select_one('a[href*="/watch/"]')["href"]
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        soup_video = utils.parse_html(video_html)
        iframe = soup_video.select_one("iframe.video-frame")
        if iframe and iframe.get("src"):
            print(f"Found iframe src: {iframe['src']}")
        else:
            print("Iframe not found")

if __name__ == "__main__":
    test_archivebate()
