#!/usr/bin/env python3
"""Generate canonical project status metrics.

Collects:
- addon version
- site counts and migration status
- test counts from pytest collection
- per-site inventory with BeautifulSoup/Regex markers
- top broken sites from KNOWN_ISSUES.md

Writes a single canonical status file at docs/status/STATUS_METRICS.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
ADDON_XML = ROOT / "plugin.video.cumination" / "addon.xml"
CHANGELOG = ROOT / "plugin.video.cumination" / "changelog.txt"
SITES_DIR = ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
TESTS_DIR = ROOT / "tests"
KNOWN_ISSUES = ROOT / "docs" / "development" / "KNOWN_ISSUES.md"
CANONICAL_STATUS = ROOT / "docs" / "status" / "STATUS_METRICS.md"

SITE_FILE_EXCLUDES = {"__init__.py", "soup_spec.py", "stripchat.py"}
SITE_ANALYSIS_REPORT = ROOT / "results" / "site_analysis.json"

BS_MARKERS = (
    "utils.parse_html(",
    "BeautifulSoup(",
    ".select(",
    ".select_one(",
)

REGEX_MARKERS = (
    "re.compile(",
    "re.findall(",
    "re.finditer(",
)


@dataclass
class SiteInfo:
    name: str
    uses_bs4: bool
    uses_regex: bool
    has_tests: bool
    url: str | None = None


@dataclass
class SiteMetrics:
    total: int
    migrated_beautifulsoup: int
    api_or_cam: int
    migration_complete: int
    migration_pending: int
    inventory: list[SiteInfo] = field(default_factory=list)


@dataclass
class TestMetrics:
    total_collected: int | None
    collection_seconds: float | None
    raw_summary: str


@dataclass
class StatusMetrics:
    generated_at_utc: str
    version: str
    changelog_version: str
    sites: SiteMetrics
    tests: TestMetrics
    known_issues: list[tuple[str, str]] = field(default_factory=list)


def parse_versions(addon_xml: Path, changelog: Path) -> tuple[str, str]:
    tree = ET.parse(addon_xml)
    addon = tree.getroot()
    addon_version = addon.attrib.get("version", "unknown")

    changelog_version = "unknown"
    if changelog.exists():
        changelog_text = changelog.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"\[B\]Version\s+([0-9][^\[]+)\[/B\]", changelog_text)
        if match:
            changelog_version = match.group(1).strip()
    
    return addon_version, changelog_version


def iter_site_files(sites_dir: Path) -> Iterable[Path]:
    for path in sorted(sites_dir.glob("*.py")):
        if path.name not in SITE_FILE_EXCLUDES:
            yield path


def collect_tested_sites() -> set[str]:
    tested = set()
    site_tests_dir = TESTS_DIR / "sites"
    if site_tests_dir.exists():
        for path in sorted(site_tests_dir.glob("test_*.py")):
            site_name = path.stem.removeprefix("test_")
            if site_name:
                tested.add(site_name)

    smoke_dir = TESTS_DIR / "smoke_generated"
    if smoke_dir.exists():
        for path in sorted(smoke_dir.glob("test_smoke_*.py")):
            site_name = path.stem.removeprefix("test_smoke_")
            if site_name:
                tested.add(site_name)

    return tested


def calculate_site_metrics(sites_dir: Path) -> SiteMetrics:
    total = 0
    migrated_beautifulsoup = 0
    api_or_cam = 0
    inventory = []
    tested_sites = collect_tested_sites()

    for site_file in iter_site_files(sites_dir):
        text = site_file.read_text(encoding="utf-8", errors="ignore")

        uses_bs4 = any(marker in text for marker in BS_MARKERS)
        uses_regex = any(marker in text for marker in REGEX_MARKERS)
        is_cam_file = bool(re.search(r"siteType\s*=\s*['\"]Cam['\"]", text))
        
        # Extract all AdultSite registrations
        # Pattern: AdultSite( "id", "label", "url" ... )
        registrations = re.findall(
            r"AdultSite\s*\(\s*['\"](?P<id>.+?)['\"]\s*,\s*['\"](?P<label>.+?)['\"]\s*,\s*['\"](?P<url>.+?)['\"]",
            text,
            re.DOTALL
        )

        if not registrations:
            # Fallback for files that might not use the standard constructor pattern directly or use variables
            total += 1
            if uses_bs4:
                migrated_beautifulsoup += 1
            if is_cam_file:
                api_or_cam += 1
            
            inventory.append(
                SiteInfo(
                    name=site_file.stem,
                    uses_bs4=uses_bs4,
                    uses_regex=uses_regex,
                    has_tests=site_file.stem in tested_sites,
                    url=None
                )
            )
            continue

        for site_id, site_label, site_url in registrations:
            total += 1
            if uses_bs4:
                migrated_beautifulsoup += 1
            
            is_cam_site = is_cam_file
            if not is_cam_site:
                # Look for webcam=True near this registration
                pattern = r"AdultSite\s*\(\s*['\"]{0}['\"].*?webcam\s*=\s*True".format(re.escape(site_id))
                if re.search(pattern, text, re.DOTALL):
                    is_cam_site = True

            if is_cam_site:
                api_or_cam += 1

            inventory.append(
                SiteInfo(
                    name=site_id,
                    uses_bs4=uses_bs4,
                    uses_regex=uses_regex,
                    has_tests=site_id in tested_sites or site_file.stem in tested_sites,
                    url=site_url
                )
            )

    migration_complete = min(total, migrated_beautifulsoup + api_or_cam)
    migration_pending = max(0, total - migration_complete)
    return SiteMetrics(
        total=total,
        migrated_beautifulsoup=migrated_beautifulsoup,
        api_or_cam=api_or_cam,
        migration_complete=migration_complete,
        migration_pending=migration_pending,
        inventory=inventory,
    )


def parse_known_issues(limit: int = 10) -> list[tuple[str, str]]:
    if not KNOWN_ISSUES.exists():
        return []
    issues_text = KNOWN_ISSUES.read_text(encoding="utf-8", errors="ignore")
    issues: list[tuple[str, str]] = []
    for line in issues_text.splitlines():
        line = line.strip()
        m = re.match(r"^-\s+\*\*(.+?)\*\*\s+[–-]\s+(.+)$", line)
        if m:
            issues.append((m.group(1).strip(), m.group(2).strip()))
        if len(issues) >= limit:
            break
    return issues


def collect_test_metrics(timeout: int) -> TestMetrics:
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
    try:
        # On Windows we might need to use the venv python if available
        # But ROOT / .venv / Scripts / python should be handled by the caller or env
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        reason = f"pytest collection unavailable: {exc}"
        return TestMetrics(
            total_collected=None, collection_seconds=None, raw_summary=reason
        )

    output = (completed.stdout or "") + (completed.stderr or "")
    lines = [line.strip() for line in output.splitlines() if line.strip()]

    summary_line = "pytest collection summary not found"
    total_collected = None
    seconds = None

    for line in reversed(lines):
        match = re.search(r"(?P<count>\d+) tests collected in (?P<sec>[0-9.]+)s", line)
        if match:
            summary_line = line
            total_collected = int(match.group("count"))
            seconds = float(match.group("sec"))
            break

    if completed.returncode != 0 and total_collected is None:
        summary_line = f"pytest collect failed with exit code {completed.returncode}"

    return TestMetrics(
        total_collected=total_collected,
        collection_seconds=seconds,
        raw_summary=summary_line,
    )


def render_markdown(metrics: StatusMetrics) -> str:
    collected_display = (
        str(metrics.tests.total_collected)
        if metrics.tests.total_collected is not None
        else "unavailable"
    )
    duration_display = (
        f"{metrics.tests.collection_seconds:.2f}s"
        if metrics.tests.collection_seconds is not None
        else "n/a"
    )

    lines = [
        "# Canonical Status Metrics",
        "",
        "> Source of truth for version, site migration, and test count metrics.",
        "> Generated by `python scripts/generate_status_metrics.py`.",
        "> Do not hand-edit metric values.",
        "",
        f"- Generated at (UTC): **{metrics.generated_at_utc}**",
        f"- Addon version: **{metrics.version}**",
        f"- Latest changelog: **{metrics.changelog_version}**",
        "",
        "## Site Migration Status",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total registered sites | {metrics.sites.total} |",
        f"| BeautifulSoup-migrated sites | {metrics.sites.migrated_beautifulsoup} |",
        f"| API/Cam sites (migration exempt) | {metrics.sites.api_or_cam} |",
        f"| Migration complete (`migrated + exempt`) | {metrics.sites.migration_complete}/{metrics.sites.total} |",
        f"| Migration pending | {metrics.sites.migration_pending} |",
        "",
        "## Test Status",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total tests collected (`pytest --collect-only -q`) | {collected_display} |",
        f"| Collection duration | {duration_display} |",
        f"| Collector summary | `{metrics.tests.raw_summary}` |",
        "",
        "## Top broken / known issue sites",
        "",
    ]

    if metrics.known_issues:
        for site, desc in metrics.known_issues:
            lines.append(f"- **{site}** — {desc}")
    else:
        lines.append("- No known issue bullets detected in `docs/development/KNOWN_ISSUES.md`.")

    lines.extend([
        "",
        "## Site inventory",
        "",
        "| Site | URL | BS4 | Regex | Tests |",
        "|---|---|---:|---:|---:|",
    ])

    for site in metrics.sites.inventory:
        bs = "✅" if site.uses_bs4 else "❌"
        rx = "✅" if site.uses_regex else "❌"
        tested = "✅" if site.has_tests else "❌"
        site_link = f"[`{site.name}`]({site.url})" if site.url else f"`{site.name}`"
        lines.append(f"| {site_link} | {site.url or 'n/a'} | {bs} | {rx} | {tested} |")

    lines.extend([
        "",
        "## Sync Checklist (for PRs that touch status metrics)",
        "",
        "- [ ] Ran `python scripts/generate_status_metrics.py`.",
        "- [ ] Committed updated `docs/status/STATUS_METRICS.md`.",
        "- [ ] Updated any status docs to reference this canonical file instead of hardcoding numbers.",
    ])

    return "\n".join(lines)


def generate_status_file(timeout: int) -> StatusMetrics:
    addon_version, changelog_version = parse_versions(ADDON_XML, CHANGELOG)
    
    status = StatusMetrics(
        generated_at_utc=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        version=addon_version,
        changelog_version=changelog_version,
        sites=calculate_site_metrics(SITES_DIR),
        tests=collect_test_metrics(timeout=timeout),
        known_issues=parse_known_issues(limit=10),
    )

    CANONICAL_STATUS.parent.mkdir(parents=True, exist_ok=True)
    CANONICAL_STATUS.write_text(render_markdown(status), encoding="utf-8")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate canonical project status metrics"
    )
    parser.add_argument(
        "--pytest-timeout",
        type=int,
        default=180,
        help="Timeout in seconds for pytest test collection",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print metrics JSON summary to stdout",
    )
    args = parser.parse_args()

    status = generate_status_file(timeout=args.pytest_timeout)
    if args.print_json:
        # Simplified JSON for brevity
        print(
            json.dumps(
                {
                    "generated_at_utc": status.generated_at_utc,
                    "version": status.version,
                    "sites_total": status.sites.total,
                    "tests_collected": status.tests.total_collected,
                    "status_file": str(CANONICAL_STATUS.relative_to(ROOT)),
                },
                indent=2,
            )
        )

    print(f"Wrote {CANONICAL_STATUS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    main()
