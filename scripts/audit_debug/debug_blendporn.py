import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_blendporn = importlib.import_module("resources.lib.sites.blendporn")

def test_blendporn():
    print("Testing blendporn...")
    site_url = "https://www.blendporn.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}most-recent/"
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select(".well.well-sm, .video-item, .item")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a.video-link, a[href]")
        if link:
            name = utils.safe_get_attr(link, "title")
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = f"{site_url}channels/"
    cat_html = utils.getHtml(cat_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select(".col-sm-6, .category-item")
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_attr(cat.select_one("a"), "title")
        print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}search/{search_keyword}/"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select(".well.well-sm, .video-item, .item")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a.video-link, a[href]")
        first_video_url = link['href']
        if not first_video_url.startswith("http"):
            first_video_url = urllib_parse.urljoin(site_url, first_video_url)
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for source or embed
        source_match = re.search(r'<source\s+[^>]*src=["\']([^"\']+)["\']', video_html)
        if source_match:
            print(f"Found direct source: {source_match.group(1)}")
        else:
            embed_match = re.search(r'iframe scrolling="no" src="([^"]+)"', video_html)
            if embed_match:
                print(f"Found embed iframe: {embed_match.group(1)}")
            else:
                print("Source or embed not found")

import urllib.parse as urllib_parse
if __name__ == "__main__":
    test_blendporn()
