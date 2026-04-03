#!/usr/bin/env python3
"""Probe live listing pages with Playwright and summarize visible cards."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from playwright.sync_api import sync_playwright


PRESET_URLS = {
    "thothub": [
        "https://thothub.mx/latest-updates/",
        "https://thothub.mx/public/",
        "https://thothub.mx/search/test/",
    ],
}


@dataclass
class ProbeResult:
    url: str
    landed_url: str
    title: str
    total_items: int
    video_links: int
    private_items: int
    public_estimate: int
    titles: list[str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect listing pages with Playwright and print card counts."
    )
    parser.add_argument(
        "--site",
        choices=sorted(PRESET_URLS),
        help="Use a built-in URL set for a supported site.",
    )
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="Probe a specific URL. Pass multiple times to inspect several pages.",
    )
    parser.add_argument(
        "--selector",
        default=".list-videos .item",
        help="CSS selector for listing cards.",
    )
    parser.add_argument(
        "--video-selector",
        default='.list-videos .item a[href*="/videos/"]',
        help="CSS selector for video links inside cards.",
    )
    parser.add_argument(
        "--private-selector",
        default=".list-videos .item.private, .list-videos .item:has(.line-private)",
        help="CSS selector that identifies private cards.",
    )
    parser.add_argument(
        "--title-limit",
        type=int,
        default=8,
        help="Number of titles to print per page.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=3000,
        help="Extra time to wait after DOMContentLoaded.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=30000,
        help="Per-page timeout in milliseconds.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run Chromium with a visible window.",
    )
    return parser


def resolve_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    if args.site:
        urls.extend(PRESET_URLS[args.site])
    if args.urls:
        urls.extend(args.urls)
    if not urls:
        raise SystemExit("Provide --site or at least one --url.")
    return urls


def collect_titles(locator, limit: int) -> list[str]:
    titles: list[str] = []
    for idx in range(min(locator.count(), limit)):
        link = locator.nth(idx)
        title = link.get_attribute("title") or link.inner_text()
        cleaned = " ".join((title or "").split())
        if cleaned:
            titles.append(cleaned)
    return titles


def probe_page(page, url: str, args: argparse.Namespace) -> ProbeResult:
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(args.wait_ms)

    cards = page.locator(args.selector)
    videos = page.locator(args.video_selector)
    private_items = page.locator(args.private_selector)

    video_count = videos.count()
    private_count = private_items.count()

    return ProbeResult(
        url=url,
        landed_url=page.url,
        title=page.title(),
        total_items=cards.count(),
        video_links=video_count,
        private_items=private_count,
        public_estimate=max(video_count - private_count, 0),
        titles=collect_titles(videos, args.title_limit),
    )


def print_result(result: ProbeResult) -> None:
    print(f"URL: {result.url}")
    print(f"LANDED: {result.landed_url}")
    print(f"TITLE: {result.title}")
    print(
        "ITEMS:",
        f"total={result.total_items}",
        f"video_links={result.video_links}",
        f"private={result.private_items}",
        f"public_est={result.public_estimate}",
    )
    if result.titles:
        print("FIRST_TITLES:")
        for index, title in enumerate(result.titles, start=1):
            print(f"  {index}. {title}")
    print("---")


def main() -> int:
    args = build_parser().parse_args()
    urls = resolve_urls(args)
    os.environ.setdefault("CUMINATION_ALLOW_PLAYWRIGHT", "1")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page(viewport={"width": 1440, "height": 2200})
        page.set_default_timeout(args.timeout_ms)
        for url in urls:
            print_result(probe_page(page, url, args))
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
