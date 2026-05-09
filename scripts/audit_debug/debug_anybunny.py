import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_anybunny = importlib.import_module("resources.lib.sites.anybunny")

def test_anybunny():
    print("Testing anybunny...")
    site_url = "https://anybunny.org/"
    
    # Test Categories (Root page)
    print("\n--- Testing Categories ---")
    html, _ = utils.get_html_with_cloudflare_retry(site_url, referer=site_url)
    if not html:
        print("Failed to fetch main page")
        return
    
    soup = utils.parse_html(html)
    cats = [a for a in soup.select("a.nuyrfe") if "/top/" in a.get('href', '') and "/too/" not in a.get('href', '')]
    print(f"Found {len(cats)} categories")
    for cat in cats[:3]:
        name = utils.safe_get_text(cat) or utils.safe_get_attr(cat.find('img'), 'alt')
        print(f"Category: {name} -> {cat['href']}")

    # Test Listing (of first category)
    if cats:
        cat_url = urllib_parse.urljoin(site_url, cats[0]['href'])
        print(f"\n--- Testing Listing for {cat_url} ---")
        list_html, _ = utils.get_html_with_cloudflare_retry(cat_url, referer=site_url)
        list_soup = utils.parse_html(list_html)
        items = list_soup.select("a.nuyrfe[href*='/too/']")
        print(f"Found {len(items)} items")
        for item in items[:3]:
            img_tag = item.select_one("img.imgresdif") or item.find("img", attrs={"src": re.compile(r"cdnclouder|thumb")})
            if not img_tag:
                imgs = item.find_all("img")
                if imgs: img_tag = imgs[-1]
                
            name = utils.cleantext(utils.safe_get_attr(img_tag, "alt"))
            if not name:
                name = utils.cleantext(utils.safe_get_attr(item, "title") or "")
            if not name:
                name = utils.cleantext(item['href'].split("-", 1)[-1].replace("_", " ").title())
                
            videopage = item['href']
            print(f"Video: {name} -> {videopage}")

    # Test Search
    print("\n--- Testing Search ---")
    search_keyword = "milf"
    search_url = f"{site_url}top/{search_keyword}"
    search_html, _ = utils.get_html_with_cloudflare_retry(search_url, referer=site_url)
    search_soup = utils.parse_html(search_html)
    search_items = search_soup.select("a.nuyrfe[href*='/too/']")
    print(f"Found {len(search_items)} search results for '{search_keyword}'")

    # Test Playback Extraction
    if items:
        first_video_url = items[0]['href']
        if not first_video_url.startswith("http"):
            first_video_url = urllib_parse.urljoin(site_url, first_video_url)
        print(f"\n--- Testing Playback Extraction for {first_video_url} ---")
        video_html, _ = utils.get_html_with_cloudflare_retry(first_video_url, referer=site_url)
        
        # Check for file: or iframe
        file_match = re.search(r'file\s*:\s*["\']([^"\']+)["\']', video_html)
        if file_match:
            print(f"Found file parameter: {file_match.group(1)}")
        else:
            iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', video_html)
            if iframe_match:
                print(f"Found iframe: {iframe_match.group(1)}")
            else:
                print("Video source or iframe not found")

import urllib.parse as urllib_parse
if __name__ == "__main__":
    test_anybunny()
