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

site_pornhoarder = importlib.import_module("resources.lib.sites.pornhoarder")

def test_pornhoarder():
    print("Testing pornhoarder...")
    site_url = "https://pornhoarder.io/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_pornhoarder.List(f"{site_url}search/?search=&sort=0", page=1)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # We use the AJAX search to get a video URL
    headers = {
        "Origin": site_url[:-1],
        "User-Agent": utils.USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": site_url,
    }
    data = site_pornhoarder.Createdata(page=1, search="mom")
    try:
        listhtml = utils.postHtml(f"{site_url}ajax_search.php", form_data=data, headers=headers)
        soup = utils.parse_html(listhtml)
        item = soup.select_one(".video, article")
        if item:
            link = item.select_one('a[href*="/watch/"]')
            video_url = utils.safe_get_attr(link, "href")
            if not video_url.startswith("http"):
                 from urllib.parse import urljoin
                 video_url = urljoin(site_url, video_url)
            print(f"Testing playback for: {video_url}")
            try:
                site_pornhoarder.Playvid(video_url, "Test Video")
                print("Playvid function executed successfully")
            except Exception as e:
                print(f"Error in Playvid: {e}")
        else:
            print("No video found for playback test")
    except Exception as e:
         print(f"Error fetching AJAX: {e}")

if __name__ == "__main__":
    test_pornhoarder()
