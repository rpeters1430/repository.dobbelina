import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_allclassic = importlib.import_module("resources.lib.sites.allclassic")

def test_allclassic():
    print("Testing allclassic...")
    site_url = "https://allclassic.porn/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url + "page/1/", site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select("a.th.item[href]")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        name = utils.cleantext(utils.safe_get_text(item.select_one(".th-description"), default=""))
        if not name:
            name = utils.cleantext(utils.safe_get_attr(item, "title", default=""))
        videopage = utils.safe_get_attr(item, "href")
        print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = site_url + "categories/"
    cat_html = utils.getHtml(cat_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select("a.th[href]")
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_attr(cat.select_one("img"), "alt", default="")
        print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "classic"
    search_url = f"{site_url}search/{search_keyword}/"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select("a.th.item[href]")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        first_video_url = items[0]['href']
        if not first_video_url.startswith("http"):
            first_video_url = site_url.rstrip('/') + first_video_url
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for kt_player
        if "kt_player('kt_player'" in video_html:
            print("kt_player detected")
            video_sources = re.findall(r'video_url:\s*\'([^\']+)\'', video_html)
            if video_sources:
                print(f"Found kt_player video sources: {video_sources}")
        else:
            print("kt_player not detected")

if __name__ == "__main__":
    test_allclassic()
