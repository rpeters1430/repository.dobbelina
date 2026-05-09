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

site_stripchat = importlib.import_module("resources.lib.sites.stripchat")

def test_stripchat():
    print("Testing stripchat...")
    
    # Test Listing (Girls)
    print("\n--- Testing Listing (Girls) ---")
    list_url = "https://stripchat.com/api/front/models?limit=10&parentTag=autoTagNew&sortBy=trending&offset=0&primaryTag=girls"
    try:
        site_stripchat.List(list_url)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # We'll try to find a model from the API manually
    try:
        response, _ = utils.get_html_with_cloudflare_retry(list_url, "https://stripchat.com/")
        data = json.loads(response)
        models = data.get("models", [])
        if models:
            model = models[0]
            username = model.get("username")
            print(f"Testing playback for: {username}")
            try:
                # Playvid(username, username)
                site_stripchat.Playvid(username, username)
                print("Playvid function executed successfully")
            except Exception as e:
                print(f"Error in Playvid: {e}")
        else:
            print("No models found in API response")
    except Exception as e:
        print(f"Error fetching API: {e}")

if __name__ == "__main__":
    test_stripchat()
