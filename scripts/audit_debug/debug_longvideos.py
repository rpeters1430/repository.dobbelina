import sys
import os
import re
import importlib
import json
import ssl

# Disable SSL verification for debug script
ssl._create_default_https_context = ssl._create_unverified_context

# Add the project root to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, 'script.module.resolveurl', 'lib'))

import scripts.stub_kodi

from resources.lib import utils

# Monkey-patch SSL context creation to avoid cert errors in local environment
def unverified_ssl_context():
    return ssl._create_unverified_context()
utils._create_ssl_context = unverified_ssl_context

# Re-create the opener with the unverified context
import urllib.request as urllib_request
utils.handlers = [urllib_request.HTTPBasicAuthHandler(), urllib_request.HTTPHandler()]
utils.handlers.append(urllib_request.HTTPSHandler(context=utils._create_ssl_context()))
utils.opener = urllib_request.build_opener(*utils.handlers)
utils.urllib_request.install_opener(utils.opener)
utils.urlopen = utils.opener.open

site_longvideos = importlib.import_module("resources.lib.sites.longvideos")

def test_longvideos():
    print("Testing longvideos...")
    site_url = "https://www.wow.xxx/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    html = utils.getHtml(f"{site_url}latest-updates/", site_url)
    if not html:
        print("Failed to fetch listing HTML")
        return
        
    soup = utils.parse_html(html)
    items = soup.select("div.item")
    print(f"Found {len(items)} items")
    for item in items[:3]:
        link = item.select_one("a.thumb_img")
        title = utils.safe_get_text(item.select_one("strong.title"))
        print(f"Item: {title} -> {link.get('href')}")

    # Test Playback Extraction
    if items:
        video_url = items[0].select_one("a.thumb_img").get("href")
        if not video_url.startswith("http"):
             from six.moves import urllib_parse
             video_url = urllib_parse.urljoin(site_url, video_url)
        print(f"\n--- Testing Playback Extraction for {video_url} ---")
        try:
            site_longvideos.Playvid(video_url, "Test Video")
            print("Playvid function executed successfully")
        except Exception as e:
            print(f"Error in Playvid: {e}")
    else:
        print("No video found for playback test")

if __name__ == "__main__":
    test_longvideos()
