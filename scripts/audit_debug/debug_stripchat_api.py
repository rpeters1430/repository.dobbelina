import json
import os
import subprocess
import sys
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
    HAS_PY_PLAYWRIGHT = True
except Exception:
    sync_playwright = None
    HAS_PY_PLAYWRIGHT = False


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)


def _short_headers(headers):
    keep = (
        "user-agent",
        "referer",
        "origin",
        "accept",
        "cookie",
        "sec-fetch-site",
        "sec-fetch-mode",
    )
    out = {}
    for key, value in headers.items():
        lower = key.lower()
        if lower in keep:
            if lower == "cookie" and len(value) > 200:
                out[key] = value[:200] + "...<trimmed>"
            else:
                out[key] = value
    return out


def run(url):
    if not HAS_PY_PLAYWRIGHT:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(script_dir, "debug_stripchat_api.js")
        print("[*] Python Playwright not installed, falling back to Node: {}".format(js_path))
        result = subprocess.run(
            ["node", js_path, url],
            cwd=script_dir,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        return

    print("[*] Analyzing browser traffic for: {}".format(url))
    print("[*] This runs outside Kodi and prints the real browser media requests.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=UA,
        )
        page = context.new_page()

        seen = set()
        media_events = []
        target_host = urlparse(url).netloc.lower()
        stop_early = {"armed": False}

        def log_media_event(kind, request, response=None, body_text=None):
            req_url = request.url
            if req_url in seen:
                return
            seen.add(req_url)

            lower = req_url.lower()
            if not any(ext in lower for ext in (".m3u8", ".mp4", ".m4s")):
                return
            if any(x in lower for x in ("/thumbs/", "/images/", ".jpg", ".png", "/image/", "/thumb/")):
                return

            event = {
                "kind": kind,
                "url": req_url,
                "method": request.method,
                "resource_type": request.resource_type,
                "headers": _short_headers(request.headers),
            }
            if response is not None:
                event["status"] = response.status
                event["response_headers"] = _short_headers(response.headers)
            if body_text is not None:
                event["body_preview"] = body_text[:800]

            media_events.append(event)
            if response is not None and response.status == 200:
                stop_early["armed"] = True

            print("\n[MEDIA {}] {}".format(kind.upper(), req_url))
            print("  method={} type={}".format(request.method, request.resource_type))
            if response is not None:
                print("  status={}".format(response.status))
            if event["headers"]:
                print("  request_headers={}".format(json.dumps(event["headers"], indent=2)))
            if response is not None and event.get("response_headers"):
                print(
                    "  response_headers={}".format(
                        json.dumps(event["response_headers"], indent=2)
                    )
                )
            if body_text:
                if "#EXT-X-MOUFLON" in body_text:
                    print("  manifest_type=MOUFLON")
                elif "#EXTM3U" in body_text:
                    print("  manifest_type=STANDARD")
                print("  body_preview={}".format(body_text[:400].replace("\n", "\\n")))

        def handle_request(request):
            lower = request.url.lower()
            if target_host in lower and "widget" in lower:
                print("\n[API REQUEST] {}".format(request.url))
            if any(ext in lower for ext in (".m3u8", ".mp4", ".m4s")):
                log_media_event("request", request)

        def handle_response(response):
            request = response.request
            try:
                lower = response.url.lower()
                ct = response.headers.get("content-type", "").lower()

                if target_host in lower and "application/json" in ct:
                    try:
                        data = response.json()
                        if "stream" in str(data).lower() or "hls" in str(data).lower():
                            print("\n[API JSON] {}".format(response.url))
                            print(json.dumps(data, indent=2)[:1500])
                    except Exception:
                        pass

                body_text = None
                if ".m3u8" in lower:
                    try:
                        body_text = response.text()
                    except Exception:
                        body_text = None

                if any(ext in lower for ext in (".m3u8", ".mp4", ".m4s")):
                    log_media_event("response", request, response=response, body_text=body_text)
            except Exception as exc:
                print("[!] response handler error: {}".format(exc))

        page.on("request", handle_request)
        page.on("response", handle_response)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print("[*] Page loaded")
            page.wait_for_timeout(3000)

            play_selectors = [
                "video",
                "button",
                ".vjs-big-play-button",
                ".play-button",
                "[data-test='video-play-button']",
            ]
            for selector in play_selectors:
                try:
                    locator = page.locator(selector).first
                    if locator.is_visible(timeout=1000):
                        print("[*] Clicking {}...".format(selector))
                        locator.click(force=True, timeout=3000)
                        page.wait_for_timeout(2000)
                except Exception:
                    continue

            print("[*] Waiting up to 15s for media traffic...")
            for _ in range(15):
                page.wait_for_timeout(1000)
                if stop_early["armed"]:
                    print("[*] Captured successful media response, stopping early.")
                    break

            print("\n[*] Media event count: {}".format(len(media_events)))
            print("[*] Unique media URLs captured:")
            for event in media_events:
                print(" - {} {} {}".format(
                    event["kind"].upper(),
                    event.get("status", ""),
                    event["url"],
                ).rstrip())
        finally:
            browser.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://stripchat.com/RussianWoman"
    run(target)
