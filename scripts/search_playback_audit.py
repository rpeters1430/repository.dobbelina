#!/usr/bin/env python3
"""Audit search, search-result playback and thumbnails for every site.

For each site this runs the live smoke harness (main, list, search, play,
search_play) in a child process. It then goes further than the harness:

* The resolved stream for the first main-list video and the first search
  result are both fetched (media_validator), so "URL resolved" is checked
  against "stream actually serves video bytes".
* Thumbnails from the main list and from the search results are fetched
  (test_site_images.probe_image), so missing or hotlink-blocked images show up.

The headline verdict is SEARCH_PLAY_BROKEN: the main list plays but search
results don't, which is what users notice most.

Usage:
  python scripts/search_playback_audit.py --all
  python scripts/search_playback_audit.py --site pornhub xvideos --keyword milf
  python scripts/search_playback_audit.py --all --workers 6 --flaresolverr http://192.168.8.143:8191/v1
  python scripts/search_playback_audit.py --rerun-failed results/search_playback_audit_latest.json

Output: results/search_playback_audit_<timestamp>.{json,md}, plus *_latest copies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import ssl
import threading
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.media_validator import validate_media  # noqa: E402
from scripts.test_site_images import probe_image  # noqa: E402

HARNESS = ROOT / "scripts" / "live_smoke_test.py"
SITES_DIR = ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
DEFAULT_FS_URL = (
    os.environ.get("FLARESOLVERR_URL")
    or os.environ.get("FS_HOST")
    or "http://192.168.8.143:8191/v1"
)
STEPS = "main,list,search,play,search_play"

# The harness's VideoPlayer stub records the page/hoster URL for these instead
# of a stream; in Kodi, resolveurl or the real VideoPlayer does the rest. We
# can't fetch a stream for them, so they are reported as UNVERIFIED.
UNVERIFIABLE_VIAS = {
    "play_from_site_link", "play_from_link_to_resolve", "play_from_kt_player", "play_from_link_list",
}

# Image probe statuses that mean the thumbnail shows up in Kodi.
IMAGE_OK = {"PASS"}

# Ordered worst-first; a site's headline verdict is its first tag in this order.
VERDICT_ORDER = [
    "HARNESS_ERROR",
    "SEARCH_PLAY_BROKEN",
    "SEARCH_BROKEN",
    "PLAY_BROKEN",
    "SEARCH_IMAGES_BROKEN",
    "IMAGES_BROKEN",
    "DNS_BLOCKED",
    "UNVERIFIED",
    "SKIPPED",
    "OK",
]
CLEAN = ("OK", "UNVERIFIED", "SKIPPED")


def list_site_modules() -> list[str]:
    excluded: set[str] = set()
    init = SITES_DIR / "__init__.py"
    if init.exists():
        text = init.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"EXCLUDED_SITE_MODULES\s*=\s*[\[{(](.*?)[\]})]", text, re.S)
        if m:
            excluded = {x.replace(".py", "") for x in re.findall(r"['\"]([\w.]+)['\"]", m.group(1))}
    return [
        p.stem
        for p in sorted(SITES_DIR.glob("*.py"))
        if not p.stem.startswith("_") and p.stem != "soup_spec" and p.stem not in excluded
    ]


def run_harness(site: str, keyword: str, step_timeout: int, site_timeout: int, env: dict) -> dict[str, Any]:
    cmd = [sys.executable, str(HARNESS), "--run-site", site, "--steps", STEPS,
           "--timeout", str(step_timeout), "--keyword", keyword]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=site_timeout, env=env, check=False)
    except subprocess.TimeoutExpired:
        return {"site": site, "overall": "ERROR", "error": f"harness timed out after {site_timeout}s", "steps": {}}
    out = (proc.stdout or "").strip()
    start = out.rfind('{"site"')
    if proc.returncode != 0 or start < 0:
        err = (proc.stderr or out or "").strip().splitlines()
        return {"site": site, "overall": "ERROR", "error": " | ".join(err[-3:])[:400], "steps": {}}
    try:
        return json.loads(out[start:])
    except json.JSONDecodeError as exc:
        return {"site": site, "overall": "ERROR", "error": f"bad harness JSON: {exc}", "steps": {}}


_block_cache: dict[str, str] = {}
_block_lock = threading.Lock()
BLOCKPAGE_MARKERS = (b"NextDNS", b"blockpage", b"Pi-hole", b"AdGuard", b"OpenDNS", b"Cisco Umbrella")


def dns_block(url: str) -> str:
    """Name of the DNS filter that answers for this host instead of the real server, or ''.

    A filtering resolver (NextDNS etc.) hands back its own blockpage, so the
    TLS cert is issued by the filter. Kodi on the same network fails the same way.
    """
    host = urlparse(url.split("|")[0]).hostname or ""
    if not host:
        return ""
    with _block_lock:
        if host in _block_cache:
            return _block_cache[host]
    found = ""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, 443), timeout=6) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                der = tls.getpeercert(binary_form=True) or b""
        found = next((m.decode() for m in BLOCKPAGE_MARKERS if m.lower() in der.lower()), "")
    except Exception:
        pass
    with _block_lock:
        _block_cache[host] = found
    return found


def check_stream(step: dict[str, Any], media_timeout: float) -> dict[str, Any]:
    """Turn a play/search_play step into OK / BROKEN / UNVERIFIED / FAIL / SKIP."""
    status = step.get("status", "SKIP")
    info: dict[str, Any] = {
        "step_status": status,
        "message": step.get("message", ""),
        "play_url": step.get("play_url", ""),
        "play_via": step.get("play_via", ""),
        "played_mode": step.get("played_mode", ""),
        "played_item_url": step.get("played_item_url", ""),
    }
    if status != "PASS":
        info["result"] = status  # FAIL or SKIP from the harness
        return info
    url, via = info["play_url"], info["play_via"]
    if via in UNVERIFIABLE_VIAS or not url.lower().startswith("http"):
        info["result"] = "UNVERIFIED"
        info["message"] = f"handed to {via or 'player'} (hoster/resolveurl in Kodi; stream not fetchable here)"
        return info
    res = validate_media(url, [], timeout=media_timeout)
    if res.passed:
        info["result"] = "OK"
        info["message"] = res.message
    elif res.classification == "HTML_PAYLOAD" and url.split("|")[0] == info["played_item_url"].split("|")[0]:
        # The site passed its own video page to the player, which only works if
        # resolveurl can handle the site. Not a stream we can verify.
        info["result"] = "UNVERIFIED"
        info["message"] = "player got the video page itself (relies on resolveurl)"
    elif blocker := dns_block(url):
        info["result"] = "DNS_BLOCKED"
        info["message"] = f"{urlparse(url).hostname} is blocked by {blocker} on this network"
    else:
        info["result"] = "BROKEN"
        info["message"] = f"{res.classification}: {res.message}"
    return info


def check_images(step: dict[str, Any], base_url: str, samples: int, timeout: float) -> dict[str, Any]:
    videos = int(step.get("video_items", 0) or 0)
    with_icon = int(step.get("image_items", 0) or 0)
    probes = []
    for url in list(step.get("thumbs") or [])[:samples]:
        if not url.lower().startswith(("http", "//", "data:")) and os.path.isfile(url):
            # Site cached the thumbnail locally (e.g. ecamrips); Kodi loads it from disk.
            probes.append({"url": url[:200], "status": "PASS", "http": 0, "error": "local cached file"})
            continue
        try:
            r = probe_image(url, site_url=base_url, timeout=timeout)
            status, error = r.status, r.error_message
            if status not in IMAGE_OK and url.lower().startswith("http") and (blocker := dns_block(url)):
                status, error = "DNS_BLOCKED", f"{urlparse(url).hostname} blocked by {blocker}"
            probes.append({"url": url[:200], "status": status, "http": r.http_code, "error": error})
        except Exception as exc:  # a probe must never kill the audit
            probes.append({"url": url[:200], "status": "ERROR", "http": 0, "error": f"{type(exc).__name__}: {exc}"})
    ok = sum(1 for p in probes if p["status"] in IMAGE_OK)
    if videos == 0:
        result = "N/A"
    elif with_icon == 0:
        result = "MISSING"
    elif not probes:
        result = "N/A"
    elif ok == len(probes):
        result = "OK"
    elif all(p["status"] in IMAGE_OK | {"DNS_BLOCKED"} for p in probes):
        result = "DNS_BLOCKED"
    elif ok == 0:
        result = "BROKEN"
    else:
        result = "PARTIAL"
    return {"result": result, "videos": videos, "with_icon": with_icon,
            "probed": len(probes), "loaded": ok, "probes": probes}


def _img_reason(label: str, img: dict[str, Any]) -> str:
    worst = next((p for p in img.get("probes", []) if p["status"] not in IMAGE_OK), None)
    why = f": {worst['status']} {worst.get('error', '')}".rstrip() if worst else ""
    return (f"{label} thumbs {img['result']} ({img['loaded']}/{img['probed']} loaded, "
            f"{img['with_icon']}/{img['videos']} items have one){why}")


def verdict_for(rec: dict[str, Any]) -> tuple[str, list[str]]:
    if rec.get("harness_error"):
        rec["tags"] = ["HARNESS_ERROR"]
        return "HARNESS_ERROR", [rec["harness_error"]]
    reasons: list[str] = []
    steps = rec["steps"]
    lp, sp = rec["list_play"]["result"], rec["search_play"]["result"]
    li, si = rec["list_images"]["result"], rec["search_images"]["result"]
    search_status = steps.get("search", {}).get("status", "SKIP")
    bad_play, good_play = {"FAIL", "BROKEN"}, {"OK", "UNVERIFIED"}
    bad_img = {"BROKEN", "MISSING", "PARTIAL"}

    tags: set[str] = set()
    if sp in bad_play and lp in good_play and search_status == "PASS":
        tags.add("SEARCH_PLAY_BROKEN")
        reasons.append(f"main list plays ({lp}) but search result doesn't: {rec['search_play']['message']}")
    if search_status == "FAIL":
        tags.add("SEARCH_BROKEN")
        reasons.append(f"search: {steps['search'].get('message', '')}")
    if lp in bad_play:
        tags.add("PLAY_BROKEN")
        reasons.append(f"main-list play: {rec['list_play']['message']}")
        if sp in bad_play:
            reasons.append(f"search play: {rec['search_play']['message']}")
    if si in bad_img:
        tags.add("SEARCH_IMAGES_BROKEN")
        reasons.append(_img_reason("search", rec["search_images"]))
    if li in bad_img:
        tags.add("IMAGES_BROKEN")
        reasons.append(_img_reason("list", rec["list_images"]))
    if "DNS_BLOCKED" in (lp, sp, li, si):
        tags.add("DNS_BLOCKED")
        for key, label in (("list_play", "main-list stream"), ("search_play", "search stream")):
            if rec[key]["result"] == "DNS_BLOCKED":
                reasons.append(f"{label}: {rec[key]['message']}")
        for key, label in (("list_images", "list"), ("search_images", "search")):
            if rec[key]["result"] == "DNS_BLOCKED":
                reasons.append(_img_reason(label, rec[key]))
    if "UNVERIFIED" in (lp, sp):
        tags.add("UNVERIFIED")
    if not tags:
        if lp == "SKIP" and sp == "SKIP" and search_status == "SKIP":
            tags.add("SKIPPED")
            reasons.append(steps.get("search", {}).get("message", "") or rec["list_play"]["message"])
        else:
            tags.add("OK")
    rec["tags"] = sorted(tags, key=VERDICT_ORDER.index)
    return rec["tags"][0], reasons


def audit_site(site: str, args: argparse.Namespace, env: dict) -> dict[str, Any]:
    t0 = time.time()
    raw = run_harness(site, args.keyword, args.timeout, args.site_timeout, env)
    steps = raw.get("steps", {}) or {}
    base_url = raw.get("base_url", "")
    rec: dict[str, Any] = {"site": site, "title": raw.get("title", site), "base_url": base_url, "steps": steps}
    if raw.get("overall") == "ERROR" and not steps:
        rec["harness_error"] = raw.get("error", "unknown harness error")
        rec["list_play"] = {"result": "SKIP", "message": ""}
        rec["search_play"] = {"result": "SKIP", "message": ""}
        rec["list_images"] = {"result": "N/A"}
        rec["search_images"] = {"result": "N/A"}
    else:
        rec["list_play"] = check_stream(steps.get("play", {}), args.media_timeout)
        rec["search_play"] = check_stream(steps.get("search_play", {}), args.media_timeout)
        list_step = steps.get("list", {})
        if list_step.get("status") != "PASS":
            list_step = steps.get("main", {})
        rec["list_images"] = check_images(list_step, base_url, args.samples, args.media_timeout)
        rec["search_images"] = check_images(steps.get("search", {}), base_url, args.samples, args.media_timeout)
        rec["notifications"] = raw.get("notifications", [])
    rec["verdict"], rec["reasons"] = verdict_for(rec)
    rec["elapsed"] = round(time.time() - t0, 1)
    return rec


SHORT = {"DNS_BLOCKED": "DNSBLK", "OK": "ok", "UNVERIFIED": "unver", "BROKEN": "BROKEN", "FAIL": "FAIL", "SKIP": "skip",
         "MISSING": "MISSING", "PARTIAL": "partial", "N/A": "-"}


def fmt_line(idx: int, total: int, rec: dict[str, Any]) -> str:
    def s(key: str) -> str:
        return SHORT.get(rec[key]["result"], rec[key]["result"])

    search = rec["steps"].get("search", {}).get("status", "-") if rec["steps"] else "-"
    return (f"[{idx:>3}/{total}] {rec['site']:<22} {rec['verdict']:<21} "
            f"search={search:<4} play={s('list_play'):<6} search_play={s('search_play'):<6} "
            f"imgs={s('list_images'):<7} search_imgs={s('search_images'):<7} ({rec['elapsed']}s)")


def render_markdown(records: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    counts: dict[str, int] = {}
    for r in records:
        for t in r.get("tags", [r["verdict"]]):
            counts[t] = counts.get(t, 0) + 1
    lines = [
        "# Search / Playback / Thumbnail Audit",
        "",
        f"- Run: {meta['started']} ({meta['duration_s']}s), keyword `{meta['keyword']}`, {len(records)} sites",
        f"- FlareSolverr: {meta['flaresolverr']} ({'available' if meta['fs_available'] else 'NOT available'})",
        "",
        "| Issue | Sites |",
        "|---|---|",
    ]
    lines += [f"| {v} | {counts[v]} |" for v in VERDICT_ORDER if counts.get(v)]
    lines += [
        "",
        "Legend: **OK** stream fetched and serves video · **UNVERIFIED** handed to a hoster/resolveurl, "
        "can't be fetched outside Kodi · **BROKEN** resolved URL doesn't serve video · **FAIL** no URL resolved · "
        "**DNS_BLOCKED** your DNS filter answers for the CDN host · images **MISSING** = items carry no thumbnail, **BROKEN/PARTIAL** = thumbnail URLs don't load.",
        "",
    ]
    sections = [
        ("Search results don't play (main list does)", "SEARCH_PLAY_BROKEN"),
        ("Search returns nothing", "SEARCH_BROKEN"),
        ("Main-list playback broken", "PLAY_BROKEN"),
        ("Search thumbnails broken", "SEARCH_IMAGES_BROKEN"),
        ("Main-list thumbnails broken", "IMAGES_BROKEN"),
        ("Blocked by DNS filter on this network (NextDNS etc.) - not a site bug", "DNS_BLOCKED"),
        ("Harness errors", "HARNESS_ERROR"),
    ]
    for title, tag in sections:
        rows = [r for r in records if tag in r.get("tags", [])]
        if not rows:
            continue
        lines += [f"## {title} ({len(rows)})", "", "| Site | Detail | Played search item |", "|---|---|---|"]
        for r in sorted(rows, key=lambda x: x["site"]):
            detail = "; ".join(r["reasons"]).replace("|", "\\|")[:300]
            sp = r.get("search_play", {})
            lines.append(f"| {r['site']} | {detail} | `{sp.get('played_mode', '')}` {sp.get('played_item_url', '')[:90]} |")
        lines.append("")
    lines += ["## All sites", "", "| Site | Verdict | Search | Play | Search play | Imgs | Search imgs |",
              "|---|---|---|---|---|---|---|"]
    for r in sorted(records, key=lambda x: (VERDICT_ORDER.index(x["verdict"]), x["site"])):
        search = r["steps"].get("search", {}).get("status", "-") if r["steps"] else "-"
        lines.append(f"| {r['site']} | {r['verdict']} | {search} | {r['list_play']['result']} | "
                     f"{r['search_play']['result']} | {r['list_images']['result']} | {r['search_images']['result']} |")
    return "\n".join(lines) + "\n"


def probe_fs(url: str) -> bool:
    req = urllib.request.Request(url, data=json.dumps({"cmd": "sessions.list"}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read() or b"{}").get("status") == "ok"
    except Exception:
        return False


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--site", "--sites", nargs="+", help="Site module name(s)")
    g.add_argument("--all", action="store_true", help="Every site module (minus EXCLUDED_SITE_MODULES)")
    g.add_argument("--rerun-failed", metavar="JSON", help="Re-test sites that weren't clean in a previous report")
    p.add_argument("--keyword", default="latina", help="Search query (default: latina)")
    p.add_argument("--workers", type=int, default=4, help="Sites tested in parallel (default 4)")
    p.add_argument("--timeout", type=int, default=45, help="Per-step timeout inside the harness (s)")
    p.add_argument("--site-timeout", type=int, default=300, help="Hard limit per site (s)")
    p.add_argument("--media-timeout", type=float, default=15.0, help="Timeout for stream/image fetches (s)")
    p.add_argument("--samples", type=int, default=3, help="Thumbnails probed per listing (default 3)")
    p.add_argument("--flaresolverr", default=DEFAULT_FS_URL, help=f"FlareSolverr/solverr v1 URL (default {DEFAULT_FS_URL})")
    p.add_argument("--out", default=str(ROOT / "results"), help="Output directory")
    return p.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    if args.all:
        sites = list_site_modules()
    elif args.rerun_failed:
        prev = json.loads(Path(args.rerun_failed).read_text(encoding="utf-8"))
        sites = [r["site"] for r in prev["sites"] if r["verdict"] not in CLEAN]
    else:
        sites = args.site

    fs_ok = probe_fs(args.flaresolverr)
    env = dict(os.environ, FLARESOLVERR_URL=args.flaresolverr, FS_HOST=args.flaresolverr,
               FLARESOLVERR_AVAILABLE="1" if fs_ok else "0", PYTHONIOENCODING="utf-8",
               SMOKE_DEEP_PLAY="1")
    started = datetime.now()
    print(f"Search/playback/thumbnail audit: {len(sites)} sites, keyword '{args.keyword}', {args.workers} workers")
    print(f"FlareSolverr {args.flaresolverr}: {'available' if fs_ok else 'NOT available (CF sites will skip)'}\n")

    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(audit_site, s, args, env): s for s in sites}
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                rec = fut.result()
            except Exception as exc:
                rec = {"site": futures[fut], "steps": {}, "harness_error": f"{type(exc).__name__}: {exc}",
                       "list_play": {"result": "SKIP", "message": ""}, "search_play": {"result": "SKIP", "message": ""},
                       "list_images": {"result": "N/A"}, "search_images": {"result": "N/A"}, "elapsed": 0}
                rec["verdict"], rec["reasons"] = verdict_for(rec)
            records.append(rec)
            print(fmt_line(i, len(sites), rec), flush=True)
            if rec["verdict"] not in CLEAN:
                for reason in rec["reasons"][:3]:
                    print(f"        - {reason[:200]}")

    meta = {"started": started.strftime("%Y-%m-%d %H:%M:%S"), "keyword": args.keyword,
            "flaresolverr": args.flaresolverr, "fs_available": fs_ok,
            "duration_s": round((datetime.now() - started).total_seconds())}
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = started.strftime("%Y%m%d_%H%M%S")
    jpath = out_dir / f"search_playback_audit_{stamp}.json"
    mpath = out_dir / f"search_playback_audit_{stamp}.md"
    records.sort(key=lambda r: r["site"])
    jpath.write_text(json.dumps({"meta": meta, "sites": records}, indent=2), encoding="utf-8")
    mpath.write_text(render_markdown(records, meta), encoding="utf-8")
    shutil.copyfile(jpath, out_dir / "search_playback_audit_latest.json")
    shutil.copyfile(mpath, out_dir / "search_playback_audit_latest.md")

    bad = [r for r in records if r["verdict"] not in CLEAN]
    print(f"\n{len(records) - len(bad)}/{len(records)} sites clean. Report: {mpath}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
