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

site_theyarehuge = importlib.import_module("resources.lib.sites.theyarehuge")

def test_theyarehuge():
    print("Testing theyarehuge...")
    site_url = "https://www.theyarehuge.com/"
    ajax_url = f"{site_url}latest-updates/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=1"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_theyarehuge.List(ajax_url, 1)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    video_url = "https://www.theyarehuge.com/v/get-a-lesson-from-huge-tits-stepsister.big-boobs"
    print(f"Testing playback for: {video_url}")
    try:
        site_theyarehuge.Playvid(video_url, "Test Video")
        print("Playvid function executed successfully")
    except Exception as e:
        print(f"Error in Playvid: {e}")

if __name__ == "__main__":
    test_theyarehuge()
