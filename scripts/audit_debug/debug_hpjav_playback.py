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

site_hpjav = importlib.import_module("resources.lib.sites.hpjav")

def test_hpjav_playback():
    url = "https://hpjav.in/uncensored/hp-removal_hzgd-258/"
    print(f"Testing playback for: {url}")
    
    videopage, _ = utils.get_html_with_cloudflare_retry(url)
    
    # Extract packed data
    packed_data = utils.get_packed_data(videopage)
    print(f"Packed data length: {len(packed_data)}")
    if packed_data:
        print(f"Packed data snippet: {packed_data[:500]}")
    
    # Try different regexes
    eurls = re.findall(r'https?://[^"\'\s]+/(?:embed|e|v|f)/[a-zA-Z0-9]+', videopage + packed_data)
    print(f"Found {len(eurls)} potential URLs with regex 1")
    for e in eurls:
        print(f"URL: {e}")
        
    eurls2 = re.findall(r'src="([^"]+)"', videopage + packed_data)
    print(f"Found {len(eurls2)} URLs with src regex")
    for e in eurls2:
        print(f"SRC URL: {e}")

if __name__ == "__main__":
    test_hpjav_playback()
