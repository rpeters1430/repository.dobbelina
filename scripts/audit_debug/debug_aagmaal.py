import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_aagmaal = importlib.import_module("resources.lib.sites.aagmaal")

def test_aagmaal():
    print("Testing aagmaal...")
    site_url = "https://aagmaal.bz/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select("article")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a.vp-card__thumb") or item.select_one("a[href]")
        if link:
            videopage = utils.safe_get_attr(link, "href")
            img_tag = link.select_one("img")
            name = utils.safe_get_attr(img_tag, "alt") or utils.safe_get_attr(link, "title")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_html = utils.getHtml(site_url, site_url)
    cat_soup = utils.parse_html(cat_html)
    cat_found = False
    for h3 in cat_soup.select("h3"):
        if utils.safe_get_text(h3, "").strip() == "Categories":
            ul = h3.find_next_sibling("ul")
            if ul:
                lis = ul.select("li a[href]")
                print(f"Found {len(lis)} categories")
                for li in lis[:3]:
                    print(f"Category: {utils.safe_get_text(li)}")
                cat_found = True
            break
    if not cat_found:
        print("Categories section not found")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "bhabhi"
    search_url = f"{site_url}?s={search_keyword}"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select("article")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        first_video_url = items[0].select_one("a.vp-card__thumb") or items[0].select_one("a[href]")
        first_video_url = first_video_url['href']
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for hosted links
        soup_video = utils.parse_html(video_html)
        links = []
        for a in soup_video.select("a[title][href][target]"):
            link_url = utils.safe_get_attr(a, "href")
            if link_url:
                links.append(link_url)
        print(f"Found {len(links)} potential hosted links")
        for link in links[:3]:
            print(f"Link: {link}")

if __name__ == "__main__":
    test_aagmaal()
