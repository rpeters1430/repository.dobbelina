"""
Live diagnostic for the Stripchat MOUFLON segment-availability race, as hit
via LemonCams -> stripchat.py's live proxy.

NOTE: lemoncams.com's own model page embeds a 3rd-party affiliate widget
(embedUrl points at creative.whitetrafsa.com/widgets/Player/lib.js) whose
domain currently has no DNS records at all -- it never loads real video, so
there is nothing to sniff by opening lemoncams.com in a browser. Our addon
already works around this: lemoncams.py's _extract_playable_url() rejects
that embedUrl (it's not a .m3u8/.mp4/manifest URL) and falls through to
_play_stripchat_model(username), which resolves the model directly against
stripchat.com and Stripchat's own doppiocdn CDN. That's the path this
script actually exercises by default (--site stripchat) -- it's the one
that matches what the addon does, even when the entry point was LemonCams.

This opens the model's page in a real browser and watches two things:

  1. Real segment fetches: every .mp4 request lemoncams.com's own player
     issues against media-hls*.doppiocdn.* and the actual HTTP status the
     CDN gave it back. This is the ground truth for "does it work on their
     site right now."
  2. Manifest contents: every #EXT-X-MOUFLON:URI line in the LL-HLS media
     playlists it fetches, independently re-probed with a direct HTTP
     request (Referer/Origin taken from the actual page we loaded) so we
     can see segments the player *listed* but never got around to
     requesting before they expired.

Each is logged as "full" (no _partN suffix) or "part", with HTTP status and
timing. This exists to check whether our stripchat.py proxy's
"prefer_full_segments=False" fix matches what lemoncams.com's own player is
actually seeing succeed/fail right now.

Usage:
    python scripts/verify_stripchat_playback.py <username> [--site lemoncams|stripchat] [--duration 45] [--headed] [--out results.json]

Examples:
    python scripts/verify_stripchat_playback.py nicdani_1
    python scripts/verify_stripchat_playback.py https://www.lemoncams.com/stripchat/some_model --duration 60
    python scripts/verify_stripchat_playback.py some_model --site stripchat
"""

import argparse
import json
import re
import time
from urllib.parse import urlparse

import requests
from playwright.sync_api import sync_playwright

STREAM_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)

MOUFLON_URI_RE = re.compile(r"#EXT-X-MOUFLON:URI:(\S+)")

SITE_URL_BUILDERS = {
    "lemoncams": lambda username: f"https://www.lemoncams.com/stripchat/{username}",
    "stripchat": lambda username: f"https://stripchat.com/{username}",
}


def _classify(url):
    return "part" if "_part" in url or re.search(r"part\d", url) else "full"


def _short(url, n=100):
    return url if len(url) <= n else url[:n] + "..."


def probe_segment(session, url, referer_origin, listed_at):
    """Fetch one segment/part URL and report status + latency since listing."""
    t0 = time.monotonic()
    try:
        resp = session.get(
            url,
            headers={
                "User-Agent": STREAM_UA,
                "Referer": referer_origin + "/",
                "Origin": referer_origin,
            },
            timeout=6,
            stream=True,
        )
        status = resp.status_code
        resp.close()
    except Exception as e:
        status = f"ERR({e})"
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    since_listed_ms = int((time.monotonic() - listed_at) * 1000)
    return status, elapsed_ms, since_listed_ms


