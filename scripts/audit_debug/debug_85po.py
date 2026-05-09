import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_85po = importlib.import_module("resources.lib.sites.85po")

def test_85po():
    print("Testing 85po...")
    site_url = "https://85po.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url + "en/latest-updates/", site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select('div.thumb.thumb_rel.item, div[class*="thumb"][class*="item"]')
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a")
        if link:
            name = utils.safe_get_attr(link, "title")
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = site_url + "en/tags/"
    cat_html = utils.getHtml(cat_url)
    cat_soup = utils.parse_html(cat_html)
    tags = cat_soup.select('a[href*="/en/tags/"]')
    print(f"Found {len(tags)} tags")
    for tag in tags[:3]:
        name = utils.safe_get_text(tag)
        print(f"Tag: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "japanese"
    search_url = f"{site_url}en/search/{search_keyword}/"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select('div.thumb.thumb_rel.item, div[class*="thumb"][class*="item"]')
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        first_video_url = items[0].select_one("a")['href']
        if not first_video_url.startswith("http"):
            first_video_url = site_url.rstrip('/') + first_video_url
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for kt_player
        if "kt_player('kt_player'" in video_html:
            print("kt_player detected")
            # Usually kt_player has video source in a script tag or via ajax
            # utils.VideoPlayer.play_from_kt_player handles this.
            # Let's see if we can see any video sources in the page
            video_sources = re.findall(r'video_url:\s*\'([^\']+)\'', video_html)
            if video_sources:
                print(f"Found kt_player video sources: {video_sources}")
            else:
                # Often it's base64 encoded or in a separate call
                print("kt_player source not directly visible, likely encoded.")
        else:
            print("kt_player not detected")

if __name__ == "__main__":
    test_85po()
