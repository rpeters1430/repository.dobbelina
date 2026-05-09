import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_beemtube = importlib.import_module("resources.lib.sites.beemtube")

def test_beemtube():
    print("Testing beemtube...")
    site_url = "https://beemtube.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}most-recent/"
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select(".video-block, .content")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a.video-link, a.thumb, a[href]")
        if link:
            name = utils.cleantext(utils.safe_get_text(item.select_one("strong")))
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = f"{site_url}categories/"
    cat_html = utils.getHtml(cat_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select(".content.categor, .category-item")
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_text(cat.select_one("strong"))
        print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}search?q={search_keyword}"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select(".video-block, .content")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a.video-link, a.thumb, a[href]")
        first_video_url = link['href']
        if not first_video_url.startswith("http"):
            first_video_url = urllib_parse.urljoin(site_url, first_video_url)
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for embedUrl
        match = re.search(r'"embedUrl":\s+"([^"]+)"', video_html)
        if match:
            print(f"Found embedUrl: {match.group(1)}")
            embed_html = utils.getHtml(match.group(1), first_video_url)
            pl_match = re.search(r'"playlist":\s+"([^"]+)"', embed_html)
            if pl_match:
                print(f"Found playlist JSON URL: {pl_match.group(1)}")
            else:
                print("Playlist JSON URL not found in embed")
        else:
            print("embedUrl not found")

import urllib.parse as urllib_parse
if __name__ == "__main__":
    test_beemtube()
