#!/usr/bin/env python3
"""Generate GitHub triage request actions from strict site health state and history."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.site_health_types import HealthState

SIG_RE = re.compile(r"Failure Signature:\s*`([^`]+)`", re.IGNORECASE)


def extract_sig_from_body(body: str) -> str:
    if not body:
        return ""
    m = SIG_RE.search(body)
    return m.group(1).strip() if m else ""


def find_existing_issue(site: str, existing_issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    marker = f"<!-- strict-site-health:{site} -->"
    for issue in existing_issues:
        body = issue.get("body", "")
        title = issue.get("title", "")
        if marker in body or f"[Site Monitor] {site}" in title:
            return issue
    return None


def generate_strict_triage_requests(
    latest: dict[str, Any],
    history: dict[str, Any],
    existing_issues: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Generate deterministic issue triage actions for priority sites."""
    if existing_issues is None:
        existing_issues = []

    requests = []
    latest_sites = latest.get("sites", {})
    history_sites = history.get("sites", {})

    all_sites = sorted(set(list(latest_sites.keys()) + list(history_sites.keys())))

    for site in all_sites:
        rep = latest_sites.get(site, {})
        hist = history_sites.get(site, {})

        state = rep.get("state", HealthState.NOT_TESTED)
        consec = hist.get("consecutive_healthy", 0)
        sig = rep.get("failure_signature") or hist.get("open_failure_signature", "")
        failed_stage = rep.get("failed_stage") or "unknown"
        classification = rep.get("classification") or "UNKNOWN"
        message = rep.get("message") or "No message provided"

        existing = find_existing_issue(site, existing_issues)
        is_open = existing and existing.get("state", "").upper() == "OPEN"

        if state in (HealthState.BROKEN, HealthState.BLOCKED, HealthState.HARNESS_ERROR):
            if state == HealthState.HARNESS_ERROR:
                title = f"[Site Monitor] Monitoring infrastructure failure ({site})"
                labels = ["site-monitor", "failure/harness"]
            elif state == HealthState.BLOCKED:
                title = f"[Site Monitor] {site} is blocked"
                labels = ["site-monitor", "failure/blocked"]
            else:
                title = f"[Site Monitor] {site} is broken"
                labels = ["site-monitor", "failure/broken"]

            body = (
                f"<!-- strict-site-health:{site} -->\n"
                f"# {title}\n\n"
                f"- **State:** `{state}`\n"
                f"- **Failed Stage:** `{failed_stage}`\n"
                f"- **Classification:** `{classification}`\n"
                f"- **Failure Signature:** `{sig}`\n"
                f"- **Message:** {message}\n\n"
                "## Reproduction Command\n"
                "```bash\n"
                f"python scripts/strict_site_monitor.py --site {site} --out results\n"
                "```\n"
            )

            if not existing or not is_open:
                requests.append({
                    "action": "CREATE_OR_REOPEN",
                    "site": site,
                    "title": title,
                    "body": body,
                    "labels": labels,
                    "failure_signature": sig,
                    "issue_number": existing.get("number") if existing else None,
                })
            else:
                existing_sig = extract_sig_from_body(existing.get("body", "")) or existing.get("signature", "")
                if existing_sig != sig:
                    requests.append({
                        "action": "UPDATE",
                        "site": site,
                        "title": title,
                        "body": body,
                        "labels": labels,
                        "failure_signature": sig,
                        "issue_number": existing.get("number"),
                        "comment": f"Failure signature updated to `{sig}`.\nMessage: {message}",
                    })
                else:
                    requests.append({
                        "action": "NONE",
                        "site": site,
                        "issue_number": existing.get("number"),
                    })

        elif state == HealthState.HEALTHY:
            if is_open and existing:
                if consec >= 2:
                    requests.append({
                        "action": "CLOSE",
                        "site": site,
                        "issue_number": existing.get("number"),
                        "comment": f"Closing issue: `{site}` has reached {consec} consecutive healthy passes in strict monitoring.",
                    })
                else:
                    requests.append({
                        "action": "NONE",
                        "site": site,
                        "issue_number": existing.get("number"),
                        "comment": f"Recovery in progress: `{site}` has reached {consec}/2 consecutive healthy passes.",
                    })
            else:
                requests.append({
                    "action": "NONE",
                    "site": site,
                })

        else:
            requests.append({
                "action": "NONE",
                "site": site,
            })

    return requests


def main():
    parser = argparse.ArgumentParser(description="Generate strict triage requests.")
    parser.add_argument("--latest", required=True, help="Path to strict_health_latest.json")
    parser.add_argument("--history", required=True, help="Path to strict_history.json")
    parser.add_argument("--out", required=True, help="Path to output triage_requests.json")
    parser.add_argument("--existing-issues", help="Path to existing issues JSON file from gh")
    args = parser.parse_args()

    latest = json.loads(Path(args.latest).read_text(encoding="utf-8"))
    history = json.loads(Path(args.history).read_text(encoding="utf-8"))

    existing_issues = []
    if args.existing_issues and Path(args.existing_issues).exists():
        try:
            existing_issues = json.loads(Path(args.existing_issues).read_text(encoding="utf-8"))
        except Exception:
            existing_issues = []

    requests = generate_strict_triage_requests(latest, history, existing_issues)
    Path(args.out).write_text(json.dumps(requests, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
