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

site_streamate = importlib.import_module("resources.lib.sites.streamate")

def test_streamate():
    print("Testing streamate...")
    
    # Test Listing
    print("\n--- Testing Listing ---")
    list_url = "https://member.naiadsystems.com/search/v3/performers?domain=streamate.com&from=0&size=100&filters=gender:f,ff,mf,tm2f,g%3Bonline:true&genderSetting=f"
    try:
        site_streamate.List(list_url)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # We'll try to find a performer from the API
    try:
        headers = {
            "platform": "SCP",
            "smtid": "ffffffff-ffff-ffff-ffff-ffffffffffffG0000000000000",
            "smeid": "ffffffff-ffff-ffff-ffff-ffffffffffffG0000000000000",
            "smvid": "ffffffff-ffff-ffff-ffff-ffffffffffffG0000000000000",
            "User-Agent": utils.USER_AGENT,
        }
        data = utils._getHtml(list_url, headers=headers)
        model_list = site_streamate._loads_json(data)
        if model_list and model_list.get("performers"):
            performer = model_list["performers"][0]
            nickname = performer.get("nickname")
            pid = performer.get("id")
            print(f"Testing playback for: {nickname} ({pid})")
            try:
                site_streamate.Playvid(f"{nickname}$${pid}", nickname)
                print("Playvid function executed successfully")
            except Exception as e:
                print(f"Error in Playvid: {e}")
        else:
            print("No models found in API response")
    except Exception as e:
        print(f"Error fetching API: {e}")

if __name__ == "__main__":
    test_streamate()
