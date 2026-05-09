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

import stub_kodi

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

site_naked = importlib.import_module("resources.lib.sites.naked")

def test_naked():
    print("Testing naked...")
    site_url = "https://www.naked.com/"
    
    # Test Listing (Girls)
    print("\n--- Testing Listing (Girls) ---")
    try:
        # Naked needs get_html_with_cloudflare_retry potentially
        site_naked.List(f"{site_url}live/girls/")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # Naked uses complex API calls. We'll see if we can find a model
    try:
        listhtml = utils._getHtml(f"{site_url}live/girls/", site_url)
        payload = site_naked._extract_models_payload(listhtml)
        if payload:
            models = json.loads(payload)
            if models:
                model = models[0]
                mid = model.get("model_id")
                video_host = model.get("video_host")
                print(f"Testing playback for model_id: {mid}, host: {video_host}")
                videourl = "https://ws.vs3.com/chat/get-stream-urls.php?model_id={0}&video_host={1}".format(
                    mid, video_host
                )
                try:
                    site_naked.Playvid(videourl, f"Test Model {mid}")
                    print("Playvid function executed successfully")
                except Exception as e:
                    print(f"Error in Playvid: {e}")
            else:
                print("No models found in payload")
        else:
            print("Models payload not found in listing page")
    except Exception as e:
        print(f"Error during playback test setup: {e}")

if __name__ == "__main__":
    test_naked()
