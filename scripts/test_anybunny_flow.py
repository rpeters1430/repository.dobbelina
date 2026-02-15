#!/usr/bin/env python3
"""Test complete anybunny flow: list videos and extract playback URL."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.utils.playwright_helper import fetch_with_playwright, sniff_video_url
from bs4 import BeautifulSoup


def test_anybunny_listing():
    """Test fetching and parsing video listing."""
    print("[*] Testing anybunny video listing...")

    list_url = "https://anybunny.org/new/"
    print(f"    Fetching: {list_url}")

    try:
        html = fetch_with_playwright(list_url, wait_for="load")
        soup = BeautifulSoup(html, 'html.parser')

        # Find video links
        video_links = []
        for anchor in soup.select('a.nuyrfe[href], a[href*="/view/"], a[href*="/videos/"]'):
            href = anchor.get('href', '')
            if '/view/' in href or '/videos/' in href:
                if not href.startswith('http'):
                    href = 'https://anybunny.org' + href
                video_links.append(href)

        video_links = list(set(video_links))[:5]  # Get first 5 unique

        print(f"\n[+] Found {len(video_links)} video(s)")
        for i, link in enumerate(video_links, 1):
            print(f"    {i}. {link}")

        return video_links

    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_anybunny_playback(video_url):
    """Test extracting playback URL from a video page."""
    print(f"\n[*] Testing video playback extraction...")
    print(f"    Video URL: {video_url}")

    play_selectors = ["pjsdiv", "video", ".play-button", "button.vjs-big-play-button"]

    try:
        video_stream = sniff_video_url(
            video_url,
            play_selectors=play_selectors,
            wait_after_click=5000,
            timeout=60000,
            debug=False
        )

        if video_stream:
            print(f"\n[+] Video stream URL found:")
            print(f"    {video_stream[:100]}...")
            return video_stream
        else:
            print("\n[!] No video stream URL found")
            return None

    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("ANYBUNNY FLOW TEST")
    print("=" * 60)

    # Test listing
    video_links = test_anybunny_listing()

    if video_links:
        # Test playback on first video
        test_url = video_links[0]
        video_stream = test_anybunny_playback(test_url)

        if video_stream:
            print("\n" + "=" * 60)
            print("✅ ANYBUNNY FLOW TEST PASSED")
            print("=" * 60)
            print("\nBoth listing and playback extraction are working!")
        else:
            print("\n" + "=" * 60)
            print("⚠️ PARTIAL SUCCESS")
            print("=" * 60)
            print("\nListing works, but playback extraction failed")
    else:
        print("\n" + "=" * 60)
        print("❌ LISTING FAILED")
        print("=" * 60)
