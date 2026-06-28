#!/usr/bin/env python3
"""
track_and_test_new_sites.py

Fetches the latest site list from https://fluffle.cc/fmfy (Fluffle).
Cross-references against:
  - Existing site modules in plugin.video.cumination
  - Local tracking markdown files (NEW_SITES.md, NEW_SITES_ROADMAP.md, FLUFFLE_FMFY_TRACKER.md)
Identifies brand new sites not yet implemented or tracked.
Runs test requests (similar to validate_candidate_sites.py) on these new sites to find ones we could add.
Outputs a report highlighting promising candidates.
"""

import argparse
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"

# Import rank_new_sites from scripts to reuse parsing logic
sys.path.insert(0, str(REPO_ROOT))
from scripts import rank_new_sites  # noqa: E402

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

PARKING_PATTERNS = [
    "domain is for sale",
    "buy this domain",
    "parked",
    "parkingcrew",
    "sedo",
    "bodis",
    "hugedomains",
    "namecheap parking",
    "this domain may be for sale",
    "website is for sale",
]

BLOCK_PATTERNS = [
    "attention required",
    "checking your browser",
    "cloudflare",
    "cf-chl",
    "captcha",
    "access denied",
    "just a moment",
    "verify you are human",
]

VIDEO_LINK_PATTERNS = [
    "/video/",
    "/videos/",
    "/watch/",
    "/embed/",
    "/movie/",
    "/movies/",
    ".html",
]

VIDEO_INDEX_SEGMENTS = {
    "categories",
    "category",
    "genres",
    "genre",
    "latest",
    "main",
    "movies",
    "new",
    "popular",
    "tags",
    "tag",
    "videos",
}

PLAYBACK_PATTERNS = [
    ".m3u8",
    ".mp4",
    "jwplayer",
    "videojs",
    "video-js",
    "<video",
    "player",
    "embed",
    "iframe",
]


@dataclass
class Candidate:
    name: str
    url: str
    category: str
    difficulty: str = "unknown"
    source_section: str = "Fluffle"


@dataclass
class Validation:
    candidate: Candidate
    status: str
    final_url: str
    http_status: int | None
    bytes_read: int
    title: str
    video_links: int
    playback_signals: int
    sampled_video_url: str
    sampled_video_status: int | None
    sampled_playback_signals: int
    reasons: list[str]


