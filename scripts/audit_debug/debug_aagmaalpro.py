import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_aagmaalpro = importlib.import_module("resources.lib.sites.aagmaalpro")

def test_aagmaalpro():
    print("Testing aagmaalpro...")
    site_url = "https://aagmaal.farm/" # Note: site.url in code is https://aagmaal.farm/
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select("div.recent-item")
    if not items:
        # Try article fallback
        items = soup.select("article")
        
    print(f"Found {len(items)} items")
    for item in items[:3]:
        title_tag = item.select_one("h3.post-box-title a") or item.select_one("h3 a") or item.select_one("h2.title a")
        if title_tag:
            name = utils.safe_get_text(title_tag)
            videopage = utils.safe_get_attr(title_tag, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_html = utils.getHtml(site_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    lis = cat_soup.select("li.cat-item")
    print(f"Found {len(lis)} categories")
    for li in lis[:3]:
        print(f"Category: {utils.safe_get_text(li)}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "bhabhi"
    search_url = f"{site_url}?s={search_keyword}"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    # Search uses List2 which uses 'article'
    search_items = search_soup.select("article")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

if __name__ == "__main__":
    test_aagmaalpro()
