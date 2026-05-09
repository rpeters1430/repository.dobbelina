import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_ask4porn = importlib.import_module("resources.lib.sites.ask4porn")

def test_ask4porn():
    print("Testing ask4porn...")
    site_url = "https://ask4porn.cc/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}?filter=latest"
    html, _ = utils.get_html_with_cloudflare_retry(list_url, referer=site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select("article.thumb-block, div.thumb-block, .thumb-block")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a")
        if link:
            name = utils.cleantext(utils.safe_get_text(item.select_one("span.title, h2, .title")))
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = f"{site_url}tags/"
    cat_html, _ = utils.get_html_with_cloudflare_retry(cat_url, referer=site_url)
    cat_soup = utils.parse_html(cat_html)
    # The code looks for a.netflix-tag-link
    cats = cat_soup.select("a.netflix-tag-link")
    if not cats:
        # Fallback to general tags
        cats = cat_soup.select("a[href*='/tag/']")
        
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_text(cat)
        print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}?s={search_keyword}"
    search_html, _ = utils.get_html_with_cloudflare_retry(search_url, referer=site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select("article.thumb-block, div.thumb-block, .thumb-block")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a")
        first_video_url = link['href']
        if not first_video_url.startswith("http"):
            first_video_url = urllib_parse.urljoin(site_url, first_video_url)
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html, _ = utils.get_html_with_cloudflare_retry(first_video_url, referer=site_url)
        
        # Check for video source or iframe
        soup_video = utils.parse_html(video_html)
        iframes = soup_video.select("iframe[src]")
        print(f"Found {len(iframes)} iframes")
        for ifr in iframes:
            print(f"Iframe: {ifr['src']}")

import urllib.parse as urllib_parse
if __name__ == "__main__":
    test_ask4porn()
