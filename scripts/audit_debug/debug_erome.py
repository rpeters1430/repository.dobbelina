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

site_erome = importlib.import_module("resources.lib.sites.erome")

def test_erome():
    print("Testing erome...")
    site_url = "https://www.erome.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_erome.List(f"{site_url}explore/new")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Playback Extraction (requires an album with videos)
    print("\n--- Testing Playback Extraction ---")
    html = utils.getHtml(f"{site_url}explore/new", site_url)
    soup = utils.parse_html(html)
    album = soup.select_one(".album-videos")
    if album:
        album_item = album.find_parent("div", id=re.compile(r"album-"))
        if album_item:
            title_link = album_item.select_one("a.album-title")
            album_url = utils.safe_get_attr(title_link, "href")
            print(f"Testing album: {album_url}")
            try:
                site_erome.List2(album_url, "vids")
                print("List2 (vids) function executed successfully")
            except Exception as e:
                print(f"Error in List2: {e}")
        else:
             print("Could not find parent album div")
    else:
        print("No video album found on explore page")

if __name__ == "__main__":
    test_erome()
