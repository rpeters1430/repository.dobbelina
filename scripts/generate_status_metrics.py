#!/usr/bin/env python3
"""Generate canonical project status metrics.

Collects:
- addon version
- site counts and migration status
- test counts from pytest collection

Writes a single canonical status file at docs/status/STATUS_METRICS.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
ADDON_XML = ROOT / "plugin.video.cumination" / "addon.xml"
SITES_DIR = ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
CANONICAL_STATUS = ROOT / "docs" / "status" / "STATUS_METRICS.md"

SITE_FILE_EXCLUDES = {"__init__.py", "soup_spec.py"}
SITE_ANALYSIS_REPORT = ROOT / "results" / "site_analysis.json"


@dataclass
class SiteMetrics:
    total: int
    migrated_beautifulsoup: int
    api_or_cam: int
    migration_complete: int
    migration_pending: int


@dataclass
class TestMetrics:
    total_collected: int | None
    collection_seconds: float | None
    raw_summary: str


@dataclass
class StatusMetrics:
    generated_at_utc: str
    version: str
    sites: SiteMetrics
    tests: TestMetrics


def parse_version(addon_xml: Path) -> str:
    tree = ET.parse(addon_xml)
    addon = tree.getroot()
    return addon.attrib.get("version", "unknown")


def iter_site_files(sites_dir: Path) -> Iterable[Path]:
    for path in sorted(sites_dir.glob("*.py")):
        if path.name not in SITE_FILE_EXCLUDES:
            yield path


def calculate_site_metrics(sites_dir: Path) -> SiteMetrics:
    total = 0
    migrated_beautifulsoup = 0
    api_or_cam = 0

    for site_file in iter_site_files(sites_dir):
        total += 1
        text = site_file.read_text(encoding="utf-8", errors="ignore")

        if "BeautifulSoup" in text:
            migrated_beautifulsoup += 1

        if re.search(r"siteType\s*=\s*['\"]Cam['\"]", text):
            api_or_cam += 1

    migration_complete = min(total, migrated_beautifulsoup + api_or_cam)
    migration_pending = max(0, total - migration_complete)
    return SiteMetrics(
        total=total,
        migrated_beautifulsoup=migrated_beautifulsoup,
        api_or_cam=api_or_cam,
        migration_complete=migration_complete,
        migration_pending=migration_pending,
    )


def calculate_site_metrics_from_analysis(timeout: int) -> SiteMetrics | None:
    cmd = ["python", "scripts/analyze_sites.py"]
    try:
        subprocess.run(
            cmd,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if not SITE_ANALYSIS_REPORT.exists():
        return None

    try:
        report = json.loads(SITE_ANALYSIS_REPORT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    sites = report.get("sites", [])
    if not isinstance(sites, list) or not sites:
        return None

    total = len(sites)
    migrated_beautifulsoup = sum(1 for site in sites if site.get("uses_beautifulsoup"))
    api_or_cam = sum(1 for site in sites if site.get("is_webcam"))
    migration_complete = min(total, migrated_beautifulsoup + api_or_cam)
    migration_pending = max(0, total - migration_complete)
    return SiteMetrics(
        total=total,
        migrated_beautifulsoup=migrated_beautifulsoup,
        api_or_cam=api_or_cam,
        migration_complete=migration_complete,
        migration_pending=migration_pending,
    )


def collect_test_metrics(timeout: int) -> TestMetrics:
    cmd = ["pytest", "--collect-only", "-q"]
    try:
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

    return f"""# Canonical Status Metrics

> Source of truth for version, site migration, and test count metrics.
> Generated by `python scripts/generate_status_metrics.py`.
> Do not hand-edit metric values.

- Generated at (UTC): **{metrics.generated_at_utc}**
- Addon version: **{metrics.version}**

## Site Migration Status

| Metric | Value |
| --- | ---: |
| Total site modules | {metrics.sites.total} |
| BeautifulSoup-migrated modules | {metrics.sites.migrated_beautifulsoup} |
| API/Cam modules (migration exempt) | {metrics.sites.api_or_cam} |
| Migration complete (`migrated + exempt`) | {metrics.sites.migration_complete}/{metrics.sites.total} |
| Migration pending | {metrics.sites.migration_pending} |

## Test Status

| Metric | Value |
| --- | ---: |
| Total tests collected (`pytest --collect-only -q`) | {collected_display} |
| Collection duration | {duration_display} |
| Collector summary | `{metrics.tests.raw_summary}` |

## Sync Checklist (for PRs that touch status metrics)

- [ ] Ran `python scripts/generate_status_metrics.py`.
- [ ] Committed updated `docs/status/STATUS_METRICS.md`.
- [ ] Updated any status docs to reference this canonical file instead of hardcoding numbers.
"""


def generate_status_file(timeout: int, analysis_timeout: int) -> StatusMetrics:
    site_metrics = calculate_site_metrics_from_analysis(timeout=analysis_timeout)
    if site_metrics is None:
        site_metrics = calculate_site_metrics(SITES_DIR)

    status = StatusMetrics(
        generated_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        version=parse_version(ADDON_XML),
        sites=site_metrics,
        tests=collect_test_metrics(timeout=timeout),
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
        "--analysis-timeout",
        type=int,
        default=180,
        help="Timeout in seconds for site analysis (used for migration status)",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print metrics JSON summary to stdout",
    )
    args = parser.parse_args()

    status = generate_status_file(
        timeout=args.pytest_timeout, analysis_timeout=args.analysis_timeout
    )
    if args.print_json:
        print(
            json.dumps(
                {
                    "generated_at_utc": status.generated_at_utc,
                    "version": status.version,
                    "sites": status.sites.__dict__,
                    "tests": status.tests.__dict__,
                    "status_file": str(CANONICAL_STATUS.relative_to(ROOT)),
                },
                indent=2,
            )
        )

    print(f"Wrote {CANONICAL_STATUS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