def run(target, site="lemoncams", duration=45, headed=False, out_path=None):
    if target.startswith("http"):
        url = target
    else:
        url = SITE_URL_BUILDERS[site](target)
    page_origin = "{0.scheme}://{0.netloc}".format(urlparse(url))
    print(f"[*] Target: {url}")
    print(f"[*] Watching for {duration}s of segment/manifest activity...\n")

    session = requests.Session()
    seen_segments = set()
    results = []
    counts = {
        "full": {"ok": 0, "fail": 0},
        "part": {"ok": 0, "fail": 0},
    }
    live_counts = {
        "full": {"ok": 0, "fail": 0},
        "part": {"ok": 0, "fail": 0},
    }

    def handle_live_segment(response):
        """Track the real segment requests the page's own player makes."""
        resp_url = response.url
        if not (".mp4" in resp_url and ("doppiocdn" in resp_url or "media-hls" in resp_url)):
            return
        kind = _classify(resp_url)
        ok = response.status == 200
        live_counts[kind]["ok" if ok else "fail"] += 1
        tag = "LIVE-OK " if ok else f"LIVE-{response.status}"
        print(f"[{tag}] {kind:<4} {_short(resp_url)}")

    def handle_manifest(response):
        resp_url = response.url
        if "media-hls." not in resp_url or ".m3u8" not in resp_url:
            return
        try:
            body = response.text()
        except Exception:
            return
        if "#EXT-X-MOUFLON:URI:" not in body:
            return

        listed_at = time.monotonic()
        base = resp_url.rsplit("/", 1)[0] + "/"
        for match in MOUFLON_URI_RE.finditer(body):
            seg_url = match.group(1).strip()
            if not seg_url.startswith("http"):
                seg_url = base + seg_url.lstrip("/")
            if seg_url in seen_segments:
                continue
            seen_segments.add(seg_url)

            kind = _classify(seg_url)
            status, probe_ms, since_listed_ms = probe_segment(
                session, seg_url, page_origin, listed_at
            )
            ok = status == 200
            counts[kind]["ok" if ok else "fail"] += 1

            tag = "OK " if ok else "404" if status == 404 else "ERR"
            print(
                f"[{tag}] {kind:<4} status={status!s:<12} "
                f"probe={probe_ms:>4}ms since_listed={since_listed_ms:>4}ms "
                f"{_short(seg_url)}"
            )
            results.append(
                {
                    "url": seg_url,
                    "kind": kind,
                    "status": status,
                    "probe_ms": probe_ms,
                    "since_listed_ms": since_listed_ms,
                    "playlist": resp_url,
                }
            )

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=STREAM_UA,
        )
        page = context.new_page()
        page.on("response", handle_live_segment)
        page.on("response", handle_manifest)

        try:
            page.goto(url, wait_until="load", timeout=60000)
            page.wait_for_timeout(4000)

            for selector in [
                "video",
                ".vjs-big-play-button",
                ".play-button",
                "iframe",
            ]:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible():
                        print(f"[*] Clicking {selector} to start playback...")
                        loc.click()
                        page.wait_for_timeout(1500)
                except Exception:
                    continue

            page.wait_for_timeout(duration * 1000)
        except Exception as e:
            print(f"[!] Error during navigation: {e}")
        finally:
            browser.close()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nLive requests actually made by {url}'s own player:")
    live_total = sum(live_counts[k]["ok"] + live_counts[k]["fail"] for k in live_counts)
    if live_total == 0:
        print(
            "  No .mp4 segment requests were observed at all -- the player "
            "may not have started, or the stream may be offline/geo-blocked. "
            "Try --headed to watch it happen."
        )
    else:
        for kind in ("full", "part"):
            ok, fail = live_counts[kind]["ok"], live_counts[kind]["fail"]
            total = ok + fail
            rate = f"{100 * ok / total:.0f}%" if total else "n/a"
            print(f"  {kind:<4}: {ok:>3} ok / {fail:>3} fail  (of {total:<3}, success rate {rate})")
        live_ok = live_counts["full"]["ok"] + live_counts["part"]["ok"]
        if live_ok == 0:
            print(
                "  -> The player never got a single segment through. "
                "Playback is genuinely broken on lemoncams.com right now, "
                "not just in our addon."
            )
        elif live_counts["full"]["fail"] > 0 and live_counts["full"]["fail"] >= live_counts["full"]["ok"]:
            print(
                "  -> Full segments are failing for their own player too -- "
                "not addon-specific. Matches the case our stripchat.py fix "
                "targets."
            )

    print("\nManifest-listed segments, independently re-probed:")
    total_ok = counts["full"]["ok"] + counts["part"]["ok"]
    total_seen = sum(counts[k]["ok"] + counts[k]["fail"] for k in counts)
    if total_seen == 0:
        print(
            "  No MOUFLON media playlists were captured (the player may be "
            "using a different manifest shape, or none loaded)."
        )
    else:
        for kind in ("full", "part"):
            ok, fail = counts[kind]["ok"], counts[kind]["fail"]
            total = ok + fail
            rate = f"{100 * ok / total:.0f}%" if total else "n/a"
            print(f"  {kind:<4}: {ok:>3} ok / {fail:>3} fail  (of {total:<3}, success rate {rate})")
        print(f"  overall: {total_ok}/{total_seen} segment probes succeeded")
        if counts["part"]["ok"] > counts["full"]["ok"] and counts["full"]["fail"] > 0:
            print(
                "  -> Parts are outperforming full segments, consistent with "
                "prefer_full_segments=False in stripchat.py's live proxy."
            )
        elif counts["full"]["fail"] == 0 and counts["full"]["ok"] > 0:
            print(
                "  -> Full segments are succeeding here; the part-preference "
                "fix should still be harmless but may not be strictly needed "
                "for this model/session."
            )

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "target": url,
                    "live_counts": live_counts,
                    "counts": counts,
                    "results": results,
                },
                f,
                indent=2,
            )
        print(f"\n[*] Wrote {len(results)} probe records to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("target", help="Model username, or a full lemoncams.com/stripchat.com URL")
    parser.add_argument(
        "--site",
        choices=sorted(SITE_URL_BUILDERS),
        default="stripchat",
        help=(
            "Which site to build the URL for when target is a bare username "
            "(default: stripchat). Note: lemoncams.com's own model page "
            "embeds a 3rd-party affiliate widget (creative.whitetrafsa.com) "
            "whose domain is currently unresolvable in DNS -- it never "
            "loads real video, so there's nothing to sniff there. Our addon "
            "already detects this (lemoncams.py's embedUrl doesn't look "
            "like a stream) and resolves the model directly against "
            "stripchat.com instead, which is what --site stripchat mirrors."
        ),
    )
    parser.add_argument("--duration", type=int, default=45, help="Seconds to watch (default 45)")
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    parser.add_argument("--out", help="Optional path to write raw results as JSON")
    args = parser.parse_args()

    run(
        args.target,
        site=args.site,
        duration=args.duration,
        headed=args.headed,
        out_path=args.out,
    )
