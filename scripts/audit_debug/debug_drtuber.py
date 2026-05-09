import sys
import os
import re
import importlib
import json

# Add the project root to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, 'script.module.resolveurl', 'lib'))

import scripts.stub_kodi

from resources.lib import utils
site_drtuber = importlib.import_module("resources.lib.sites.drtuber")

def test_drtuber():
    print("Testing drtuber...")
    site_url = "https://www.drtuber.com/"
    
    # Test Listing
    print("\n--- Testing Listing ---")
    try:
        site_drtuber.List(site_url)
        print("List function executed successfully")
    except Exception as e:
        print(f"Error in List: {e}")

    # Test Categories
    print("\n--- Testing Categories ---")
    try:
        site_drtuber.Cat(f"{site_url}categories/")
        print("Cat function executed successfully")
    except Exception as e:
        print(f"Error in Cat: {e}")

    # Test Playback Extraction
    print("\n--- Testing Playback Extraction ---")
    video_url = f"{site_url}video/4484126/shy-desi-indian-gf-giving-blowjob-to-college-lover"
    try:
        # Mock VideoPlayer to avoid actual playback
        site_drtuber.Play(video_url, "Test Video")
        print("Play function executed successfully")
    except Exception as e:
        print(f"Error in Play: {e}")

if __name__ == "__main__":
    test_drtuber()
