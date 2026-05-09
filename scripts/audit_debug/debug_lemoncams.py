import sys
import os
import re
import importlib
import json
import ssl
import time

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

site_lemoncams = importlib.import_module("resources.lib.sites.lemoncams")

def test_lemoncams():
    print("Testing lemoncams...")
    
    # Test Listing (Top Stripchat Cams)
    print("\n--- Testing Listing (Top) ---")
    try:
        site_lemoncams.List("__top__", 1)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction (using a real username if found)
    print("\n--- Testing Playback Extraction ---")
    # We'll try to find a username from the API manually
    API_URL = "https://api-v2-prod.lemoncams.com/main"
    params = {
        "page": "1",
        "function": "cams",
        "project": "lemoncams",
        "tsp": str(int(time.time() * 1000)),
        "provider": "stripchat"
    }
    query = urllib_parse.urlencode(params)
    url = "{}?{}".format(API_URL, query)
    try:
        payload = utils._getHtml(url, referer="https://www.lemoncams.com/")
        jd = json.loads(payload)
        cams = jd.get("cams", [])
        if cams:
            username = cams[0].get("username")
            print(f"Testing playback for: {username}")
            try:
                # Build mock URL format: stripchat/username|stream_url
                stream_url = site_lemoncams._extract_playable_url(cams[0])
                mock_url = f"stripchat/{username}|{stream_url}"
                site_lemoncams.Playvid(mock_url, f"Test: {username}")
                print("Playvid function executed successfully")
            except Exception as e:
                print(f"Error in Playvid: {e}")
        else:
            print("No cams found in API response")
    except Exception as e:
        print(f"Error fetching API: {e}")

if __name__ == "__main__":
    from six.moves import urllib_parse
    test_lemoncams()
