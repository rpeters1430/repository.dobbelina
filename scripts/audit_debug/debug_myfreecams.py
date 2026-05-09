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

site_myfreecams = importlib.import_module("resources.lib.sites.myfreecams")

def test_myfreecams():
    print("Testing myfreecams...")
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_myfreecams.List("https://www.myfreecams.com/php/model_explorer.php?get_contents=1&sort=cam_score&selection=public&page=1")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # We need a model name from the listing
    try:
        serverlist = utils.getHtml("https://app.myfreecams.com/server")
        if serverlist:
             print("Successfully fetched server list")
             # Actually testing playback needs a real model name
             # This will likely fail due to websocket dependency or complex logic
             print("Skipping full playback test due to websocket complexity in debug script.")
    except Exception as e:
        print(f"Error fetching servers: {e}")

if __name__ == "__main__":
    test_myfreecams()
