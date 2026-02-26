"""
Playwright codegen wrapper that blocks ad/tracker networks.

Since `playwright codegen` CLI doesn't support route interception, this script
opens a headed browser with ad-blocking active so you can inspect the site and
manually explore what selectors/requests to use. For actual code generation,
run `playwright codegen <url>` separately and use this script first to identify
the selectors without ad interference.

Usage:
    # Explore a site with ads blocked (identify selectors, network requests):
    python scripts/codegen.py https://site.com

    # Also sniff video/stream URLs while browsing:
    python scripts/codegen.py https://site.com --sniff

    # Disable popup removal (to see what popups are present):
    python scripts/codegen.py https://site.com --no-dismiss

    # Then run official codegen (no ad blocking, but you know what to look for):
    playwright codegen https://site.com
"""

import argparse
from playwright.sync_api import sync_playwright

# Ad/tracker domains to block. Any request URL containing these strings is aborted.
BLOCKED_DOMAINS = [
    "doubleclick.net",
    "googlesyndication.com",
    "googletagmanager.com",
    "google-analytics.com",
    "adnxs.com",
    "amazon-adsystem.com",
    "trafficjunky.net",
    "trafficjunky.com",
    "juicyads.com",
    "plugrush.com",
    "exoclick.com",
    "exdynsrv.com",
    "trafficholder.com",
    "propellerads.com",
    "popcash.net",
    "popads.net",
    "bidvertiser.com",
    "hilltopads.net",
    "trafficstars.com",
    "adsterra.com",
    "ero-advertising.com",
    "tsyndicate.com",
    "taboola.com",
    "outbrain.com",
    "criteo.com",
    "rubiconproject.com",
    "openx.net",
    "pubmatic.com",
]

# Popup/overlay selectors to auto-remove after page load.
POPUP_SELECTORS = [
    ".age-gate", "#age-gate", "[class*='age-verify']", "[class*='age-gate']",
    "[class*='cookie']", "[class*='consent']", "[class*='gdpr']",
    ".cookie-banner", "#cookie-banner",
    "[id*='popup']:not(video)", "[class*='popup']:not(video)",
    "[id*='modal']", "[class*='modal']",
    "[id*='overlay']", "[class*='overlay']",
]

VIDEO_EXTENSIONS = [".mp4", ".m3u8", ".ts", ".m4s", "manifest", "/playlist", "get_sources"]

# XHR/API patterns to log response bodies for (useful for Livewire/AJAX sites).
API_PATTERNS = ["livewire/message", "api/video", "api/stream", "get_video", "source"]


def should_block(url: str) -> bool:
    lower = url.lower()
    return any(domain in lower for domain in BLOCKED_DOMAINS)


def main():
    parser = argparse.ArgumentParser(
        description="Open a site with ads blocked for selector/network exploration"
    )
    parser.add_argument("url", help="Site URL to open")
    parser.add_argument(
        "--sniff", action="store_true",
        help="Print video/stream URLs as they are detected"
    )
    parser.add_argument(
        "--no-dismiss", action="store_true",
        help="Skip auto-dismissing popups/overlays"
    )
    parser.add_argument(
        "--no-block", action="store_true",
        help="Disable ad/tracker blocking"
    )
    parser.add_argument(
        "--dump-page", metavar="FILE",
        help="After load, save the fully-rendered page HTML to FILE for offline inspection"
    )
    args = parser.parse_args()

    found_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
        )

        # Create the main page first, then register the popup-closer so it only
        # fires for pages opened AFTER this one (not the main page itself).
        page = context.new_page()

        # Auto-close any new tab/window that opens (window.open, target="_blank").
        # This is the main source of popup ads on adult sites.
        if not args.no_block:
            def on_new_page(new_page):
                try:
                    new_page.close()
                except Exception:
                    pass

            context.on("page", on_new_page)

        if not args.no_block:
            def route_handler(route):
                if should_block(route.request.url):
                    route.abort()
                else:
                    route.continue_()

            context.route("**/*", route_handler)
            print(f"[*] Blocking {len(BLOCKED_DOMAINS)} ad/tracker domain patterns")
            print(f"[*] Auto-closing popup windows")

        if args.sniff:
            def handle_response(response):
                url = response.url
                lower = url.lower()
                if any(ext in lower for ext in VIDEO_EXTENSIONS):
                    if url not in found_urls:
                        found_urls.append(url)
                        print(f"[>>] VIDEO: {url}")
                elif any(pat in lower for pat in API_PATTERNS):
                    try:
                        body = response.text()
                        # Truncate large responses but show enough to be useful
                        preview = body[:800].replace("\n", " ")
                        print(f"[API] {url}\n      {preview}\n")
                    except Exception:
                        pass

            page.on("response", handle_response)

        # Inject before every page navigation to kill window.open at the JS level.
        if not args.no_block:
            context.add_init_script("""
                window.open = function() { return null; };
                Object.defineProperty(window, 'open', {
                    value: function() { return null; },
                    writable: false
                });
            """)

        print(f"[*] Opening: {args.url}")
        try:
            page.goto(args.url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"[!] Navigation error: {e}")

        if args.dump_page:
            page.wait_for_timeout(2000)
            html = page.content()
            with open(args.dump_page, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[*] Page HTML saved to: {args.dump_page}")

        if not args.no_dismiss:
            page.wait_for_timeout(1500)
            dismissed = 0
            for selector in POPUP_SELECTORS:
                try:
                    for el in page.locator(selector).all():
                        if el.is_visible():
                            el.evaluate("el => el.remove()")
                            dismissed += 1
                except Exception:
                    pass
            if dismissed:
                print(f"[*] Dismissed {dismissed} popup/overlay element(s)")

        print("[*] Browser open. Explore the site, then close the window to exit.")
        print("[*] Tip: open DevTools → Elements to find CSS selectors")
        if args.sniff:
            print("[*] Sniffing video/stream URLs...")
        print()

        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass

        if found_urls:
            print(f"\n[*] Found {len(found_urls)} stream URL(s):")
            for u in found_urls:
                print(f"    {u}")

        browser.close()


if __name__ == "__main__":
    main()
