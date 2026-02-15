#!/usr/bin/env python3
"""Analyze anybunny page to find video URL in JavaScript."""

import requests
import re

url = 'https://anybunny.org/view/anb4KREd'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=10)

print('=== Looking for video patterns in JavaScript ===\n')

# Pattern 1: Look for .mp4 or .m3u8 URLs
video_patterns = [
    (r'[\"\047](https?://[^\"\047]+\.mp4[^\"\047]*)[\"\047]', 'MP4 in quotes'),
    (r'[\"\047](https?://[^\"\047]+\.m3u8[^\"\047]*)[\"\047]', 'M3U8 in quotes'),
    (r'file[\"\047]\s*:\s*[\"\047](https?://[^\"\047]+)[\"\047]', 'file: property'),
    (r'source[\"\047]\s*:\s*[\"\047](https?://[^\"\047]+)[\"\047]', 'source: property'),
    (r'src[\"\047]\s*:\s*[\"\047](https?://[^\"\047]+\.mp4[^\"\047]*)[\"\047]', 'src: property'),
]

found_any = False
for pattern, desc in video_patterns:
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    if matches:
        print(f'{desc}: ({len(matches)} matches)')
        for match in matches[:3]:
            print(f'  - {match[:120]}')
            if '.mp4' in match or '.m3u8' in match:
                found_any = True
        print()

if not found_any:
    print('No direct video URLs found in HTML/JS')
    print('\n=== Checking for embedded players ===')

    # Look for iframe sources
    iframe_matches = re.findall(r'<iframe[^>]+src=[\"\047]([^\"\047]+)[\"\047]', response.text, re.IGNORECASE)
    if iframe_matches:
        print(f'Found {len(iframe_matches)} iframe(s):')
        for iframe in iframe_matches[:3]:
            print(f'  - {iframe}')
    else:
        print('No iframes found')

    print('\n=== Sample of page content (first 2000 chars) ===')
    print(response.text[:2000])
