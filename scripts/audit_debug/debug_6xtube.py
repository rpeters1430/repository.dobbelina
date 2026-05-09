import sys
import os
import re

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi # This will setup all Kodi mocks

from resources.lib import utils
import importlib
site_6xtube = importlib.import_module("resources.lib.sites.6xtube")

def test_6xtube():
    print("Testing 6xtube...")
    site_url = "http://www.6xtube.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url + "most-recent/", site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select("div.well.well-sm")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a.video-link[href]")
        if link:
            name = utils.safe_get_attr(link, "title", default="")
            videopage = utils.safe_get_attr(link, "href", default="")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = site_url + "channels/"
    cat_html = utils.getHtml(cat_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select(".col-sm-6")
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        link = cat.select_one("a[href][title]")
        if link:
            name = utils.safe_get_attr(link, "title", default="")
            print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}search/{search_keyword}/"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select("div.well.well-sm")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        first_video_url = items[0].select_one("a.video-link[href]")['href']
        if not first_video_url.startswith("http"):
            first_video_url = site_url.rstrip('/') + first_video_url
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Current logic in 6xtube.py
        source_match = re.search(r'<source\s+[^>]*src=["\']([^"\']+)["\']', video_html, re.IGNORECASE)
        if source_match:
            print(f"Found direct video source: {source_match.group(1)}")
        else:
            match = re.compile(r'iframe scrolling="no"\s*src="([^"]+)"', re.IGNORECASE | re.DOTALL).findall(video_html)
            if match:
                print(f"Found embed iframe: {match[0]}")
                embed_html = utils.getHtml(match[0], first_video_url)
                # Check if it has a video source
                video_src = re.search(r'(?:src:|source src=)\s*["\']([^"\']+)["\']', embed_html)
                if video_src:
                    print(f"Found video in embed: {video_src.group(1)}")
                else:
                    print("Could not find video in embed")
            else:
                print("Could not find video source or iframe")

if __name__ == "__main__":
    test_6xtube()
