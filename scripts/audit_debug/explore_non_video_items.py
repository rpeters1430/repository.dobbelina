import sys
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import scripts.stub_kodi
from resources.lib import utils

def explore():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://thothub.mx/'
    }
    
    url = "https://thothub.mx/categories/panty-fetish/"
    html = utils.getHtml(url, "https://thothub.mx/", headers=headers)
    if not html:
        return
        
    soup = utils.parse_html(html)
    items = soup.select(".item")
    print(f"Total .item elements: {len(items)}")
    non_video_count = 0
    for i, item in enumerate(items):
        if not item.select_one('a[href*="/videos/"]'):
            non_video_count += 1
            print(f"\n--- Non-video item {non_video_count} (index {i}) ---")
            print(item.prettify()[:1000])

if __name__ == "__main__":
    explore()
