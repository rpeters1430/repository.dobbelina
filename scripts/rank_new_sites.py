#!/usr/bin/env python3
"""
rank_new_sites.py

Fetches https://fluffle.cc/fmfy, cross-references it against:
  - The existing site modules in the addon
  - A "new sites" roadmap markdown file (default: NEW_SITES_ROADMAP.md)
  - The Fluffle tracker (default: docs/research/FLUFFLE_FMFY_TRACKER.md)

Produces a ranked list of candidates not yet implemented.

Usage:
    python scripts/rank_new_sites.py
    python scripts/rank_new_sites.py --sites-md docs/development/NEW_SITES.md
    python scripts/rank_new_sites.py --output report.md
"""

import argparse
import ast
import io
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# Force UTF-8 on Windows stdout so emoji/unicode in markdown renders correctly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
FLUFFLE_URL = "https://fluffle.cc/fmfy"

DEFAULT_ROADMAP = REPO_ROOT / "NEW_SITES_ROADMAP.md"
DEFAULT_TRACKER = REPO_ROOT / "docs" / "research" / "FLUFFLE_FMFY_TRACKER.md"
DEFAULT_NEW_SITES = REPO_ROOT / "docs" / "development" / "NEW_SITES.md"

# Difficulty score used for sorting (lower = easier = higher priority)
DIFFICULTY_SCORE = {
    "easy": 1,
    "easy-medium": 2,
    "medium": 3,
    "medium-hard": 4,
    "hard": 5,
    "unknown": 6,
}
DIFFICULTY_LABELS = sorted(DIFFICULTY_SCORE, key=len, reverse=True)

DEFAULT_CATEGORIES = {
    "Adult Movies / Grindhouse",
    "Asian / JAV",
    "Cam Models",
    "Hentai Anime",
    "Leak Sites",
    "Streaming",
}

EXCLUDED_HOSTS = {
    "cse.google.com",
    "discord.gg",
    "fmhy.net",
    "github.com",
    "gitlab.com",
    "greasyfork.org",
    "pastebin.com",
    "reddit.com",
    "redd.it",
    "sleazyfork.org",
    "t.me",
    "vkvideo.ru",
    "www.reddit.com",
}

