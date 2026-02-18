#!/usr/bin/env python3
"""
Diagnostic script for peachurnet.com parsing issues.
This script fetches live pages and shows what the parser is finding.
"""

import sys
import os

# Add the plugin path to import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugin.video.cumination"))

from resources.lib.sites import peachurnet
from resources.lib import utils


def diagnose_listing_page(url="https://peachurnet.com/en"):
    """Diagnose issues with video listing page."""
    print(f"\n{'=' * 80}")
    print(f"DIAGNOSING LISTING PAGE: {url}")
    print(f"{'=' * 80}\n")

    try:
        html = utils.getHtml(url, headers=peachurnet._ensure_headers())
        print(f"✓ Successfully fetched HTML ({len(html)} bytes)\n")
    except Exception as e:
        print(f"✗ Failed to fetch page: {e}")
        return

    # Save raw HTML for inspection
    with open("/tmp/peachurnet_listing.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Saved raw HTML to /tmp/peachurnet_listing.html\n")

    # Parse with BeautifulSoup
    soup = utils.parse_html(html)

    # Find all video links
    video_links = soup.select('a[href*="/video/"]')
    print(f'Found {len(video_links)} video links with selector: a[href*="/video/"]\n')

    if not video_links:
        print("⚠ No video links found! Trying alternative selectors...")
        # Try other common patterns
        video_links = soup.find_all("a", href=lambda x: x and "/video" in x)
        print(f"Found {len(video_links)} video links with href containing '/video'\n")

    # Examine first few video items in detail
    for i, link in enumerate(video_links[:3], 1):
        print(f"\n--- VIDEO {i} ---")
        print(f"URL: {utils.safe_get_attr(link, 'href')}")

        # Try to extract title
        title = peachurnet._extract_title(link)
        print(f"Title: '{title}' {'' if title else '❌ EMPTY'}")

        # Show what's inside the link
        print(f"\nLink inner HTML (first 500 chars):")
        print(link.prettify()[:500])

        # Try to find title candidates
        print(f"\nTitle candidates:")
        for selector in [".title", ".video-title", "h3", "h2", "h4", "p", "span"]:
            elem = link.select_one(selector)
            if elem:
                text = utils.safe_get_text(elem)
                print(f"  {selector}: '{text}'")

        # Check link text directly
        link_text = utils.safe_get_text(link)
        print(f"  Direct link text: '{link_text}'")

        # Try thumbnail
        thumb = peachurnet._extract_thumbnail(link)
        print(f"\nThumbnail: {thumb if thumb else '❌ EMPTY'}")

        # Try duration
        duration = peachurnet._extract_duration(link)
        print(f"Duration: {duration if duration else '❌ EMPTY'}")

        print(f"\n{'─' * 60}")

    # Try to parse with the actual function
    print(f"\n{'=' * 80}")
    print("TESTING _parse_video_cards FUNCTION")
    print(f"{'=' * 80}\n")

    videos = peachurnet._parse_video_cards(soup)
    print(f"✓ _parse_video_cards returned {len(videos)} videos\n")

    for i, video in enumerate(videos[:5], 1):
        print(f"Video {i}:")
        print(f"  Title: {video['title']}")
        print(f"  URL: {video['url']}")
        print(
            f"  Thumb: {video['thumb'][:80]}..." if video["thumb"] else "  Thumb: EMPTY"
        )
        print(
            f"  Plot: {video['plot'][:100]}..."
            if len(video["plot"]) > 100
            else f"  Plot: {video['plot']}"
        )
        print()


def diagnose_video_page(url):
    """Diagnose issues with video playback page."""
    print(f"\n{'=' * 80}")
    print(f"DIAGNOSING VIDEO PAGE: {url}")
    print(f"{'=' * 80}\n")

    try:
        html = utils.getHtml(url, headers=peachurnet._ensure_headers())
        print(f"✓ Successfully fetched HTML ({len(html)} bytes)\n")
    except Exception as e:
        print(f"✗ Failed to fetch page: {e}")
        return

    # Save raw HTML for inspection
    with open("/tmp/peachurnet_video.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Saved raw HTML to /tmp/peachurnet_video.html\n")

    # Check for login requirement
    if "/login" in html or "sign in" in html.lower():
        print("⚠ Page may require login/authentication\n")

    # Try to extract video sources
    sources = peachurnet._gather_video_sources(html, url)

    print(f"{'=' * 80}")
    print(f"VIDEO SOURCES FOUND: {len(sources)}")
    print(f"{'=' * 80}\n")

    if sources:
        for host, url in sources.items():
            print(f"  {host}: {url}")
    else:
        print("❌ NO VIDEO SOURCES FOUND")
        print("\nSearching for common video patterns in HTML:")

        # Look for video-related elements
        soup = utils.parse_html(html)

        video_tags = soup.find_all("video")
        print(f"\n<video> tags: {len(video_tags)}")
        for vid in video_tags:
            print(f"  {vid.prettify()[:200]}")

        source_tags = soup.find_all("source")
        print(f"\n<source> tags: {len(source_tags)}")
        for src in source_tags:
            print(f"  {src.prettify()[:200]}")

        iframes = soup.find_all("iframe")
        print(f"\n<iframe> tags: {len(iframes)}")
        for iframe in iframes:
            print(f"  src: {utils.safe_get_attr(iframe, 'src')}")

        # Look for data attributes
        data_src_elements = soup.find_all(attrs={"data-src": True})
        print(f"\nElements with data-src: {len(data_src_elements)}")

        # Search for URLs in the HTML
        import re

        mp4_matches = re.findall(r'https?://[^\s"\'<>]+\.mp4', html, re.IGNORECASE)
        m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8', html, re.IGNORECASE)

        print(f"\n.mp4 URLs in HTML: {len(mp4_matches)}")
        for match in mp4_matches[:5]:
            print(f"  {match}")

        print(f"\n.m3u8 URLs in HTML: {len(m3u8_matches)}")
        for match in m3u8_matches[:5]:
            print(f"  {match}")


if __name__ == "__main__":
    import argparse

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

        # Try to get a video URL from the listing
        html = utils.getHtml(
            "https://peachurnet.com/en", headers=peachurnet._ensure_headers()
        )
        soup = utils.parse_html(html)
        video_links = soup.select('a[href*="/video/"]')
        if video_links:
            first_video_url = peachurnet._absolute_url(
                utils.safe_get_attr(video_links[0], "href")
            )
            print(f"\n\nAttempting to diagnose first video found: {first_video_url}")
            diagnose_video_page(first_video_url)