def normalize(name: str) -> str:
    """Lowercase and strip punctuation/spaces for fuzzy matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def same_site(base_url: str, candidate_url: str) -> bool:
    base_host = urlparse(base_url).netloc.lower().removeprefix("www.")
    candidate_host = urlparse(candidate_url).netloc.lower().removeprefix("www.")
    return bool(candidate_host) and (
        candidate_host == base_host or candidate_host.endswith("." + base_host)
    )


def host_changed(original_url: str, final_url: str) -> bool:
    original = urlparse(original_url).netloc.lower().removeprefix("www.")
    final = urlparse(final_url).netloc.lower().removeprefix("www.")
    return bool(original and final and original != final)


def page_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return " ".join(soup.title.string.split())
    heading = soup.find(["h1", "h2"])
    return " ".join(heading.get_text(" ", strip=True).split()) if heading else ""


def count_playback_signals(html: str) -> int:
    lower = html.lower()
    return sum(1 for pattern in PLAYBACK_PATTERNS if pattern in lower)


def text_has_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in patterns)


def likely_video_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    scored_links = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if href.startswith(("javascript:", "mailto:", "#")):
            continue
        absolute = urljoin(base_url, href)
        if not same_site(base_url, absolute):
            continue
        parsed = urlparse(absolute)
        path = parsed.path.lower()
        segments = [segment for segment in path.strip("/").split("/") if segment]
        last_segment = segments[-1] if segments else ""
        text = anchor.get_text(" ", strip=True).lower()
        score = 0

        if ".html" in path:
            score += 4
        if any(pattern in path for pattern in ("/video/", "/watch/", "/embed/")):
            score += 4
        if any(pattern in path for pattern in ("/movie/", "/movies/")):
            score += 2
        if re.search(r"/\d{3,}(?:[-_/]|$)", path) or re.search(r"-\d{3,}(?:\.html|/|$)", path):
            score += 2
        if any(word in text for word in ("watch", "video", "movie", "scene")):
            score += 1
        if last_segment in VIDEO_INDEX_SEGMENTS:
            score -= 4
        if len(segments) <= 1 and ".html" not in path:
            score -= 2
        if not any(pattern in path for pattern in VIDEO_LINK_PATTERNS) and score < 3:
            continue
        if score < 2:
            continue
        if absolute not in seen:
            seen.add(absolute)
            scored_links.append((score, absolute))

    scored_links.sort(key=lambda item: (-item[0], item[1]))
    return [url for _, url in scored_links]


def validate_candidate(session: requests.Session, candidate: Candidate, timeout: int) -> Validation:
    reasons = []
    final_url = candidate.url
    http_status = None
    html = ""

    try:
        response = session.get(candidate.url, timeout=timeout, allow_redirects=True)
        final_url = response.url
        http_status = response.status_code
        html = response.text or ""
    except requests.RequestException as exc:
        return Validation(
            candidate=candidate,
            status="FAIL",
            final_url=final_url,
            http_status=http_status,
            bytes_read=0,
            title="",
            video_links=0,
            playback_signals=0,
            sampled_video_url="",
            sampled_video_status=None,
            sampled_playback_signals=0,
            reasons=[f"request error: {exc.__class__.__name__}: {exc}"],
        )

    title = page_title(html)
    links = likely_video_links(final_url, html)
    playback_signals = count_playback_signals(html)
    sampled_video_url = ""
    sampled_video_status = None
    sampled_playback_signals = 0

    if http_status and http_status >= 400:
        reasons.append(f"HTTP {http_status}")
    if host_changed(candidate.url, final_url):
        reasons.append(f"redirected to different host: {urlparse(final_url).netloc}")
    if text_has_any(html[:120000], PARKING_PATTERNS):
        reasons.append("parking/sale text detected")
    if text_has_any(html[:120000], BLOCK_PATTERNS):
        reasons.append("anti-bot or access challenge text detected")
    if len(html) < 2000:
        reasons.append("very small HTML response")

    if links:
        sampled_video_url = links[0]
        try:
            video_response = session.get(sampled_video_url, timeout=timeout, allow_redirects=True)
            sampled_video_url = video_response.url
            sampled_video_status = video_response.status_code
            video_html = video_response.text or ""
            sampled_playback_signals = count_playback_signals(video_html)
            if sampled_video_status >= 400:
                reasons.append(f"sample video HTTP {sampled_video_status}")
            if text_has_any(video_html[:120000], BLOCK_PATTERNS):
                reasons.append("sample video anti-bot text detected")
        except requests.RequestException as exc:
            reasons.append(f"sample video request error: {exc.__class__.__name__}")
    else:
        reasons.append("no likely same-site video links found")

    # Determine status
    if any(reason.startswith("HTTP 4") or reason.startswith("HTTP 5") for reason in reasons):
        status = "FAIL"
    elif any("parking" in reason or "different host" in reason for reason in reasons):
        status = "FAIL"
    elif any("anti-bot" in reason for reason in reasons):
        status = "BLOCKED"
    elif links and (sampled_playback_signals > 0 or playback_signals > 0):
        status = "PROMISING"
    elif links:
        status = "REVIEW"
    else:
        status = "LOW"

    return Validation(
        candidate=candidate,
        status=status,
        final_url=final_url,
        http_status=http_status,
        bytes_read=len(html.encode("utf-8", errors="ignore")),
        title=title,
        video_links=len(links),
        playback_signals=playback_signals,
        sampled_video_url=sampled_video_url,
        sampled_video_status=sampled_video_status,
        sampled_playback_signals=sampled_playback_signals,
        reasons=reasons,
    )


def generate_suggested_markdown(promising_validations: list[Validation]) -> str:
    """Generate Markdown snippet for easy copy-pasting to NEW_SITES.md."""
    if not promising_validations:
        return "No promising new sites found to suggest."

    lines = [
        "### Suggested Additions for docs/development/NEW_SITES.md",
        "Copy and paste the promising entries below into your tracking file.",
        "",
        "| Site | Category | Difficulty | Status | Notes |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for item in promising_validations:
        site_name = item.candidate.name
        cat = item.candidate.category
        diff = "Easy" if "tube" in cat.lower() else "Medium"
        notes = f"New Fluffle discovery. {item.video_links} video links. Sample playback signals: {item.sampled_playback_signals}."
        lines.append(f"| **{site_name}** | {cat} | {diff} | [ ] | {notes} |")
    
    return "\n".join(lines)


def render_report(validations: list[Validation], total_new: int, tested_count: int) -> str:
    lines = [
        "# New Fluffle Sites Discovery & Validation Report",
        "",
        f"**{total_new}** brand new sites found on Fluffle that are not currently implemented or tracked.",
        f"Tested **{tested_count}** of them.",
        "",
    ]

    counts = {}
    for validation in validations:
        counts[validation.status] = counts.get(validation.status, 0) + 1
    
    status_summary = ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
    lines.append(f"Validation Status Summary: {status_summary}")
    lines.append("")

    lines += [
        "## Tested Sites Table",
        "",
        "| Status | Site | Category | HTTP | Links | Playback | Sample Playback | Notes |",
        "| :--- | :--- | :--- | :--- | ---: | ---: | ---: | :--- |",
    ]
    for item in validations:
        notes = "; ".join(item.reasons[:3]) or item.title or item.final_url
        lines.append(
            "| {status} | **{name}**<br>{url} | {category} | {http} | {links} | {playback} | {sample} | {notes} |".format(
                status=item.status,
                name=item.candidate.name,
                url=item.final_url,
                category=item.candidate.category,
                http=item.http_status or "",
                links=item.video_links,
                playback=item.playback_signals,
                sample=item.sampled_playback_signals,
                notes=notes.replace("|", "\\|"),
            )
        )
    lines.append("")

    promising = [item for item in validations if item.status == "PROMISING"]
    if promising:
        lines += [
            "## Promising New Candidates",
            "These sites are highly recommended for implementation. They have same-site video links and direct playback signals (HTML5 video, players, iFrames, or stream formats).",
            "",
        ]
        for item in promising:
            sample_info = f" (Sample URL: {item.sampled_video_url})" if item.sampled_video_url else ""
            lines.append(
                f"- **{item.candidate.name}** ({item.candidate.category}) - "
                f"Links found: {item.video_links}, Playback signals: {item.sampled_playback_signals}{sample_info}"
            )
        lines.append("")
        lines.append(generate_suggested_markdown(promising))
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tracks new sites from Fluffle against local tracking files and tests them."
    )
    parser.add_argument(
        "--new-sites-md",
        type=Path,
        default=REPO_ROOT / "docs" / "development" / "NEW_SITES.md",
        help="Path to docs/development/NEW_SITES.md",
    )
    parser.add_argument(
        "--sites-md",
        type=Path,
        default=REPO_ROOT / "NEW_SITES_ROADMAP.md",
        help="Path to NEW_SITES_ROADMAP.md",
    )
    parser.add_argument(
        "--tracker-md",
        type=Path,
        default=REPO_ROOT / "docs" / "research" / "FLUFFLE_FMFY_TRACKER.md",
        help="Path to FLUFFLE_FMFY_TRACKER.md",
    )
    parser.add_argument(
        "--url",
        default="https://fluffle.cc/fmfy",
        help="Fluffle URL to scrape",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of brand-new sites to run HTTP verification tests on",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Network timeout in seconds",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "research" / "NEW_FLUFFLE_SITES_REPORT.md",
        help="File path to write validation report to",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include non-video categories (e.g. tools, index links) from Fluffle",
    )
    args = parser.parse_args()

    print(f"Loading existing implemented modules from {SITES_DIR}...")
    existing_modules = rank_new_sites.load_existing_modules()
    print(f"Found {len(existing_modules)} implemented site modules.")

    # Gather tracked site keys from local files
    tracked = set()
    if args.new_sites_md.exists():
        new_sites_dict = rank_new_sites.parse_new_sites(args.new_sites_md)
        tracked.update(new_sites_dict.keys())
        print(f"Loaded {len(new_sites_dict)} site entries from {args.new_sites_md.name}.")
    
    if args.sites_md.exists():
        roadmap_dict = rank_new_sites.parse_roadmap(args.sites_md)
        tracked.update(roadmap_dict.keys())
        print(f"Loaded {len(roadmap_dict)} site entries from {args.sites_md.name}.")

    if args.tracker_md.exists():
        tracker_dict = rank_new_sites.parse_tracker(args.tracker_md)
        tracked.update(tracker_dict.keys())
        tracker_implemented = rank_new_sites.parse_tracker_implemented(args.tracker_md)
        tracked.update(tracker_implemented)
        print(f"Loaded {len(tracker_dict) + len(tracker_implemented)} site entries from {args.tracker_md.name}.")

    print(f"Total distinct tracked/implemented names in markdown files: {len(tracked)}")

    print(f"Fetching Fluffle index from {args.url}...")
    fluffle_sites = rank_new_sites.fetch_fluffle(args.url)
    if not fluffle_sites:
        print("[ERROR] Failed to fetch or parse any sites from Fluffle. Exiting.")
        sys.exit(1)
    print(f"Scraped {len(fluffle_sites)} total entries from Fluffle.")

    # Identify brand new sites
    new_candidates = []
    seen = set()
    for site in fluffle_sites:
        key = site["name"]
        if not key or key in seen:
            continue
        seen.add(key)

        # Filter categories if requested
        if not rank_new_sites.is_supported_candidate(site, include_all=args.include_all):
            continue

        keys = rank_new_sites.site_keys(site)
        
        # Check if already implemented or tracked
        is_implemented = bool(keys & existing_modules)
        is_tracked = bool(keys & tracked)

        if not is_implemented and not is_tracked:
            new_candidates.append(site)

    print(f"Found {len(new_candidates)} brand new, untracked/unimplemented sites on Fluffle.")

    if not new_candidates:
        print("No new untracked sites discovered. Writing empty/status report.")
        report = render_report([], total_new=0, tested_count=0)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
        return

    # Sort candidates by category and name for consistent checking
    new_candidates.sort(key=lambda s: (s["category"], s["raw_name"].lower()))

    # Limit testing
    to_test = new_candidates
    if args.limit and len(new_candidates) > args.limit:
        print(f"Limiting HTTP testing to first {args.limit} new sites.")
        to_test = new_candidates[:args.limit]

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    validations = []
    print(f"Testing {len(to_test)} new sites...")
    for idx, site in enumerate(to_test, 1):
        candidate_obj = Candidate(
            name=site["raw_name"],
            url=site["url"],
            category=site["category"]
        )
        print(f"[{idx}/{len(to_test)}] Testing: {candidate_obj.name} ({candidate_obj.url})")
        val = validate_candidate(session, candidate_obj, args.timeout)
        print(f"   -> Result: {val.status} (Video links: {val.video_links}, Playback signals: {val.sampled_playback_signals})")
        validations.append(val)

    # Render and save report
    report = render_report(validations, total_new=len(new_candidates), tested_count=len(to_test))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Report successfully written to {args.output}")


if __name__ == "__main__":
    main()
