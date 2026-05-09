import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_analdin = importlib.import_module("resources.lib.sites.analdin")

def test_analdin():
    print("Testing analdin...")
    site_url = "https://www.analdin.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(site_url + "latest-updates/", site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select(".list-videos .item, .list-videos .item-video, .list-videos .video-item, .item")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a.popup-video-link[href]") or item.select_one("a[href]")
        if link:
            name = utils.cleantext(utils.safe_get_text(item.select_one(".title")))
            videopage = utils.safe_get_attr(link, "href")
            print(f"Video: {name} -> {videopage}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "anal"
    search_url = f"{site_url}search/{search_keyword}/"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select(".list-videos .item, .list-videos .item-video, .list-videos .video-item, .item")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a.popup-video-link[href]") or items[0].select_one("a[href]")
        first_video_url = link['href']
        if not first_video_url.startswith("http"):
            first_video_url = site_url.rstrip('/') + first_video_url
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for video_url or video_alt_url
        match = re.search(r"video_alt_url:\s*'([^']+)'", video_html, re.IGNORECASE)
        if not match:
            match = re.search(r"video_url:\s*'([^']+)'", video_html, re.IGNORECASE)
        
        if match:
            print(f"Found direct link: {match.group(1)}")
        elif "kt_player(" in video_html:
            print("kt_player detected")
        else:
            print("Video source not found")

if __name__ == "__main__":
    test_analdin()
