#!/usr/bin/env python3
"""Test the peachurnet video URL extraction without Kodi dependencies."""

import base64
import re


def _decode_base64_var(value):
    """Decode a double base64-encoded value."""
    if not value:
        return ""
    try:
        # First decode
        first_decode = base64.b64decode(value).decode("utf-8")
        # Second decode
        second_decode = base64.b64decode(first_decode).decode("utf-8")
        return second_decode
    except Exception:
        return ""


def _extract_peachurnet_video_url(html):
    """
    Extract video URL from PeachUrNet's obfuscated JavaScript variables.
    """
    # Look for the JavaScript variables
    sy_match = re.search(r'var\s+sy\s*=\s*"([^"]+)"', html)
    syt_match = re.search(r'var\s+syt\s*=\s*"([^"]+)"', html)

    if not sy_match or not syt_match:
        return ""

    # Decode the variables
    request_url = _decode_base64_var(sy_match.group(1))
    path_suffix = _decode_base64_var(syt_match.group(1))

    if not request_url or not path_suffix:
        print("Failed to decode video URL variables")
        return ""

    # Construct full video URL
    video_url = "{}/{}".format(request_url, path_suffix)
    print("Decoded video URL from JavaScript: {}".format(video_url))
    return video_url


# Test with the saved HTML
with open("/tmp/peachurnet_video.html", "r", encoding="utf-8") as f:
    html = f.read()

print("Testing video URL extraction...")
print("=" * 80)
video_url = _extract_peachurnet_video_url(html)

if video_url:
    print("\n✓ SUCCESS!")
    print(f"Extracted URL: {video_url}")

    # Check if it's the placeholder
    if "/data/video.mp4" in video_url:
        print("\n❌ ERROR: This is the placeholder URL!")
    else:
        print("\n✓ This is a real video URL (not the placeholder)")
else:
    print("\n❌ FAILED to extract video URL")
