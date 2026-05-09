import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_anysex = importlib.import_module("resources.lib.sites.anysex")

def test_anysex():
    print("Testing anysex...")
    site_url = "https://anysex.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}videos/new/"
    html, _ = utils.get_html_with_cloudflare_retry(list_url, referer=site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    item_selectors = ".list-videos .item, #list_videos_custom_videos_list_items .item, .item[data-video-id]"
    items = soup.select(item_selectors)
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a[href*='/video/'], a[href*='/videos/']")
        if link:
            name = utils.cleantext(utils.safe_get_attr(link, "title") or utils.safe_get_text(item.select_one(".title")))
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Categories ---")
    cat_url = f"{site_url}videos/categories/"
    cat_html, _ = utils.get_html_with_cloudflare_retry(cat_url, referer=site_url)
    cat_soup = utils.parse_html(cat_html)
    cats = cat_soup.select(".list-categories .item")
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_text(cat.select_one(".title"))
        print(f"Category: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}search/?q={search_keyword}"
    search_html, _ = utils.get_html_with_cloudflare_retry(search_url, referer=site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select(item_selectors)
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a[href*='/video/'], a[href*='/videos/']")
        first_video_url = link['href']
        if not first_video_url.startswith("http"):
            first_video_url = urllib_parse.urljoin(site_url, first_video_url)
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html, _ = utils.get_html_with_cloudflare_retry(first_video_url, referer=site_url)
        
        # Check for video source
        match = re.search(r'video_url\s*:\s*["\']([^"\']+)["\']', video_html)
        if match:
            print(f"Found video_url: {match.group(1)}")
        else:
            sources = re.findall(r'<source\s*src="([^"]+)"', video_html)
            if sources:
                print(f"Found source tags: {sources}")
            else:
                print("Video source not found")

import urllib.parse as urllib_parse
if __name__ == "__main__":
    test_anysex()
