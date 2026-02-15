#!/usr/bin/env python3
"""Test anybunny video extraction using the existing sniff_video_url function."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from resources.lib.playwright_helper import sniff_video_url


def test_anybunny_sniff(video_url: str):
    """Test the sniff_video_url function with anybunny."""
    print(f"[*] Testing anybunny video: {video_url}")

    # These are the selectors used in anybunny.py
    play_selectors = [
        "pjsdiv",
        "video",
        ".play-button",
        "button.vjs-big-play-button"
    ]

    print(f"[*] Using play selectors: {play_selectors}")
    print("[*] Calling sniff_video_url()...")

    try:
        video_url_result = sniff_video_url(
            video_url,
            play_selectors=play_selectors,
            timeout=60000,
            wait_after_click=5000,  # Wait 5s after clicking
            debug=True  # Enable debug output
        )

        if video_url_result:
            print(f"\n[+] SUCCESS! Video URL found:")
            print(f"    {video_url_result}")
            return video_url_result
        else:
            print("\n[!] No video URL found")
            return None

    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = input("Enter anybunny video URL: ")

    if test_url:
        result = test_anybunny_sniff(test_url)
        if result:
            print(f"\n[*] Final result: {result}")
        else:
            print("\n[*] No result - debugging needed")
