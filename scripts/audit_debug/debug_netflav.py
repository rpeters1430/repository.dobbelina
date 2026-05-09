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

site_netflav = importlib.import_module("resources.lib.sites.netflav")

def test_netflav():
    print("Testing netflav...")
    site_url = "https://netflav.com/"
    
    # Test Listing (Censored)
    print("\n--- Testing Listing (Censored) ---")
    try:
        # Note: Netflav is heavily Cloudflare-protected and uses Next.js
        site_netflav.List(f"{site_url}censored", section="censored")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # This site requires complex parsing of __NEXT_DATA__
    # We'll see if the List function finds any videos first
    try:
         headers = site_netflav.make_netflav_headers()
         html, _ = utils.get_html_with_cloudflare_retry(f"{site_url}censored", headers=headers)
         soup = utils.parse_html(html)
         script_tag = soup.select_one('script#__NEXT_DATA__[type="application/json"]')
         if script_tag:
             jdata = json.loads(script_tag.string).get("props", {}).get("initialState", {}).get("censored", {})
             videos = jdata.get("docs", [])
             if videos:
                 video_id = videos[0].get("videoId")
                 video_url = f"{site_url}video?id={video_id}"
                 print(f"Testing playback for: {video_url}")
                 try:
                     site_netflav.Playvid(video_url, "Test Video")
                     print("Playvid function executed successfully")
                 except Exception as e:
                     print(f"Error in Playvid: {e}")
             else:
                 print("No videos found in __NEXT_DATA__")
         else:
             print("__NEXT_DATA__ script tag NOT found")
    except Exception as e:
         print(f"Error during playback test setup: {e}")

if __name__ == "__main__":
    test_netflav()
