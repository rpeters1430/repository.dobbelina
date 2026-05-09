import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_bongacams = importlib.import_module("resources.lib.sites.bongacams")

def test_bongacams():
    print("Testing bongacams...")
    
    # Test Listing (Female)
    print("\n--- Testing Listing (Female) ---")
    bu = "https://tools.bongacash.com/promo.php?c=226355&type=api&api_type=json&categories[]="
    list_url = f"{bu}female"
    
    # We use get_html_with_cloudflare_retry which returns (content, used_fs)
    data, used_fs = utils.get_html_with_cloudflare_retry(list_url)
    
    model_list = None
    try:
        model_list = site_bongacams._loads_json(data)
        if model_list and isinstance(model_list, list):
            print(f"Found {len(model_list)} models")
            for model in model_list[:3]:
                print(f"Model: {model.get('username')} (HD: {model.get('hd_cam')})")
        else:
            print(f"Failed to parse model list or list is empty. Type: {type(model_list)}")
            print(f"Data snippet: {str(data)[:200]}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

    # Test Playback Extraction (only if we have models)
    if model_list and isinstance(model_list, list) and len(model_list) > 0:
        username = model_list[0].get("username")
        print(f"\n--- Testing Playback Extraction for {username} ---")
        postRequest = [
            ("method", "getRoomData"),
            ("args[]", str(username)),
            ("args[]", ""),
            ("args[]", ""),
        ]
        hdr = utils.base_hdrs
        hdr.update({"X-Requested-With": "XMLHttpRequest"})
        try:
            # _postHtml returns the raw response
            response = utils._postHtml(
                "https://bongacams.com/tools/amf.php",
                form_data=postRequest,
                headers=hdr,
                compression=False,
            )
            
            if "cf-browser-verification" in response or "cloudflare" in response.lower():
                print("Cloudflare challenge detected on amf.php. Playback test skipped (requires FlareSolverr).")
            else:
                amf_json = json.loads(response)
                if amf_json.get("status") == "success":
                    video_url = amf_json.get("localData", {}).get("videoServerUrl")
                    print(f"Found video server: {video_url}")
                else:
                    print(f"AMF Error: {amf_json.get('message')}")
        except Exception as e:
            print(f"Error in AMF request: {e}")
    else:
        print("\nSkipping playback test as no models were found.")

if __name__ == "__main__":
    test_bongacams()
