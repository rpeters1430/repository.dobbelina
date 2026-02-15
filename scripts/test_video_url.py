#!/usr/bin/env python3
"""Test if a video URL is accessible."""

import sys
import requests

def test_video_url(url):
    """Test if a video URL returns valid headers."""
    print(f"[*] Testing video URL...")
    print(f"    {url[:80]}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Range': 'bytes=0-1024'  # Just request first 1KB
    }

    try:
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"\n[+] Status Code: {response.status_code}")
        print(f"[+] Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"[+] Content-Length: {response.headers.get('Content-Length', 'N/A')}")

        if response.status_code in [200, 206]:
            print("\n✅ Video URL is accessible!")
            return True
        else:
            print("\n⚠️ Unexpected status code")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = input("Enter video URL to test: ")

    if test_url:
        test_video_url(test_url)
