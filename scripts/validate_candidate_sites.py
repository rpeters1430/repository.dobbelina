#!/usr/bin/env python3
"""Validate ranked site candidates before implementing new site modules."""

from __future__ import annotations

import argparse
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RANK_REPORT = REPO_ROOT / "docs" / "research" / "FLUFFLE_RANK_REPORT.md"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "research" / "SITE_VALIDATION_REPORT.md"

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
    difficulty: str
    source_section: str


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


def parse_candidates(path: Path, sections: set[str]) -> list[Candidate]:
    candidates: list[Candidate] = []
    current_section = ""

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip()
            continue
        if current_section not in sections:
            continue
        if not line.startswith("| **"):
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        name = re.sub(r"^\*\*|\*\*$", "", cells[0]).strip()
        candidates.append(
            Candidate(
                name=name,
                url=cells[1],
                category=cells[2],
                difficulty=cells[3],
                source_section=current_section,
            )
        )

    return candidates


def text_has_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in patterns)


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


def likely_video_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    scored_links: list[tuple[int, str]] = []

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


def fetch(session: requests.Session, url: str, timeout: int) -> requests.Response:
    return session.get(url, timeout=timeout, allow_redirects=True)


def validate_candidate(session: requests.Session, candidate: Candidate, timeout: int) -> Validation:
    reasons: list[str] = []
    final_url = candidate.url
    http_status: int | None = None
    html = ""

    try:
        response = fetch(session, candidate.url, timeout)
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
    sampled_video_status: int | None = None
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
            video_response = fetch(session, sampled_video_url, timeout)
            sampled_video_url = video_response.url
            sampled_video_status = video_response.status_code
            sampled_playback_signals = count_playback_signals(video_response.text or "")
            if sampled_video_status >= 400:
                reasons.append(f"sample video HTTP {sampled_video_status}")
        except requests.RequestException as exc:
            reasons.append(f"sample video request error: {exc.__class__.__name__}")
    else:
        reasons.append("no likely same-site video links found")

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


def render_report(validations: list[Validation]) -> str:
    lines = [
        "# Site Candidate Validation Report",
        "",
        "Validated by fetching each candidate homepage and, when possible, one likely same-site video page.",
        "",
    ]

    counts: dict[str, int] = {}
    for validation in validations:
        counts[validation.status] = counts.get(validation.status, 0) + 1
    lines.append(
        "Summary: "
        + ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
    )
    lines.append("")

    lines += [
        "| Status | Site | Difficulty | HTTP | Links | Playback | Sample Playback | Notes |",
        "| :--- | :--- | :--- | :--- | ---: | ---: | ---: | :--- |",
    ]
    for item in validations:
        notes = "; ".join(item.reasons[:3]) or item.title or item.final_url
        sample_playback = item.sampled_playback_signals
        lines.append(
            "| {status} | **{name}**<br>{url} | {difficulty} | {http} | {links} | {playback} | {sample} | {notes} |".format(
                status=item.status,
                name=item.candidate.name,
                url=item.final_url,
                difficulty=item.candidate.difficulty,
                http=item.http_status or "",
                links=item.video_links,
                playback=item.playback_signals,
                sample=sample_playback,
                notes=notes.replace("|", "\\|"),
            )
        )
    lines.append("")

    promising = [item for item in validations if item.status == "PROMISING"]
    if promising:
        lines += ["## Recommended Next Checks", ""]
        for item in promising[:10]:
            sample = f" Sample: {item.sampled_video_url}" if item.sampled_video_url else ""
            lines.append(
                f"- **{item.candidate.name}** ({item.candidate.difficulty}) - "
                f"{item.video_links} candidate video links, "
                f"{item.sampled_playback_signals} playback signals on sample.{sample}"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rank-report", type=Path, default=DEFAULT_RANK_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--section",
        action="append",
        default=["In Roadmap/Tracker but Not Yet Implemented"],
        help="Report section to validate. Can be provided multiple times.",
    )
    args = parser.parse_args()

    candidates = parse_candidates(args.rank_report, set(args.section))
    if args.limit:
        candidates = candidates[: args.limit]

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    validations: list[Validation] = []
    for index, candidate in enumerate(candidates, 1):
        print(f"[{index}/{len(candidates)}] {candidate.name} {candidate.url}", file=sys.stderr)
        validations.append(validate_candidate(session, candidate, args.timeout))

    report = render_report(validations)
    args.output.write_text(report, encoding="utf-8")
    print(f"Report written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
