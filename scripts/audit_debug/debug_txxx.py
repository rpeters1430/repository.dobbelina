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

site_txxx = importlib.import_module("resources.lib.sites.txxx")

def test_txxx():
    print("Testing txxx...")
    site_url = "https://txxx.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_txxx.List(f"{site_url}latest-updates")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # We need a video ID from the working API URL
    try:
        api_url = f"{site_url}api/json/videos/86400/str/latest-updates/60/..1.json"
        data = utils.getHtml(api_url, site_url)
        jdata = json.loads(data)
        if jdata.get("videos"):
            video = jdata["videos"][0]
            video_id = video.get("video_id")
            print(f"Testing playback for video_id: {video_id}")
            try:
                site_txxx.Playvid(f"{site_url}{video_id}", "Test Video")
                print("Playvid function executed successfully")
            except Exception as e:
                print(f"Error in Playvid: {e}")
        else:
            print("No videos found in API response")
    except Exception as e:
        print(f"Error fetching API: {e}")

if __name__ == "__main__":
    test_txxx()
