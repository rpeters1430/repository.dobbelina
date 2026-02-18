"""
Test hotleak video URL decryption without Playwright
"""
import base64
import json
import re
from bs4 import BeautifulSoup


def decrypt_hotleak_url(encrypted_url):
    """
    Decrypt hotleak video URL using their client-side decryption.

    The JavaScript function f() does:
    1. Remove first 8 characters
    2. Remove last 16 characters
    3. Reverse the string
    4. Base64 decode

    Args:
        encrypted_url: The encrypted URL from data-video.source[0].src

    Returns:
        Decrypted M3U8 URL
    """
    # Remove first 8 chars
    decrypted = encrypted_url[8:]
    # Remove last 16 chars
    decrypted = decrypted[:-16]
    # Reverse the string
    decrypted = decrypted[::-1]
    # Base64 decode
    decrypted = base64.b64decode(decrypted).decode('utf-8')

    return decrypted


def extract_video_url_from_html(html):
    """
    Extract and decrypt video URL from hotleak HTML.

    Args:
        html: The HTML content from the video page

    Returns:
        Decrypted M3U8 URL or None if not found
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Look for elements with data-video attribute
    video_items = soup.select('[data-video]')

    for item in video_items:
        data_video = item.get('data-video', '')
        if not data_video:
            continue

        try:
            video_json = json.loads(data_video)

            # Extract encrypted URL
            if 'source' in video_json and len(video_json['source']) > 0:
                encrypted_url = video_json['source'][0].get('src', '')

                if encrypted_url:
                    # Decrypt and return the first valid URL found
                    decrypted_url = decrypt_hotleak_url(encrypted_url)
                    return decrypted_url

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            continue

    return None


# Test the decryption
if __name__ == '__main__':
    # Test cases from the actual page
    test_cases = [
        "nsHBDRtgq21ismxd==wToxkWER0YThjYYdTcwZkY9IzZpNnJ1ADNiFjM2YWYjdTN4ATNkdTNiVGOlNTMjJ2Y0MDOxYWYldTYmJmNllTOwETN4ATZidTO5MTN0EGNmFTY4ETNh1zZpNnJ4MzM5gTMxczNx0TZtlGd/gTdz0mL2kDM5MTOxEzL4U3Mt9CcpZnLrFWZsR3bo9yL6MHc0RHaAwsYEQOVzY1M3sRW",
        "y5jckDxlP3EvJPZT==wQyFDTZJ3QyVWVxQ2Y2YFS9IzZpNnJ1UWNmZGM0UTYkNjMhJDM0IGN1QDN2YmY0EmZ5UWOlRjY1EGMiV2NxEWYxYDO3kzMjNzNyI2MmdzNxYGMjF2Mz0zZpNnJ4MzM5gTMxczNx0TZtlGd/gTdz0mL5kDM5MTOxEzL4U3Mt9CcpZnLrFWZsR3bo9yL6MHc0RHaVir2KICDc1IDr0Kn",
    ]

    print("Testing hotleak URL decryption:\n")

    for idx, encrypted in enumerate(test_cases, 1):
        print(f"Test {idx}:")
        print(f"  Encrypted: {encrypted[:60]}...")

        try:
            decrypted = decrypt_hotleak_url(encrypted)
            print(f"  Decrypted: {decrypted}")
            print(f"  ✅ SUCCESS\n")
        except Exception as e:
            print(f"  ❌ FAILED: {e}\n")
