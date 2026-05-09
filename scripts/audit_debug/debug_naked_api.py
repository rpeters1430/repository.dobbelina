import sys
import os
import re
import json
import ssl

# Disable SSL verification for debug script
ssl._create_default_https_context = ssl._create_unverified_context

# Add the project root and scripts directory to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS = os.path.join(ROOT, 'scripts')
sys.path.append(ROOT)
sys.path.append(SCRIPTS)

import stub_kodi
from resources.lib import utils

def test_naked_api():
    print("Testing Naked.com API hypothesis...")
    base_url = "https://www.naked.com/"
    
    test_urls = [
        f"{base_url}?tpl=index2&model=json",
        f"{base_url}live/girls/?tpl=index2&model=json",
        f"{base_url}search/models/?q=ebony&model=json",
        f"{base_url}search/models/?q=ebony&tpl=index2&model=json",
    ]
    
    for api_url in test_urls:
        print(f"\nRequesting: {api_url}")
        headers = utils.base_hdrs.copy()
        headers["Referer"] = base_url
        
        try:
            html = utils._getHtml(api_url, base_url, headers=headers)
            if html:
                print(f"Received {len(html)} bytes")
                
                if "search/models" in api_url:
                     print("\nFirst 1000 characters of Search response:")
                     print(html[:1000])
                
                # Try to extract models array directly
                models_match = re.search(r"['\"]models['\"]\s*:\s*\[(.*?)\]\s*,\s*['\"]", html, re.DOTALL)
                if not models_match:
                     models_match = re.search(r"['\"]models['\"]\s*:\s*\[(.*?)\]\s*\}", html, re.DOTALL)
                     
                if models_match:
                    models_json = "[" + models_match.group(1).strip() + "]"
                    models_json = re.sub(r",\s*\]$", "]", models_json)
                    try:
                        models = json.loads(models_json)
                        print(f"Successfully parsed {len(models)} models!")
                        if models:
                             print(f"First 5 models: {[m.get('model_seo_name') for m in models[:5]]}")
                    except Exception as e:
                        print(f"Failed to parse models JSON: {e}")
                else:
                    print("Could not find 'models' array in response")
            else:
                print("Received empty response")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_naked_api()
