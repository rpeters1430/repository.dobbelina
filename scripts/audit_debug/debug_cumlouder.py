import sys
import os
import re
import importlib

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts.stub_kodi

from resources.lib import utils
site_cumlouder = importlib.import_module("resources.lib.sites.cumlouder")

def test_cumlouder():
    print("Testing cumlouder...")
    site_url = "https://www.cumlouder.com/"
    
    # Test Categories (Now using BS4 in the module)
    print("\n--- Testing Categories (BS4 in module) ---")
    # site_cumlouder.Categories will call site.add_dir
    # Our stub_kodi.py should handle this.
    try:
        site_cumlouder.Categories(f"{site_url}categories/")
        # If no exception, it likely worked. 
        # In a real test we'd check the added dirs, but for now we'll just see if it runs.
        print("Categories function executed successfully")
    except Exception as e:
        print(f"Error in Categories: {e}")

    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_cumlouder.List(f"{site_url}porn/")
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

if __name__ == "__main__":
    test_cumlouder()
