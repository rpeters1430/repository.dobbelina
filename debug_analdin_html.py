
import sys
import os

# Add the addon resources to the path
sys.path.append(os.path.join(os.getcwd(), 'plugin.video.cumination'))
sys.path.append(os.path.join(os.getcwd(), 'plugin.video.cumination', 'resources', 'lib'))

# Mock xbmc modules
from MagicMock.mock import mock_xbmc_all
mock_xbmc_all()

from resources.lib import utils
from resources.lib.sites import analdin

def debug_analdin():
    url = "https://www.analdin.com/latest-updates/"
    print(f"Fetching: {url}")
    
    # We want to see what utils.getHtml actually gets
    html = utils.getHtml(url, "https://www.analdin.com/")
    
    if not html:
        print("Got empty response")
        return

    print(f"Response length: {len(html)}")
    print("First 500 chars of response:")
    print("-" * 50)
    print(html[:500])
    print("-" * 50)
    
    if "just a moment" in html.lower() or "checking your browser" in html.lower() or "cloudflare" in html.lower():
        print("CLOUDFLARE DETECTED!")
    
    # Try to parse it using analdin's logic
    soup = utils.parse_html(html)
    items = soup.select(".list-videos .item, .list-videos .item-video, .list-videos .video-item, .item")
    print(f"Found {len(items)} items using selector '.list-videos .item'")
    
    # Check if any have /videos/ in them
    added = 0
    for item in items:
        link = item.select_one("a.popup-video-link[href]") or item.select_one("a[href]")
        if link:
            video_url = utils.safe_get_attr(link, "href")
            if video_url and "/videos/" in video_url:
                added += 1
    
    print(f"Items with /videos/ links: {added}")

if __name__ == "__main__":
    debug_analdin()
