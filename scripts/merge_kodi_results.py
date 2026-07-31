#!/usr/bin/env python3
"""Merge Kodi runtime probe results into strict site monitoring reports."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.site_health_types import HealthState, failure_signature


def merge_kodi_result(
    strict_report: dict[str, Any],
    kodi_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge a Kodi runtime probe result into a strict site evaluation report."""
    report = dict(strict_report)
    if not kodi_result:
        return report

    report["kodi_probe"] = kodi_result

    if kodi_result.get("infrastructure_error"):
        report["state"] = HealthState.HARNESS_ERROR
        report["exit_code"] = 2
        report["failed_stage"] = "kodi_harness"
        report["classification"] = "KODI_INFRASTRUCTURE_ERROR"
        report["message"] = kodi_result.get("error", "Kodi infrastructure error")
        report["failure_signature"] = failure_signature({
            "state": HealthState.HARNESS_ERROR,
            "failed_stage": "kodi_harness",
            "classification": "KODI_INFRASTRUCTURE_ERROR",
            "message": report["message"],
        })
        return report

    current_state = report.get("state", HealthState.NOT_TESTED)

    # Kodi mismatch overrides HEALTHY state only
    if current_state == HealthState.HEALTHY and not kodi_result.get("passed"):
        report["state"] = HealthState.BROKEN
        report["exit_code"] = 1
        report["failed_stage"] = "kodi_runtime"
        report["classification"] = "KODI_RUNTIME_MISMATCH"
        report["message"] = f"Kodi runtime mismatch: {kodi_result.get('message', 'Playback failed')}"
        report["failure_signature"] = failure_signature({
            "state": HealthState.BROKEN,
            "failed_stage": "kodi_runtime",
            "classification": "KODI_RUNTIME_MISMATCH",
            "message": report["message"],
        })

    return report


def main():
    parser = argparse.ArgumentParser(description="Merge Kodi probe result into strict site report.")
    parser.add_argument("--strict-report", required=True, help="Path to strict_site_<site>.json")
    parser.add_argument("--kodi-report", required=True, help="Path to kodi_probe_<site>.json")
    parser.add_argument("--out", required=True, help="Output path for updated report")
    args = parser.parse_args()

    strict_data = json.loads(Path(args.strict_report).read_text(encoding="utf-8"))
    kodi_data = None
    if Path(args.kodi_report).exists():
        try:
            kodi_data = json.loads(Path(args.kodi_report).read_text(encoding="utf-8"))
        except Exception:
            kodi_data = None

    merged = merge_kodi_result(strict_data, kodi_data)
    Path(args.out).write_text(json.dumps(merged, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
