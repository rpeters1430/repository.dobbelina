#!/usr/bin/env python3
"""Generate GitHub triage request actions from strict site health state and history."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.site_health_types import HealthState

SIG_RE = re.compile(r"Failure Signature:\*{0,2}\s*`([^`]+)`", re.IGNORECASE)


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

        profile = rep.get("record", {}).get("profile", {})
        ignored_states = profile.get("triage", {}).get("ignored_states", [])
        state_value = state.value if hasattr(state, "value") else str(state)
        if state_value in ignored_states:
            if is_open and existing:
                requests.append({
                    "action": "CLOSE",
                    "site": site,
                    "issue_number": existing.get("number"),
                    "comment": (
                        f"Closing issue: `{site}` state `{state_value}` is ignored by triage policy."
                    ),
                })
            else:
                requests.append({
                    "action": "NONE",
                    "site": site,
                })
            continue

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


BROAD_SUMMARY_MARKER = "<!-- broad-site-health:summary -->"


def _find_broad_summary_issue(existing_issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    for issue in existing_issues:
        if BROAD_SUMMARY_MARKER in (issue.get("body") or ""):
            return issue
    return None


def generate_broad_summary_request(
    diff: dict[str, Any],
    existing_issues: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Create, update, or close a single rolling summary issue for broad smoke failures."""
    if existing_issues is None:
        existing_issues = []

    actionable_new = [
        f for f in diff.get("new_failures", [])
        if f.get("class") != "ENV" and not f.get("is_flaky")
    ]
    actionable_persistent = [
        f for f in diff.get("persistent_failures", [])
        if f.get("class") != "ENV" and not f.get("is_flaky")
    ]
    all_actionable = actionable_new + actionable_persistent

    existing = _find_broad_summary_issue(existing_issues)
    is_open = bool(existing and existing.get("state", "").upper() == "OPEN")

    if not all_actionable:
        if is_open and existing:
            return {
                "action": "CLOSE",
                "site": "broad-smoke",
                "issue_number": existing.get("number"),
                "comment": "Closing issue: 0 actionable non-ENV failures remain in broad smoke monitoring.",
            }
        return None

    sig_payload = "|".join(
        sorted(f"{f.get('site')}:{f.get('class', 'UNKNOWN')}" for f in all_actionable)
    )
    sig = hashlib.sha256(sig_payload.encode("utf-8")).hexdigest()[:16]

    lines = [
        BROAD_SUMMARY_MARKER,
        f"# Broad Smoke Failures ({len(all_actionable)} failing)",
        "",
        f"- **Failure Signature:** `{sig}`",
        f"- **New Failures:** {len(actionable_new)}",
        f"- **Persistent Failures:** {len(actionable_persistent)}",
        "",
    ]
    if actionable_new:
        lines.append("## New Failures")
        for f in actionable_new:
            lines.append(f"- **{f.get('site')}** (`{f.get('class', 'UNKNOWN')}`): {f.get('message', '')}")
        lines.append("")
    if actionable_persistent:
        lines.append("## Persistent Failures")
        for f in actionable_persistent:
            lines.append(f"- **{f.get('site')}** (`{f.get('class', 'UNKNOWN')}`): {f.get('message', '')}")
        lines.append("")

    title = f"[Site Monitor] Broad smoke failures ({len(all_actionable)} failing)"
    body = "\n".join(lines)
    labels = ["site-health", "site-health/persistent-failure"]

    if not existing or not is_open:
        return {
            "action": "CREATE_OR_REOPEN",
            "site": "broad-smoke",
            "title": title,
            "body": body,
            "labels": labels,
            "failure_signature": sig,
            "issue_number": existing.get("number") if existing else None,
        }

    existing_sig = extract_sig_from_body(existing.get("body", ""))
    if existing_sig != sig:
        return {
            "action": "UPDATE",
            "site": "broad-smoke",
            "title": title,
            "body": body,
            "labels": labels,
            "failure_signature": sig,
            "issue_number": existing.get("number"),
            "comment": f"Broad smoke failure list updated ({len(all_actionable)} failing, signature `{sig}`).",
        }

    return {
        "action": "NONE",
        "site": "broad-smoke",
        "issue_number": existing.get("number"),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate strict triage requests.")
    parser.add_argument("--latest", required=True, help="Path to strict_health_latest.json")
    parser.add_argument("--history", required=True, help="Path to strict_history.json")
    parser.add_argument("--out", required=True, help="Path to output triage_requests.json")
    parser.add_argument("--existing-issues", help="Path to existing issues JSON file from gh")
    parser.add_argument("--broad-diff", help="Optional path to site_health_diff_latest.json")
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
    if args.broad_diff and Path(args.broad_diff).exists():
        broad_diff = json.loads(Path(args.broad_diff).read_text(encoding="utf-8"))
        broad_req = generate_broad_summary_request(broad_diff, existing_issues)
        if broad_req:
            requests.append(broad_req)

    Path(args.out).write_text(json.dumps(requests, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
