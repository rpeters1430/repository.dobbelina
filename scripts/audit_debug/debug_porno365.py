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

site_porno365 = importlib.import_module("resources.lib.sites.porno365")

def test_porno365():
    print("Testing porno365...")
    site_url = "https://porno365.club/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_porno365.List(f"{site_url}")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    html = utils.getHtml(site_url, site_url, headers=headers)
    soup = utils.parse_html(html)
    item = soup.select_one("div.thumb")
    if item:
        link = item.select_one("a.th-title") or item.select_one("div.th-img a")
        video_url = utils.safe_get_attr(link, "href")
        if not video_url.startswith("http"):
             from urllib.parse import urljoin
             video_url = urljoin(site_url, video_url)
        print(f"Testing playback for: {video_url}")
        try:
            site_porno365.Playvid(video_url, "Test Video")
            print("Playvid function executed successfully")
        except Exception as e:
            print(f"Error in Playvid: {e}")
    else:
        print("No video found for playback test")

if __name__ == "__main__":
    test_porno365()
