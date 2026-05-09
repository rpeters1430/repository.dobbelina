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

site_xtheatre = importlib.import_module("resources.lib.sites.xtheatre")

def test_xtheatre():
    print("Testing xtheatre...")
    site_url = "https://pornxtheatre.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_xtheatre.XTList(f"{site_url}?filter=latest", 1)
        print("XTList function executed successfully")
    except Exception as e:
        print(f"Error in XTList: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    html = utils.getHtml(f"{site_url}?filter=latest", site_url)
    soup = utils.parse_html(html)
    item = soup.select_one("article")
    if item:
        link = item.select_one("a[href]")
        video_url = utils.safe_get_attr(link, "href")
        print(f"Testing playback for: {video_url}")
        try:
            site_xtheatre.XTVideo(video_url, "Test Video")
            print("XTVideo function executed successfully")
        except Exception as e:
            print(f"Error in XTVideo: {e}")
    else:
        print("No video found for playback test")

if __name__ == "__main__":
    test_xtheatre()
