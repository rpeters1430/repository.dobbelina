import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_awmnet = importlib.import_module("resources.lib.sites.awmnet")

def test_awmnet():
    print("Testing awmnet (4tube)...")
    site_url = "https://www.4tube.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}new?pricing=free"
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select('a.item-link, a[class*="item-link"]')
    print(f"Found {len(items)} items")
    for item in items[:3]:
        name = utils.safe_get_attr(item, "title")
        videopage = utils.safe_get_attr(item, "href")
        print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_html = utils.getHtml(site_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select('div.card.group, div[class*="card"][class*="group"]')
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_attr(cat.select_one("a"), "title")
        print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}search/?s={search_keyword}&pricing=free"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select('a.item-link, a[class*="item-link"]')
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        first_video_url = items[0]['href']
        if not first_video_url.startswith("http"):
            first_video_url = site_url.rstrip('/') + first_video_url
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for source or embed
        if 'license_code: \'' in video_html:
            print("license_code detected (KVS site)")
        elif 'video_url:' in video_html:
            print("video_url detected")
        else:
            print("Neither license_code nor video_url found")

if __name__ == "__main__":
    test_awmnet()
