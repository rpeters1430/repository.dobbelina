#!/usr/bin/env python3
"""Test anybunny iframe video extraction."""

import requests
import re
from urllib.parse import urljoin

def test_anybunny_iframe_extraction(video_url):
    """Test extracting video URL via iframe method."""
    print(f"[*] Testing: {video_url}")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # Step 1: Fetch main page
    print("\n[*] Fetching main page...")
    response = requests.get(video_url, headers=headers, timeout=10)
    pagehtml = response.text

    # Step 2: Extract iframe URL
    print("[*] Looking for iframe...")
    iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', pagehtml, re.IGNORECASE)

    if not iframe_match:
        print("❌ No iframe found")
        return None

    iframe_url = iframe_match.group(1)
    if not iframe_url.startswith('http'):
        iframe_url = urljoin(video_url, iframe_url)

    print(f"[+] Found iframe: {iframe_url[:120]}...")

    # Step 3: Fetch iframe content
    print("\n[*] Fetching iframe content...")
    iframe_response = requests.get(iframe_url, headers={**headers, 'Referer': video_url}, timeout=10)
    iframe_html = iframe_response.text

    # Step 4: Extract video URL
    print("[*] Searching for video URL...")
    video_patterns = [
        (r'(https?://[^\s\"\'\],]+\.mp4[^\s\"\'\],]*)', 'MP4 URL'),
        (r'(https?://[^\s\"\'\],]+\.m3u8[^\s\"\'\],]*)', 'M3U8 URL'),
    ]

    for pattern, desc in video_patterns:
        video_match = re.search(pattern, iframe_html, re.IGNORECASE)
        if video_match:
            video_url_found = video_match.group(1)
            # Clean up any trailing characters
            video_url_found = video_url_found.split(':cast:')[0]  # Remove Chromecast URLs
            video_url_found = re.sub(r'[,\]\)\}].*$', '', video_url_found)  # Remove trailing punctuation

            print(f"[+] Found video URL using '{desc}':")
            print(f"    {video_url_found[:150]}...")

            # Test if URL is accessible
            try:
                test_response = requests.head(video_url_found, headers=headers, timeout=10, allow_redirects=True)
                print(f"\n[+] Video URL is accessible!")
                print(f"    Status: {test_response.status_code}")
                print(f"    Content-Type: {test_response.headers.get('Content-Type', 'N/A')}")
                return video_url_found
            except Exception as e:
                print(f"[!] Could not access video URL: {e}")
                continue

    print("❌ No video URL found in iframe")
    print("\n[DEBUG] First 1000 chars of iframe HTML:")
    print(iframe_html[:1000])
    return None


if __name__ == "__main__":
    test_url = "https://anybunny.org/view/anb4KREd"
    result = test_anybunny_iframe_extraction(test_url)

    if result:
        print(f"\n✅ SUCCESS! Video URL: {result[:100]}...")
    else:
        print("\n❌ FAILED to extract video URL")
