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

site_hentai_moon = importlib.import_module("resources.lib.sites.hentai-moon")

def test_hentai_moon():
    print("Testing hentai-moon...")
    site_url = "https://hentai-moon.com/"
    ajaxlist = "?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=1"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_hentai_moon.List(f"{site_url}latest-updates/{ajaxlist}")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Categories
    print("\n--- Testing Categories ---")
    try:
        site_hentai_moon.Categories(f"{site_url}categories/?mode=async&function=get_block&block_id=list_categories_categories_list&sort_by=title")
        print("Categories function executed successfully")
    except Exception as e:
        print(f"Error in Categories: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    html = utils.getHtml(f"{site_url}latest-updates/{ajaxlist}")
    soup = utils.parse_html(html)
    item = soup.select_one("a[href*='/videos/']")
    if item:
        video_url = utils.safe_get_attr(item, "href")
        if not video_url.startswith("http"):
             video_url = site_url[:-1] + video_url
        print(f"Testing playback for: {video_url}")
        try:
            site_hentai_moon.Playvid(video_url, "Test Video")
            print("Playvid function executed successfully")
        except Exception as e:
            print(f"Error in Playvid: {e}")
    else:
        print("No video found for playback test")

if __name__ == "__main__":
    test_hentai_moon()
