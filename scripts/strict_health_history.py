#!/usr/bin/env python3
"""Strict health history aggregator and report renderer."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.site_health_types import HealthState

PRIORITY_SITES = [
    "anybunny",
    "ask4porn",
    "cam4",
    "camsoda",
    "chaturbate",
    "luxuretv",
    "missav",
    "porndig",
    "pornhub",
    "pornkai",
    "spankbang",
    "streamate",
    "thothub",
    "xnxx",
    "xvideos",
    "youporn",
    "yourlesbians",
]


def merge_reports(
    report_paths: list[Path],
    previous: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge individual site report JSON files and update 14-run history."""
    site_reports: dict[str, dict[str, Any]] = {}
    for path in report_paths:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                site_name = data.get("site")
                if site_name:
                    site_reports[site_name] = data
            except Exception:
                pass

    prev_sites = previous.get("sites", {}) if previous else {}

    summary = {
        HealthState.HEALTHY: 0,
        HealthState.BROKEN: 0,
        HealthState.BLOCKED: 0,
        HealthState.HARNESS_ERROR: 0,
        HealthState.NOT_TESTED: 0,
    }

    latest_sites: dict[str, Any] = {}
    updated_history_sites: dict[str, Any] = {}

    for site in PRIORITY_SITES:
        rep = site_reports.get(site)
        if not rep:
            rep = {
                "site": site,
                "state": HealthState.NOT_TESTED,
                "exit_code": 2,
                "classification": "NOT_TESTED",
                "message": "No strict test report generated",
                "failure_signature": "",
                "record": {},
            }

        state = rep.get("state", HealthState.NOT_TESTED)
        summary[state] = summary.get(state, 0) + 1
        latest_sites[site] = rep

        prev_hist = prev_sites.get(site, {})
        runs = list(prev_hist.get("runs", []))
        prev_consecutive = prev_hist.get("consecutive_healthy", 0)
        baseline = dict(prev_hist.get("healthy_baseline", {}))
        open_sig = prev_hist.get("open_failure_signature", "")

        new_run = {
            "state": state,
            "failed_stage": rep.get("failed_stage"),
            "classification": rep.get("classification"),
            "message": rep.get("message"),
            "failure_signature": rep.get("failure_signature", ""),
        }
        runs.append(new_run)
        runs = runs[-14:]

        if state == HealthState.HEALTHY:
            consecutive_healthy = prev_consecutive + 1
            healthy_baseline = rep.get("listing_metrics", {}) or baseline
            open_failure_signature = open_sig
        else:
            consecutive_healthy = 0
            healthy_baseline = baseline
            open_failure_signature = rep.get("failure_signature", "") or open_sig

        updated_history_sites[site] = {
            "consecutive_healthy": consecutive_healthy,
            "healthy_baseline": healthy_baseline,
            "open_failure_signature": open_failure_signature,
            "last_state": state,
            "runs": runs,
        }

    latest = {
        "summary": summary,
        "sites": latest_sites,
    }
    history = {
        "sites": updated_history_sites,
    }
    return latest, history


def render_strict_summary_markdown(latest: dict[str, Any], history: dict[str, Any]) -> str:
    """Render markdown summary of strict site monitoring results."""
    summary = latest.get("summary", {})
    sites = latest.get("sites", {})
    hist_sites = history.get("sites", {})

    lines = [
        "# Strict Priority Site Health Summary",
        "",
        f"- **Healthy:** {summary.get(HealthState.HEALTHY, 0)}",
        f"- **Broken:** {summary.get(HealthState.BROKEN, 0)}",
        f"- **Blocked:** {summary.get(HealthState.BLOCKED, 0)}",
        f"- **Harness Error:** {summary.get(HealthState.HARNESS_ERROR, 0)}",
        f"- **Not Tested:** {summary.get(HealthState.NOT_TESTED, 0)}",
        "",
        "| Priority Site | State | Stage | Classification | Consecutive Healthy | Signature |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]

    for site in PRIORITY_SITES:
        rep = sites.get(site, {})
        h_entry = hist_sites.get(site, {})
        raw_state = rep.get("state", HealthState.NOT_TESTED)
        state_str = str(raw_state.value if hasattr(raw_state, "value") else raw_state)
        stage = rep.get("failed_stage") or "-"
        classification = rep.get("classification") or "-"
        consec = h_entry.get("consecutive_healthy", 0)
        sig = rep.get("failure_signature") or h_entry.get("open_failure_signature") or "-"
        lines.append(f"| `{site}` | `{state_str}` | `{stage}` | `{classification}` | {consec} | `{sig}` |")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Merge strict site reports and update 14-run history.")
    parser.add_argument("reports", nargs="*", help="List of strict_site_<site>.json report paths")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--history-file", help="Path to existing strict_history.json file")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    previous_history = None
    if args.history_file and Path(args.history_file).exists():
        try:
            previous_history = json.loads(Path(args.history_file).read_text(encoding="utf-8"))
        except Exception:
            previous_history = None

    report_paths = []
    for p in args.reports:
        path_obj = Path(p)
        if "*" in p or "?" in p:
            parent = path_obj.parent if str(path_obj.parent) != "." else Path.cwd()
            report_paths.extend(parent.glob(path_obj.name))
        else:
            report_paths.append(path_obj)

    latest, history = merge_reports(report_paths, previous_history)

    latest_json_path = out_dir / "strict_health_latest.json"
    latest_md_path = out_dir / "strict_health_latest.md"
    history_json_path = out_dir / "strict_history.json"

    latest_json_path.write_text(json.dumps(latest, indent=2), encoding="utf-8")
    latest_md_path.write_text(render_strict_summary_markdown(latest, history), encoding="utf-8")
    history_json_path.write_text(json.dumps(history, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
