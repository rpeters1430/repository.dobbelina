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

site_porndig = importlib.import_module("resources.lib.sites.porndig")

def test_porndig():
    print("Testing porndig...")
    site_url = "https://www.porndig.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        # Porndig List(channel, section, page=0)
        site_porndig.List(1, 0, 0)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    # I'll try to find a real video URL from the listing
    try:
        from six.moves import urllib_parse
        values = {
            "main_category_id": 1,
            "type": "post",
            "name": "category_videos",
            "filters[filter_type]": "date",
            "filters[filter_period]": "",
            "offset": 0,
        }
        data = urllib_parse.urlencode(values)
        headers = {"User-Agent": utils.USER_AGENT, "X-Requested-With": "XMLHttpRequest"}
        urldata = utils.getHtml(f"{site_url}posts/load_more_posts", site_url, headers, data=data)
        content = site_porndig.ParseJson(urldata)
        soup = utils.parse_html(content)
        item = soup.select_one("section")
        if item:
            link = item.select_one("a[href]")
            video_url = utils.safe_get_attr(link, "href")
            if not video_url.startswith("http"):
                 video_url = site_url.rstrip("/") + "/" + video_url.lstrip("/")
            print(f"Testing playback for: {video_url}")
            try:
                site_porndig.Playvid(video_url, "Test Video")
                print("Playvid function executed successfully")
            except Exception as e:
                print(f"Error in Playvid: {e}")
        else:
            print("No video found for playback test")
    except Exception as e:
         print(f"Error fetching API: {e}")

if __name__ == "__main__":
    test_porndig()