EXCLUDED_NAMES = {
    "add features",
    "add to greasyfork",
    "android client",
    "bypasser",
    "discord",
    "downloader",
    "extension",
    "features",
    "forum",
    "general ddl sites",
    "general torrent sites",
    "github",
    "invite",
    "login",
    "mirrors",
    "note",
    "nsfw games",
    "porn app",
    "register",
    "refresh",
    "telegram",
    "verification",
    "vpn",
    "warning",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize(name: str) -> str:
    """Lowercase, strip punctuation/spaces — used for fuzzy matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_existing_modules() -> set[str]:
    """Return normalized names of active site modules currently in the addon."""
    skip = {"__init__", "soup_spec"}
    excluded = load_excluded_site_modules()
    return {
        normalize(p.stem)
        for p in SITES_DIR.glob("*.py")
        if p.stem not in skip and p.name not in excluded
    }


def load_excluded_site_modules() -> set[str]:
    """Read sites/__init__.py and return modules excluded from runtime listing."""
    init_file = SITES_DIR / "__init__.py"
    if not init_file.exists():
        return set()

    try:
        tree = ast.parse(init_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "EXCLUDED_SITE_MODULES":
                    value = ast.literal_eval(node.value)
                    return {str(item) for item in value}
    return set()


def host_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


def site_keys(site: dict) -> set[str]:
    """Return normalized aliases for matching a Fluffle entry to known sites."""
    keys = {site["name"]}

    host = host_from_url(site["url"]).split("@")[-1].split(":")[0]
    if host:
        labels = [part for part in host.split(".") if part]
        labels = [part for part in labels if not re.fullmatch(r"www\d*", part)]
        if labels:
            keys.add(normalize(labels[0]))
        if len(labels) >= 2:
            keys.add(normalize(labels[-2]))
            keys.add(normalize("".join(labels[:-1])))

    return {key for key in keys if key}


def is_supported_candidate(site: dict, include_all: bool = False) -> bool:
    """Default to candidates that fit a video add-on and skip tool/index noise."""
    if include_all:
        return True

    if site["category"] not in DEFAULT_CATEGORIES:
        return False

    host = host_from_url(site["url"])
    if host in EXCLUDED_HOSTS or host.endswith(".onion"):
        return False

    raw_name = site["raw_name"].strip().lower()
    if raw_name in EXCLUDED_NAMES:
        return False
    if re.fullmatch(r"\d+", raw_name):
        return False

    return True


# ---------------------------------------------------------------------------
# Markdown parsers
# ---------------------------------------------------------------------------

def extract_names_from_md(text: str) -> set[str]:
    """Pull every bolded **Name** or `name` token from markdown text."""
    names: set[str] = set()
    for m in re.finditer(r"\*\*([^*]+)\*\*", text):
        names.add(normalize(m.group(1)))
    for m in re.finditer(r"`([^`]+)`", text):
        names.add(normalize(m.group(1)))
    return names


def parse_roadmap(path: Path) -> dict[str, str]:
    """
    Parse NEW_SITES_ROADMAP.md style files.
    Returns {normalized_name: difficulty} for every candidate entry.
    """
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    current_difficulty = "unknown"

    difficulty_map = {
        "easy candidates": "easy",
        "medium candidates": "medium",
        "hard candidates": "hard",
        "tier 1": "easy",
        "tier 2": "medium",
        "tier 3": "hard",
    }

    for line in text.splitlines():
        lower = line.lower()
        for key, diff in difficulty_map.items():
            if key in lower and line.startswith("#"):
                current_difficulty = diff
                break

        # Table rows: | **SiteName** | ... |
        for m in re.finditer(r"\|\s*\*\*([^*]+)\*\*\s*\|", line):
            name = m.group(1).strip()
            key = normalize(name)
            if key and key not in result:
                result[key] = current_difficulty

    return result


def parse_tracker(path: Path) -> dict[str, str]:
    """
    Parse FLUFFLE_FMFY_TRACKER.md candidate queue table.
    Returns {normalized_name: difficulty}.
    """
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    in_queue = False

    for line in text.splitlines():
        if "Candidate Queue" in line:
            in_queue = True
            continue
        if in_queue and line.startswith("##"):
            in_queue = False

        if not in_queue:
            continue

        # Table row: | `name` | Category | Easy | ...
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*[^|]+\|\s*([^|]+)\|", line)
        if m:
            raw_name = m.group(1).strip()
            diff_raw = m.group(2).strip().lower()
            # Normalize difficulty string
            diff = "unknown"
            for key in DIFFICULTY_LABELS:
                if key in diff_raw:
                    diff = key
                    break
            for alias in re.split(r"\s*/\s*", raw_name):
                key = normalize(alias)
                if key:
                    result[key] = diff

    return result


def parse_tracker_implemented(path: Path) -> set[str]:
    """Parse tracker aliases listed before Candidate Queue as already supported."""
    if not path.exists():
        return set()

    text = path.read_text(encoding="utf-8")
    result: set[str] = set()
    before_queue = text.split("## Candidate Queue", 1)[0]
    supported = before_queue.split("## Already Supported", 1)
    if len(supported) < 2:
        return result
    supported_text = supported[1].split("## Existing But Special State", 1)[0]

    for m in re.finditer(r"`([^`]+)`", supported_text):
        raw_name = m.group(1).strip()
        for alias in re.split(r"\s*/\s*", raw_name):
            key = normalize(alias)
            if key:
                result.add(key)
    return result


def parse_new_sites(path: Path) -> dict[str, str]:
    """Parse docs/development/NEW_SITES.md tier tables."""
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    current_tier = "unknown"

    for line in text.splitlines():
        lower = line.lower()
        if line.startswith("#"):
            if "tier 1" in lower or "easy" in lower:
                current_tier = "easy"
            elif "tier 2" in lower or "medium" in lower:
                current_tier = "medium"
            elif "tier 3" in lower or "hard" in lower:
                current_tier = "hard"
            elif "recently added" in lower or "already" in lower:
                current_tier = "implemented"

        table_match = re.match(r"\|\s*\*\*([^*]+)\*\*\s*\|(.+)", line)
        if table_match:
            key = normalize(table_match.group(1))
            row_tail = table_match.group(2).lower()
            value = current_tier
            if "✅" in row_tail or "integrated" in row_tail or "added" in row_tail:
                value = "implemented"
            elif any(status in row_tail for status in ("parked", "changed", "redirect")):
                value = "unavailable"
            if key and key not in result:
                result[key] = value
            continue

        for m in re.finditer(r"\*\*([^*]+)\*\*", line):
            key = normalize(m.group(1))
            if key and key not in result:
                result[key] = current_tier

    return result


# ---------------------------------------------------------------------------
# Fluffle fetcher
# ---------------------------------------------------------------------------

def fetch_fluffle(url: str = FLUFFLE_URL) -> list[dict]:
    """
    Fetch and parse fluffle.cc/fmfy.
    Returns list of {name, url, category, raw_name}.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch {url}: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    sites: list[dict] = []
    current_category = "Unknown"

    # Walk all elements and track headings + links
    for el in soup.find_all(["h1", "h2", "h3", "h4", "a", "li"]):
        tag = el.name
        if tag in ("h1", "h2", "h3", "h4"):
            text = el.get_text(strip=True)
            if text:
                current_category = text

        elif tag == "a":
            href = el.get("href", "")
            name = el.get_text(strip=True)
            if not name or not href:
                continue
            # Only external links (site links start with http/https)
            if not href.startswith("http"):
                continue
            # Skip self-referential fluffle links
            if "fluffle.cc" in href:
                continue
            sites.append({
                "raw_name": name,
                "name": normalize(name),
                "url": href.rstrip("/"),
                "category": current_category,
            })

    return sites


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def rank_candidates(
    fluffle_sites: list[dict],
    existing_modules: set[str],
    roadmap: dict[str, str],
    tracker: dict[str, str],
    new_sites_md: dict[str, str],
    tracker_implemented: set[str] | None = None,
    include_all: bool = False,
) -> tuple[list[dict], list[dict]]:
    """
    Split fluffle sites into:
      - new_candidates: not yet implemented, with difficulty + source annotations
      - already_implemented: already in the addon

    New candidates are sorted by: difficulty (easy first), then category, then name.
    """
    # Merge all known-difficulty sources; tracker is most detailed
    all_known: dict[str, str] = {}
    all_known.update(roadmap)
    all_known.update(new_sites_md)
    all_known.update(tracker)

    # Sites marked implemented in any MD
    implemented_in_md: set[str] = {
        k for k, v in new_sites_md.items() if "implement" in v
    }
    if tracker_implemented:
        implemented_in_md.update(tracker_implemented)
    unavailable_in_md: set[str] = {
        k for k, v in new_sites_md.items() if "unavailable" in v
    }

    seen: set[str] = set()
    new_candidates: list[dict] = []
    already_implemented: list[dict] = []

    for site in fluffle_sites:
        key = site["name"]
        if not key or key in seen:
            continue
        seen.add(key)
        if not is_supported_candidate(site, include_all=include_all):
            continue

        keys = site_keys(site)
        if keys & unavailable_in_md:
            continue

        is_implemented = (
            bool(keys & existing_modules)
            or bool(keys & implemented_in_md)
        )

        if is_implemented:
            already_implemented.append(site)
            continue

        # Determine difficulty from known sources
        difficulty = next((all_known[k] for k in keys if k in all_known), "unknown")

        # Determine if it was previously tracked in any MD
        in_roadmap = bool(keys & roadmap.keys())
        in_tracker = bool(keys & tracker.keys())

        new_candidates.append({
            **site,
            "difficulty": difficulty,
            "diff_score": DIFFICULTY_SCORE.get(difficulty, 6),
            "in_roadmap": in_roadmap,
            "in_tracker": in_tracker,
            "is_new": not (in_roadmap or in_tracker),
        })

    # Sort: truly new first (not in any MD), then by difficulty, then category
    new_candidates.sort(
        key=lambda s: (
            0 if s["is_new"] else 1,
            s["diff_score"],
            s["category"],
            s["raw_name"].lower(),
        )
    )

    return new_candidates, already_implemented


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def render_report(
    candidates: list[dict],
    implemented: list[dict],
    fluffle_url: str,
) -> str:
    lines = [
        "# Fluffle Site Ranking Report",
        f"Source: {fluffle_url}",
        "",
        f"**{len(candidates)}** unimplemented candidates found.",
        f"**{len(implemented)}** fluffle-listed sites already in the addon.",
        "",
    ]

    # Split into "new to all MDs" vs "known but not implemented"
    brand_new = [s for s in candidates if s["is_new"]]
    known_queue = [s for s in candidates if not s["is_new"]]

    if brand_new:
        lines += [
            "## Brand New (not in any roadmap or tracker)",
            "",
            "| Site | URL | Category | Difficulty |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for s in brand_new:
            lines.append(
                f"| **{s['raw_name']}** | {s['url']} | {s['category']} | {s['difficulty']} |"
            )
        lines.append("")

    if known_queue:
        lines += [
            "## In Roadmap/Tracker but Not Yet Implemented",
            "",
            "| Site | URL | Category | Difficulty | Sources |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for s in known_queue:
            sources = []
            if s["in_roadmap"]:
                sources.append("roadmap")
            if s["in_tracker"]:
                sources.append("tracker")
            lines.append(
                f"| **{s['raw_name']}** | {s['url']} | {s['category']} | {s['difficulty']} | {', '.join(sources)} |"
            )
        lines.append("")

    if implemented:
        lines += [
            "## Already Implemented",
            "",
            "| Site | URL | Category |",
            "| :--- | :--- | :--- |",
        ]
        for s in implemented:
            lines.append(f"| {s['raw_name']} | {s['url']} | {s['category']} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Rank new sites from fluffle.cc/fmfy")
    parser.add_argument(
        "--sites-md",
        type=Path,
        default=DEFAULT_ROADMAP,
        help="Path to the new-sites roadmap markdown (default: NEW_SITES_ROADMAP.md)",
    )
    parser.add_argument(
        "--tracker-md",
        type=Path,
        default=DEFAULT_TRACKER,
        help="Path to the Fluffle tracker markdown",
    )
    parser.add_argument(
        "--new-sites-md",
        type=Path,
        default=DEFAULT_NEW_SITES,
        help="Path to docs/development/NEW_SITES.md",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to this file instead of stdout",
    )
    parser.add_argument(
        "--url",
        default=FLUFFLE_URL,
        help=f"Override the Fluffle URL (default: {FLUFFLE_URL})",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include non-video categories and external tool/index links.",
    )
    args = parser.parse_args()

    print(f"Fetching {args.url} ...", file=sys.stderr)
    fluffle_sites = fetch_fluffle(args.url)
    if not fluffle_sites:
        print("[WARN] No sites parsed from Fluffle page.", file=sys.stderr)

    print(f"  -> {len(fluffle_sites)} entries parsed from Fluffle", file=sys.stderr)

    existing = load_existing_modules()
    print(f"  -> {len(existing)} existing site modules found", file=sys.stderr)

    roadmap = parse_roadmap(args.sites_md)
    print(f"  -> {len(roadmap)} entries from roadmap ({args.sites_md.name})", file=sys.stderr)

    tracker = parse_tracker(args.tracker_md)
    print(f"  -> {len(tracker)} entries from tracker ({args.tracker_md.name})", file=sys.stderr)

    tracker_implemented = parse_tracker_implemented(args.tracker_md)
    print(f"  -> {len(tracker_implemented)} implemented aliases from tracker", file=sys.stderr)

    new_sites = parse_new_sites(args.new_sites_md)
    print(f"  -> {len(new_sites)} entries from new-sites md ({args.new_sites_md.name})", file=sys.stderr)

    candidates, implemented = rank_candidates(
        fluffle_sites,
        existing,
        roadmap,
        tracker,
        new_sites,
        tracker_implemented=tracker_implemented,
        include_all=args.include_all,
    )

    report = render_report(candidates, implemented, args.url)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
