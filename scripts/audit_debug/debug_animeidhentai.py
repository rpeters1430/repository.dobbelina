import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_animeidhentai = importlib.import_module("resources.lib.sites.animeidhentai")

def test_animeidhentai():
    print("Testing animeidhentai...")
    site_url = "https://animeidhentai.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = f"{site_url}?s="
    html = utils.getHtml(list_url, site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    items = soup.select("article")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        title_tag = item.select_one(".title, h2, h3")
        name = utils.safe_get_text(title_tag)
        link = item.select_one("a.link-co[href]") or item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href")
        print(f"Video: {name} -> {videopage}")

    # Test Categories
    print("\n--- Testing Genres ---")
    genres_html = utils.getHtml(site_url, site_url)
    genres_soup = utils.parse_html(genres_html)
    # The genres are usually listed in a sidebar or specific page
    # In animeidhentai_genres it looks for 'article' in site.url
    genre_items = genres_soup.select("article")
    print(f"Found {len(genre_items)} genre/category items on homepage")
    for item in genre_items[:3]:
        name = utils.safe_get_text(item.select_one(".link-co"))
        print(f"Genre: {name}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "overflow"
    search_url = f"{site_url}?s={search_keyword}"
    search_html = utils.getHtml(search_url, site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select("article")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        link = items[0].select_one("a.link-co[href]") or items[0].select_one("a[href]")
        first_video_url = link['href']
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html = utils.getHtml(first_video_url, site_url)
        
        # Check for iframe
        soup_video = utils.parse_html(video_html)
        iframes = soup_video.select("iframe[src]")
        print(f"Found {len(iframes)} iframes")
        for ifr in iframes:
            src = ifr['src']
            print(f"Iframe: {src}")

if __name__ == "__main__":
    test_animeidhentai()
