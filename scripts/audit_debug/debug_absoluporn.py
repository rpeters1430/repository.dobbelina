import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_absoluporn = importlib.import_module("resources.lib.sites.absoluporn")

def test_absoluporn():
    print("Testing absoluporn...")
    site_url = "http://www.absoluporn.com/en"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}/wall-date-1.html"
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select(".thumb-main-titre, .thumb-block")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a[href][title]") or item.find_parent("a") or item.select_one("a")
        if link:
            name = utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_html = utils.getHtml(site_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    cat_links = cat_soup.select('a.link1b[href*="wall-"]')
    print(f"Found {len(cat_links)} categories/tags")
    for link in cat_links[:3]:
        print(f"Category: {utils.safe_get_text(link)}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}/search-{search_keyword}-1.html"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select(".thumb-main-titre, .thumb-block")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a[href][title]") or items[0].find_parent("a") or items[0].select_one("a")
        first_video_url = link['href']
        if first_video_url.startswith(".."):
            first_video_url = first_video_url[2:]
        if not first_video_url.startswith("http"):
            first_video_url = "http://www.absoluporn.com" + first_video_url
            
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for source tag
        source_match = re.search(r'<source\s*src="([^"]+)', video_html, re.IGNORECASE)
        if source_match:
            print(f"Found direct source: {source_match.group(1)}")
        else:
            print("Direct source not found, checking JS variables...")
            servervideo = re.search("servervideo = '([^']+)'", video_html)
            if servervideo:
                print(f"servervideo: {servervideo.group(1)}")
            else:
                print("JS variables not found")

if __name__ == "__main__":
    test_absoluporn()
