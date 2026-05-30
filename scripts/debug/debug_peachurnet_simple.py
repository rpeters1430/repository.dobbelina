#!/usr/bin/env python3
"""
Simple diagnostic script for peachurnet.com parsing issues.
Uses requests and BeautifulSoup directly without Kodi dependencies.
"""

import requests
from bs4 import BeautifulSoup
import re


def diagnose_listing_page(url="https://peachurnet.com/en"):
    """Diagnose issues with video listing page."""
    print(f"\n{'=' * 80}")
    print(f"DIAGNOSING LISTING PAGE: {url}")
    print(f"{'=' * 80}\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://peachurnet.com/",
        "Origin": "https://peachurnet.com",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        html = response.text
        print(f"✓ Successfully fetched HTML ({len(html)} bytes)\n")
    except Exception as e:
        print(f"✗ Failed to fetch page: {e}")
        return

    # Save raw HTML for inspection
    with open("/tmp/peachurnet_listing.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Saved raw HTML to /tmp/peachurnet_listing.html\n")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find all video links
    video_links = soup.select('a[href*="/video/"]')
    print(f'Found {len(video_links)} video links with selector: a[href*="/video/"]\n')

    if not video_links:
        print("⚠ No video links found! Trying alternative selectors...")
        video_links = soup.find_all("a", href=lambda x: x and "/video" in x)
        print(f"Found {len(video_links)} video links with href containing '/video'\n")

    # Examine first few video items in detail
    for i, link in enumerate(video_links[:3], 1):
        print(f"\n--- VIDEO {i} ---")
        href = link.get("href", "")
        print(f"URL: {href}")

        # Show what's inside the link
        print(f"\nLink HTML structure:")
        print(link.prettify()[:800])

        # Try to find title in various ways
        print(f"\nSearching for title:")
        for selector in [
            ".title",
            ".video-title",
            "h3",
            "h2",
            "h4",
            "p",
            "span",
            "div",
        ]:
            elem = link.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) > 2:
                    print(f"  {selector}: '{text}'")

        # Check link text directly
        link_text = link.get_text(strip=True)
        print(f"  Direct link text: '{link_text[:100]}'")

        # Check for title in attributes
        if link.get("title"):
            print(f"  title attribute: '{link.get('title')}'")
        if link.get("aria-label"):
            print(f"  aria-label: '{link.get('aria-label')}'")

        # Try thumbnail
        img = link.select_one("img")
        if img:
            src = img.get("src") or img.get("data-src") or img.get("data-original")
            print(f"\nThumbnail img: {src}")
            print(f"  alt: '{img.get('alt', '')}'")

        # Try duration
        duration_elem = link.find(class_=re.compile(r"duration|length", re.I))
        if duration_elem:
            print(f"Duration: {duration_elem.get_text(strip=True)}")

        print(f"\n{'─' * 60}")


def diagnose_video_page(url):
    """Diagnose issues with video playback page."""
    print(f"\n{'=' * 80}")
    print(f"DIAGNOSING VIDEO PAGE: {url}")
    print(f"{'=' * 80}\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://peachurnet.com/",
        "Origin": "https://peachurnet.com",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        html = response.text
        print(f"✓ Successfully fetched HTML ({len(html)} bytes)\n")
    except Exception as e:
        print(f"✗ Failed to fetch page: {e}")
        return

    # Save raw HTML for inspection
    with open("/tmp/peachurnet_video.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Saved raw HTML to /tmp/peachurnet_video.html\n")

    # Parse
    soup = BeautifulSoup(html, "html.parser")

    # Check for login requirement
    if "/login" in html or "sign in" in html.lower():
        print("⚠ Page may require login/authentication\n")

    # Look for video sources
    print(f"{'=' * 80}")
    print("SEARCHING FOR VIDEO SOURCES")
    print(f"{'=' * 80}\n")

    # Video tags
    video_tags = soup.find_all("video")
    print(f"<video> tags found: {len(video_tags)}")
    for vid in video_tags[:2]:
        print(vid.prettify()[:500])

    # Source tags
    source_tags = soup.find_all("source")
    print(f"\n<source> tags found: {len(source_tags)}")
    for src in source_tags[:5]:
        print(f"  src: {src.get('src')}")
        print(f"  data-src: {src.get('data-src')}")

    # iframes
    iframes = soup.find_all("iframe")
    print(f"\n<iframe> tags found: {len(iframes)}")
    for iframe in iframes[:5]:
        print(f"  src: {iframe.get('src')}")

    # Search for video URLs in HTML
    mp4_urls = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', html, re.IGNORECASE)
    m3u8_urls = re.findall(
        r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html, re.IGNORECASE
    )

    print(f"\n.mp4 URLs found in HTML: {len(set(mp4_urls))}")
    for url in list(set(mp4_urls))[:5]:
        print(f"  {url}")

    print(f"\n.m3u8 URLs found in HTML: {len(set(m3u8_urls))}")
    for url in list(set(m3u8_urls))[:5]:
        print(f"  {url}")

    # Look for common JavaScript video players
    if "jwplayer" in html.lower():
        print("\n⚠ Site uses JW Player")
    if "videojs" in html.lower() or "video-js" in html:
        print("\n⚠ Site uses Video.js")
    if "plyr" in html.lower():
        print("\n⚠ Site uses Plyr")


if __name__ == "__main__":
    import argparse
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser(
        description="Diagnose peachurnet.com parsing issues"
    )
    parser.add_argument("--listing", action="store_true", help="Diagnose listing page")
    parser.add_argument("--video", type=str, help="Diagnose specific video page URL")

    args = parser.parse_args()

    if args.video:
        diagnose_video_page(args.video)
    elif args.listing:
        diagnose_listing_page()
    else:
        # Do both by default
        diagnose_listing_page()

        # Try to get first video URL
        try:
            response = requests.get(
                "https://peachurnet.com/en", verify=False, timeout=10
            )
            soup = BeautifulSoup(response.text, "html.parser")
            video_links = soup.select('a[href*="/video/"]')
            if video_links:
                first_href = video_links[0].get("href", "")
                if first_href.startswith("/"):
                    first_video_url = "https://peachurnet.com" + first_href
                else:
                    first_video_url = first_href
                print(f"\n\nAttempting to diagnose first video: {first_video_url}\n")
                diagnose_video_page(first_video_url)
        except Exception as e:
            print(f"\nCouldn't auto-fetch first video: {e}")
