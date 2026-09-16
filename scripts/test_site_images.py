#!/usr/bin/env python3
"""
Test image/thumbnail loading across Cumination sites.
Diagnoses:
- Direct loading failures (HTTP 403/401 hotlink protection)
- Missing Referer header requirements (|Referer=<site_url>)
- Fallback-only thumbnails (where scraper failed to extract real thumbs)
- Broken URLs (404, malformed, relative, data URIs, template placeholders)
- Cloudflare blocked image CDNs

Usage:
  python scripts/test_site_images.py --site redtube eporner spankbang
  python scripts/test_site_images.py --tier 1
  python scripts/test_site_images.py --all --limit 20
  python scripts/test_site_images.py --all --resume
  python scripts/test_site_images.py --flaresolverr http://192.168.50.114:8191/v1
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.error
from urllib.parse import parse_qs, unquote, urlparse, urljoin
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_FS_URL = (
    os.environ.get("FLARESOLVERR_URL")
    or os.environ.get("FS_HOST")
    or "http://192.168.50.114:8191/v1"
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

FALLBACK_ICON_NAMES = {
    "icon.png",
    "cuminationicon",
    "fanart.jpg",
    "defaultvideo.png",
    "cum-next.png",
    "cum-prev.png",
    "cum-search.png",
    "cum-cat.png",
}


@dataclass
class ImageProbeResult:
    original_url: str
    cleaned_url: str
    status: str  # PASS, NEEDS_REFERER, HTTP_ERROR, MALFORMED, DATA_URI, FALLBACK_ONLY, NON_IMAGE, TEMPLATE_PLACEHOLDER
    http_code: int = 0
    content_type: str = ""
    content_length: int = 0
    error_message: str = ""
    recommendation: str = ""


@dataclass
class SiteImageReport:
    site: str
    title: str
    base_url: str
    listing_status: str
    total_videos: int = 0
    total_images: int = 0
    overall_status: str = "UNKNOWN"  # PASS, NEEDS_REFERER, FALLBACK_ONLY, BROKEN_IMAGES, NO_IMAGES, TEMPLATE_PLACEHOLDER, LISTING_FAILED
    probes: list[ImageProbeResult] = field(default_factory=list)
    recommendation: str = ""
    error_message: str = ""


def is_fallback_icon(url: str, site_image: str = "") -> bool:
    if not url:
        return True
    clean = url.split("|")[0].strip()
    clean_lower = clean.lower()

    if "plugin.video.cumination" in clean_lower or "resources\\images" in clean_lower or "resources/images" in clean_lower:
        return True
    if clean_lower.startswith("special://"):
        return True

    path = urlparse(clean_lower).path
    filename = Path(path or clean_lower).name
    if filename in FALLBACK_ICON_NAMES:
        return True
    if site_image and clean_lower == site_image.split("|")[0].strip().lower():
        return True
    return False


def _probe_url_with_curl(test_url: str, headers: dict, timeout: float = 15.0):
    """Fallback probe using curl (matching Kodi's libcurl networking stack)."""
    try:
        cmd = ["curl.exe", "-s", "-I", "--max-time", str(int(timeout)), test_url]
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if res.stdout:
            lines = res.stdout.splitlines()
            code = 0
            ct = ""
            cl = 0
            for line in lines:
                if line.startswith("HTTP/"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        code = int(parts[1])
                elif line.lower().startswith("content-type:"):
                    ct = line.split(":", 1)[1].strip().lower()
                elif line.lower().startswith("content-length:"):
                    try:
                        cl = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
            if code > 0:
                return code, ct, cl
    except Exception:
        pass
    return None


def _parse_pipe_headers(raw_url: str) -> tuple[str, dict[str, str]]:
    pipe_headers: dict[str, str] = {}
    test_url = raw_url
    if "|" in raw_url:
        parts = raw_url.split("|", 1)
        test_url = parts[0].strip()
        qs = parse_qs(parts[1], keep_blank_values=True)
        for k, vals in qs.items():
            if vals:
                pipe_headers[k] = unquote(vals[0])
    return test_url, pipe_headers


def probe_image(
    raw_url: str,
    site_url: str = "",
    site_image: str = "",
    timeout: float = 15.0,
) -> ImageProbeResult:
    """Probe an image URL to determine if it loads correctly in Kodi."""
    if not raw_url:
        return ImageProbeResult(
            original_url=raw_url,
            cleaned_url="",
            status="NO_URL",
            error_message="Image URL is empty",
            recommendation="Fix scraper to extract valid thumbnail URL",
        )

    clean_url, pipe_headers = _parse_pipe_headers(raw_url)
    test_url = clean_url

    if is_fallback_icon(test_url, site_image):
        return ImageProbeResult(
            original_url=raw_url,
            cleaned_url=test_url,
            status="FALLBACK_ONLY",
            error_message="Image points to addon/site fallback logo",
            recommendation="Scraper is using addon/site fallback icon; fix video thumbnail extraction",
        )

    if test_url.startswith("data:"):
        return ImageProbeResult(
            original_url=raw_url,
            cleaned_url=test_url[:40] + "...",
            status="DATA_URI",
            error_message="Image is a data: URI, not a network URL",
            recommendation="Extract data-src or real image URL instead of placeholder data URI",
        )

    for placeholder in ("THUMBNUM", "{width}", "{height}"):
        if placeholder in test_url:
            return ImageProbeResult(
                original_url=raw_url,
                cleaned_url=test_url,
                status="TEMPLATE_PLACEHOLDER",
                error_message=f"Image URL contains template placeholder: {placeholder}",
                recommendation="Replace template placeholder (e.g. replace THUMBNUM with 1 or 16) in site scraper",
            )

    parsed = urlparse(test_url)
    if not parsed.scheme or not parsed.netloc:
        if test_url.startswith("//"):
            fixed = "https:" + test_url
            return ImageProbeResult(
                original_url=raw_url,
                cleaned_url=fixed,
                status="MALFORMED",
                error_message="Protocol-relative URL missing scheme (//...)",
                recommendation="Use 'https:' + url or urllib_parse.urljoin(site.url, url)",
            )
        elif test_url.startswith("/"):
            fixed = urljoin(site_url, test_url)
            return ImageProbeResult(
                original_url=raw_url,
                cleaned_url=fixed,
                status="MALFORMED",
                error_message="Relative path missing domain",
                recommendation="Use urllib_parse.urljoin(site.url, url)",
            )
        return ImageProbeResult(
            original_url=raw_url,
            cleaned_url=test_url,
            status="MALFORMED",
            error_message=f"Missing scheme or domain: {test_url}",
            recommendation="Fix URL formatting in scraper",
        )

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    headers.update(pipe_headers)

    req = urllib.request.Request(test_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.status
            ct = resp.headers.get("Content-Type", "").lower()
            cl = int(resp.headers.get("Content-Length", "0") or "0")
            if "image/" in ct or "octet-stream" in ct or not ct:
                return ImageProbeResult(
                    original_url=raw_url,
                    cleaned_url=test_url,
                    status="PASS",
                    http_code=code,
                    content_type=ct,
                    content_length=cl,
                )
            else:
                return ImageProbeResult(
                    original_url=raw_url,
                    cleaned_url=test_url,
                    status="NON_IMAGE",
                    http_code=code,
                    content_type=ct,
                    error_message=f"Received non-image Content-Type: {ct}",
                    recommendation="Verify scraper is targeting image link, not landing page",
                )
    except urllib.error.HTTPError as exc:
        direct_code = exc.code
        # Try curl fallback (handles HTTP/2 and TLS variations supported by Kodi)
        curl_res = _probe_url_with_curl(test_url, headers, timeout=min(timeout, 15.0))
        if curl_res and curl_res[0] == 200:
            c_code, c_ct, c_cl = curl_res
            if "image/" in c_ct or "octet-stream" in c_ct or not c_ct:
                return ImageProbeResult(
                    original_url=raw_url,
                    cleaned_url=test_url,
                    status="PASS",
                    http_code=c_code,
                    content_type=c_ct,
                    content_length=c_cl,
                )

        if direct_code in (401, 403) and "Referer" not in headers and site_url:
            retry_headers = dict(headers)
            retry_headers["Referer"] = site_url
            retry_req = urllib.request.Request(test_url, headers=retry_headers)
            try:
                with urllib.request.urlopen(retry_req, timeout=timeout) as retry_resp:
                    r_code = retry_resp.status
                    r_ct = retry_resp.headers.get("Content-Type", "").lower()
                    r_cl = int(retry_resp.headers.get("Content-Length", "0") or "0")
                    if "image/" in r_ct or "octet-stream" in r_ct or not r_ct:
                        return ImageProbeResult(
                            original_url=raw_url,
                            cleaned_url=test_url,
                            status="NEEDS_REFERER",
                            http_code=direct_code,
                            content_type=r_ct,
                            content_length=r_cl,
                            error_message=f"Direct request returned HTTP {direct_code}, but succeeded with Referer",
                            recommendation=f"Append '|Referer={site_url}' to thumbnail URL in site module",
                        )
            except Exception:
                # Try curl with Referer
                c_retry = _probe_url_with_curl(test_url, retry_headers, timeout=min(timeout, 15.0))
                if c_retry and c_retry[0] == 200:
                    _, r_ct, r_cl = c_retry
                    if "image/" in r_ct or "octet-stream" in r_ct or not r_ct:
                        return ImageProbeResult(
                            original_url=raw_url,
                            cleaned_url=test_url,
                            status="NEEDS_REFERER",
                            http_code=direct_code,
                            content_type=r_ct,
                            content_length=r_cl,
                            error_message=f"Direct request returned HTTP {direct_code}, but succeeded with Referer",
                            recommendation=f"Append '|Referer={site_url}' to thumbnail URL in site module",
                        )

        return ImageProbeResult(
            original_url=raw_url,
            cleaned_url=test_url,
            status=f"HTTP_{direct_code}",
            http_code=direct_code,
            error_message=f"HTTP {direct_code} error requesting image",
            recommendation=f"Image host returned {direct_code}; inspect site/CDN anti-hotlinking rules",
        )
    except Exception as exc:
        # Check if curl can handle the connection (e.g. SSL renegotiation)
        curl_res = _probe_url_with_curl(test_url, headers, timeout=min(timeout, 15.0))
        if curl_res and curl_res[0] == 200:
            c_code, c_ct, c_cl = curl_res
            if "image/" in c_ct or "octet-stream" in c_ct or not c_ct:
                return ImageProbeResult(
                    original_url=raw_url,
                    cleaned_url=test_url,
                    status="PASS",
                    http_code=c_code,
                    content_type=c_ct,
                    content_length=c_cl,
                )

        return ImageProbeResult(
            original_url=raw_url,
            cleaned_url=test_url,
            status="NETWORK_ERROR",
            error_message=f"{type(exc).__name__}: {exc}",
            recommendation="Network or DNS error contacting image server",
        )


probe_single_image = probe_image


def evaluate_site(
    site_name: str,
    fs_url: str = DEFAULT_FS_URL,
    samples_per_site: int = 5,
    timeout: float = 30.0,
) -> SiteImageReport:
    """Run live_smoke_test child for a site, extract listing items, and probe thumbnails."""
    env = os.environ.copy()
    if fs_url:
        env["FLARESOLVERR_URL"] = fs_url
        env["FS_HOST"] = fs_url
        env["FS_ENABLE"] = "true"

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "live_smoke_test.py"),
        "--run-site",
        site_name,
        "--steps",
        "main,list",
        "--force-steps",
        "--timeout",
        str(int(timeout)),
    ]

    proc_timeout = int(max(timeout * 3, 90))
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=proc_timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return SiteImageReport(
            site=site_name,
            title=site_name,
            base_url="",
            listing_status="TIMEOUT",
            overall_status="LISTING_FAILED",
            error_message=f"Site listing timed out after {proc_timeout}s",
        )
    except Exception as e:
        return SiteImageReport(
            site=site_name,
            title=site_name,
            base_url="",
            listing_status="ERROR",
            overall_status="LISTING_FAILED",
            error_message=str(e),
        )

    raw_out = proc.stdout.strip()
    if not raw_out:
        err_msg = proc.stderr.strip() or "No output from child process"
        return SiteImageReport(
            site=site_name,
            title=site_name,
            base_url="",
            listing_status="FAILED",
            overall_status="LISTING_FAILED",
            error_message=err_msg[:200],
        )

    try:
        data = json.loads(raw_out)
    except json.JSONDecodeError:
        brace_idx = raw_out.find("{")
        if brace_idx >= 0:
            try:
                data = json.loads(raw_out[brace_idx:])
            except Exception:
                return SiteImageReport(
                    site=site_name,
                    title=site_name,
                    base_url="",
                    listing_status="FAILED",
                    overall_status="LISTING_FAILED",
                    error_message=f"Failed to parse runner output: {raw_out[:200]}",
                )
        else:
            return SiteImageReport(
                site=site_name,
                title=site_name,
                base_url="",
                listing_status="FAILED",
                overall_status="LISTING_FAILED",
                error_message=raw_out[:200],
            )

    title = data.get("title", site_name)
    base_url = data.get("base_url", "")
    steps = data.get("steps", {})
    list_step = steps.get("list") or steps.get("main") or {}
    listing_status = list_step.get("status", "FAIL")

    samples = data.get("listing_samples", [])
    video_samples = [s for s in samples if s.get("item_type") == "video"]
    if not video_samples:
        # Check for album/gallery/cam sites where content items are dirs
        video_samples = [
            s for s in samples
            if not s.get("name", "").startswith("Next Page")
            and "cum-next" not in s.get("icon", "")
            and "cum-search" not in s.get("icon", "")
            and "cum-cat" not in s.get("icon", "")
            and not any(s.get("mode", "").endswith(f".{m}") for m in ("Main", "Search", "Categories", "Cat", "Tags", "Toplist", "clean_database"))
            and not any(nav in s.get("name", "").lower() for nav in ("search", "categories", "next page", "tag", "refresh"))
            and (s.get("icon", "").startswith("http") or s.get("icon", "").startswith("//"))
        ]

    total_videos = len(video_samples)
    if total_videos == 0:
        msg = list_step.get("message", "No video items found")
        return SiteImageReport(
            site=site_name,
            title=title,
            base_url=base_url,
            listing_status=listing_status,
            total_videos=0,
            total_images=0,
            overall_status="LISTING_FAILED" if listing_status != "PASS" else "NO_VIDEOS",
            error_message=msg,
        )

    probe_items = video_samples[:samples_per_site] if samples_per_site > 0 else video_samples
    probes: list[ImageProbeResult] = []
    site_image = getattr(data, "image", "")

    for item in probe_items:
        icon_url = item.get("icon", "")
        probe = probe_single_image(icon_url, base_url, site_image=site_image, timeout=timeout)
        probes.append(probe)

    pass_count = sum(1 for p in probes if p.status == "PASS")
    referer_count = sum(1 for p in probes if p.status == "NEEDS_REFERER")
    fallback_count = sum(1 for p in probes if p.status == "FALLBACK_ONLY")
    malformed_count = sum(1 for p in probes if p.status == "MALFORMED")
    template_count = sum(1 for p in probes if p.status == "TEMPLATE_PLACEHOLDER")
    http_error_count = sum(1 for p in probes if p.status.startswith("HTTP_"))
    no_url_count = sum(1 for p in probes if p.status == "NO_URL")

    if referer_count > 0 and (pass_count + referer_count == len(probes)):
        overall = "NEEDS_REFERER"
        rec = f"Append '|Referer={base_url}' to thumbnail URLs"
    elif template_count > 0:
        overall = "TEMPLATE_PLACEHOLDER"
        rec = "Scraper outputs unreplaced template placeholders (e.g. THUMBNUM)"
    elif fallback_count == len(probes):
        overall = "FALLBACK_ONLY"
        rec = "Scraper is using addon/site fallback icon; fix video thumbnail extraction"
    elif pass_count == len(probes):
        overall = "PASS"
        rec = "Images load correctly"
    elif malformed_count > 0:
        overall = "MALFORMED_URL"
        rec = "Scraper produces relative or malformed URLs; resolve with urllib_parse.urljoin"
    elif http_error_count > 0:
        overall = "BROKEN_IMAGES"
        rec = f"Image URLs return HTTP errors ({', '.join(set(p.status for p in probes if p.status.startswith('HTTP_')))})"
    elif no_url_count == len(probes):
        overall = "NO_IMAGES"
        rec = "Scraper provides no thumbnail URLs"
    elif pass_count > 0:
        overall = "PARTIAL_PASS"
        rec = f"{pass_count}/{len(probes)} images loaded successfully"
    else:
        overall = "FAIL"
        rec = "Images failed to load"

    return SiteImageReport(
        site=site_name,
        title=title,
        base_url=base_url,
        listing_status=listing_status,
        total_videos=total_videos,
        total_images=sum(1 for s in video_samples if s.get("icon")),
        overall_status=overall,
        probes=probes,
        recommendation=rec,
    )


def print_site_report(report: SiteImageReport) -> None:
    status_icons = {
        "PASS": "[PASS]   ",
        "NEEDS_REFERER": "[REF!]  ",
        "FALLBACK_ONLY": "[FALLBK]",
        "TEMPLATE_PLACEHOLDER": "[TMPL!] ",
        "MALFORMED_URL": "[MALF!] ",
        "BROKEN_IMAGES": "[BROKEN]",
        "NO_IMAGES": "[NOIMG] ",
        "PARTIAL_PASS": "[PARTIAL]",
        "LISTING_FAILED": "[NO_LST]",
        "NO_VIDEOS": "[NO_VID]",
    }
    tag = status_icons.get(report.overall_status, f"[{report.overall_status[:6]}]")
    print(f"{tag} {report.site:<20} videos={report.total_videos:<3} status={report.overall_status}")
    if report.recommendation and report.overall_status != "PASS":
        print(f"         Recommendation: {report.recommendation}")
    if report.error_message:
        print(f"         Error: {report.error_message}")
    for p in report.probes:
        if p.status != "PASS":
            print(f"           - {p.status}: {p.cleaned_url[:70]} ({p.error_message})")


def render_markdown_report(reports: list[SiteImageReport], start_time: str, fs_url: str) -> str:
    lines = [
        "# Site Image Loading Audit Report",
        "",
        f"- **Date:** {start_time}",
        f"- **FlareSolverr URL:** `{fs_url}`",
        f"- **Total Sites Tested:** {len(reports)}",
        "",
        "## Summary",
        "",
    ]

    status_counts: dict[str, int] = {}
    for r in reports:
        status_counts[r.overall_status] = status_counts.get(r.overall_status, 0) + 1

    lines.append("| Status | Count | Description |")
    lines.append("|---|---|---|")
    lines.append(f"| `PASS` | {status_counts.get('PASS', 0)} | Images load directly with 200 OK |")
    lines.append(f"| `NEEDS_REFERER` | {status_counts.get('NEEDS_REFERER', 0)} | 403 unless Referer header is appended |")
    lines.append(f"| `FALLBACK_ONLY` | {status_counts.get('FALLBACK_ONLY', 0)} | Scraper outputs site logo instead of video thumb |")
    lines.append(f"| `TEMPLATE_PLACEHOLDER` | {status_counts.get('TEMPLATE_PLACEHOLDER', 0)} | Unreplaced template placeholders like THUMBNUM |")
    lines.append(f"| `MALFORMED_URL` | {status_counts.get('MALFORMED_URL', 0)} | Protocol-relative or relative path missing domain |")
    lines.append(f"| `BROKEN_IMAGES` | {status_counts.get('BROKEN_IMAGES', 0)} | Image CDN returned 404, 500, etc. |")
    lines.append(f"| `NO_IMAGES` | {status_counts.get('NO_IMAGES', 0)} | Empty image attribute emitted |")
    lines.append(f"| `LISTING_FAILED` | {status_counts.get('LISTING_FAILED', 0)} | Site listing failed or timed out |")
    lines.append("")

    issues = [r for r in reports if r.overall_status not in ("PASS", "LISTING_FAILED", "NO_VIDEOS")]
    if issues:
        lines.append("## Sites Requiring Image Fixes")
        lines.append("")
        lines.append("| Site | Overall | Sample Image URL | Diagnosis / Fix |")
        lines.append("|---|---|---|---|")
        for r in issues:
            sample_probe = r.probes[0] if r.probes else None
            sample_url = sample_probe.cleaned_url if sample_probe else "N/A"
            if len(sample_url) > 60:
                sample_url = sample_url[:57] + "..."
            lines.append(f"| `{r.site}` | `{r.overall_status}` | `{sample_url}` | {r.recommendation} |")
        lines.append("")

    lines.append("## All Tested Sites")
    lines.append("")
    lines.append("| Site | Title | Videos | Status | Recommendation |")
    lines.append("|---|---|---|---|---|")
    for r in reports:
        lines.append(f"| `{r.site}` | {r.title} | {r.total_videos} | `{r.overall_status}` | {r.recommendation or 'OK'} |")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit and test video image loading for Cumination sites")
    parser.add_argument("--site", "--sites", nargs="+", help="Specific site module name(s) to test")
    parser.add_argument("--all", action="store_true", help="Test all available site modules")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3], help="Test sites in a specific tier")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of sites to test")
    parser.add_argument("--resume", action="store_true", help="Skip sites already present in latest results")
    parser.add_argument("--samples", type=int, default=3, help="Number of image samples to probe per site (default 3)")
    parser.add_argument("--flaresolverr", default=DEFAULT_FS_URL, help=f"FlareSolverr API URL (default {DEFAULT_FS_URL})")
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout in seconds per site listing (default 30)")
    parser.add_argument("--out", default=str(ROOT / "results"), help="Directory for JSON/MD output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    from scripts.live_smoke_test import discover_site_names, load_site_profiles

    all_sites = discover_site_names()
    profiles = load_site_profiles()

    selected_sites = []
    if args.site:
        selected_sites = args.site
    elif args.tier:
        for s in all_sites:
            site_prof = profiles.get("sites", {}).get(s, {})
            if site_prof.get("tier") == args.tier:
                selected_sites.append(s)
    elif args.all:
        selected_sites = all_sites
    else:
        tier1 = [s for s in all_sites if profiles.get("sites", {}).get(s, {}).get("tier") == 1]
        selected_sites = tier1 if tier1 else all_sites[:15]

    if args.limit > 0:
        selected_sites = selected_sites[:args.limit]

    # Resume support: load existing results if requested
    existing_reports: dict[str, SiteImageReport] = {}
    latest_json = out_dir / "image_audit_latest.json"
    if args.resume and latest_json.exists():
        try:
            prev_data = json.loads(latest_json.read_text(encoding="utf-8"))
            for r in prev_data.get("results", []):
                probes = [ImageProbeResult(**p) for p in r.get("probes", [])]
                rep = SiteImageReport(
                    site=r["site"],
                    title=r.get("title", r["site"]),
                    base_url=r.get("base_url", ""),
                    listing_status=r.get("listing_status", "PASS"),
                    total_videos=r.get("total_videos", 0),
                    total_images=r.get("total_images", 0),
                    overall_status=r.get("overall_status", "UNKNOWN"),
                    probes=probes,
                    recommendation=r.get("recommendation", ""),
                    error_message=r.get("error_message", ""),
                )
                existing_reports[r["site"]] = rep
            print(f"[Resume] Loaded {len(existing_reports)} existing site results.")
        except Exception as e:
            print(f"[Resume] Warning: failed to load existing results: {e}")

    start_iso = datetime.datetime.now().isoformat()
    print("=" * 70)
    print("Cumination Site Image Loading Audit")
    print(f"Sites to test: {len(selected_sites)}")
    print(f"FlareSolverr:  {args.flaresolverr}")
    print(f"Samples/site:  {args.samples}")
    print("=" * 70)

    reports: list[SiteImageReport] = []
    for idx, site_name in enumerate(selected_sites, 1):
        if args.resume and site_name in existing_reports and existing_reports[site_name].overall_status != "LISTING_FAILED":
            rep = existing_reports[site_name]
            reports.append(rep)
            print(f"[{idx}/{len(selected_sites)}] [CACHED] {site_name:<20} status={rep.overall_status}")
            continue

        print(f"[{idx}/{len(selected_sites)}] Testing site: {site_name}...")
        rep = evaluate_site(
            site_name=site_name,
            fs_url=args.flaresolverr,
            samples_per_site=args.samples,
            timeout=args.timeout,
        )
        reports.append(rep)
        print_site_report(rep)
        print()

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"image_audit_{ts}.json"
    md_path = out_dir / f"image_audit_{ts}.md"
    latest_json = out_dir / "image_audit_latest.json"
    latest_md = out_dir / "image_audit_latest.md"

    json_data = {
        "timestamp": start_iso,
        "flaresolverr": args.flaresolverr,
        "total_sites": len(reports),
        "results": [
            {
                "site": r.site,
                "title": r.title,
                "base_url": r.base_url,
                "overall_status": r.overall_status,
                "total_videos": r.total_videos,
                "recommendation": r.recommendation,
                "error_message": r.error_message,
                "probes": [asdict(p) for p in r.probes],
            }
            for r in reports
        ],
    }

    serialized_json = json.dumps(json_data, indent=2)
    json_path.write_text(serialized_json, encoding="utf-8")
    latest_json.write_text(serialized_json, encoding="utf-8")

    md_content = render_markdown_report(reports, start_iso, args.flaresolverr)
    md_path.write_text(md_content, encoding="utf-8")
    latest_md.write_text(md_content, encoding="utf-8")

    print("=" * 70)
    print("Audit Complete. Results saved:")
    print(f"  JSON:   {json_path}")
    print(f"  MD:     {md_path}")
    print(f"  Latest: {latest_json} & {latest_md}")
    print("=" * 70)

    issues_found = any(r.overall_status in ("NEEDS_REFERER", "FALLBACK_ONLY", "MALFORMED_URL", "BROKEN_IMAGES", "TEMPLATE_PLACEHOLDER") for r in reports)
    return 1 if issues_found else 0


if __name__ == "__main__":
    sys.exit(main())
