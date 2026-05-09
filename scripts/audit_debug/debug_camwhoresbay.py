import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_camwhoresbay = importlib.import_module("resources.lib.sites.camwhoresbay")

def test_camwhoresbay():
    print("Testing camwhoresbay...")
    site_url = "https://www.camwhoresbay.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}latest-updates/"
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select(".video-item")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a[href]")
        if link:
            name = utils.safe_get_attr(link, "title")
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = f"{site_url}categories/"
    cat_html = utils.getHtml(cat_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select("a.item[href], div.item a[href]")
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_attr(cat, "title")
        print(f"Category: {name}")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a[href]")
        first_video_url = link['href']
        if not first_video_url.startswith("http"):
            from six.moves import urllib_parse
            first_video_url = urllib_parse.urljoin(site_url, first_video_url)
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        if "kt_player('kt_player'" in video_html:
            print("Found kt_player script")
        else:
            print("kt_player script NOT found")

if __name__ == "__main__":
    test_camwhoresbay()
