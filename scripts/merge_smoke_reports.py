#!/usr/bin/env python3
"""Merge multiple live smoke reports into one."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

def merge_reports(report_paths: list[Path]) -> dict[str, Any]:
    if not report_paths:
        raise ValueError("No reports to merge")

    merged_sites = {}
    total_sites = []
    
    first_report = json.loads(report_paths[0].read_text(encoding="utf-8"))
    summary = {
        "generated": datetime.now().isoformat(),
        "started": first_report["summary"]["started"],
        "sites_total": 0,
        "pass": 0,
        "warn": 0,
        "fail": 0,
        "error": 0,
        "skip": 0,
        "blocked_hint": 0,
        "steps": first_report["summary"]["steps"],
        "timeout_per_step_sec": first_report["summary"]["timeout_per_step_sec"],
        "timeout_per_site_sec": first_report["summary"]["timeout_per_site_sec"],
        "keyword": first_report["summary"]["keyword"],
    }

    for path in report_paths:
        report = json.loads(path.read_text(encoding="utf-8"))
        for site in report.get("sites", []):
            site_name = site["site"]
            # If a site appears in multiple reports, the last one wins (or we could be smarter)
            if site_name not in merged_sites:
                merged_sites[site_name] = site
                total_sites.append(site)
                
                # Update summary counts
                overall = site.get("overall", "ERROR")
                if overall == "PASS": summary["pass"] += 1
                elif overall == "WARN": summary["warn"] += 1
                elif overall == "FAIL": summary["fail"] += 1
                elif overall == "ERROR": summary["error"] += 1
                elif overall == "SKIP": summary["skip"] += 1
                
                # Coarse blocked hint check
                msgs = [site.get("error", "")]
                for step_data in site.get("steps", {}).values():
                    msgs.append(step_data.get("message", ""))
                from live_smoke_test import classify_message
                if any(classify_message(m) == "BLOCKED" for m in msgs):
                    summary["blocked_hint"] += 1

    summary["sites_total"] = len(total_sites)
    
    return {
        "summary": summary,
        "sites": total_sites
    }

def main():
    parser = argparse.ArgumentParser(description="Merge live smoke reports")
    parser.add_argument("reports", nargs="+", help="Path to JSON reports")
    parser.add_argument("--out", required=True, help="Output path")
    args = parser.parse_args()

    # We need to be able to import classify_message from live_smoke_test
    sys.path.append(str(Path(__file__).resolve().parent))
    
    report_paths = [Path(p) for p in args.reports]
    merged = merge_reports(report_paths)
    
    from live_smoke_test import render_markdown
    
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    
    md_path = out_path.with_suffix(".md")
    md_path.write_text(render_markdown(merged), encoding="utf-8")
    
    print(f"Merged {len(report_paths)} reports into {out_path}")

if __name__ == "__main__":
    main()
