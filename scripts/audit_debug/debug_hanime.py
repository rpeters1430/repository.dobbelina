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

site_hanime = importlib.import_module("resources.lib.sites.hanime")

def test_hanime():
    print("Testing hanime...")
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        # hanime_list uses POST
        site_hanime.hanime_list("", "", 0)
        print("hanime_list function executed successfully")
    except Exception as e:
        print(f"Error in hanime_list: {e}")

    # Test Playback Extraction (requires a slug)
    print("\n--- Testing Playback Extraction ---")
    # I'll try to find a slug from the listing first
    siteurl = "https://search.htv-services.com/"
    data = {
        "search_text": "",
        "tags": [],
        "tags_mode": "OR",
        "brands": [],
        "blacklist": [],
        "order_by": "created_at_unix",
        "ordering": "desc",
        "page": 0,
    }
    try:
        listhtml = utils.postHtml(
            siteurl, json_data=data, headers={"User-Agent": "Mozilla/5.0"}
        )
        hits = json.loads(listhtml)
        videos = json.loads(hits["hits"])
        if videos:
            slug = videos[0]["slug"]
            print(f"Testing playback for slug: {slug}")
            try:
                site_hanime.hanime_play(slug, "Test Video")
                print("hanime_play function executed successfully")
            except Exception as e:
                print(f"Error in hanime_play: {e}")
        else:
            print("No videos found to test playback")
    except Exception as e:
        print(f"Error fetching search hits: {e}")

if __name__ == "__main__":
    test_hanime()
