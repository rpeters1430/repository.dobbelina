#!/usr/bin/env python3
"""Generate triage requests for Gemini based on site health regressions."""

import argparse
import json
import sys
from pathlib import Path


SKIP_CLASSES = {"ENV"}


def is_environment_failure(item: dict) -> bool:
    message = (item.get("message") or "").lower()
    return item.get("class") in SKIP_CLASSES or (
        "flaresolverr" in message
        and any(
            token in message
            for token in (
                "not available",
                "unavailable",
                "check if flaresolverr is running",
                "failed to connect",
                "connection refused",
                "no connection could be made",
            )
        )
    )


def should_skip(item: dict) -> bool:
    if item.get("is_flaky"):
        print(
            f"Skipping flaky failure for {item['site']} "
            f"(stability: {item.get('stability_score', 0):.1%})"
        )
        return True
    if is_environment_failure(item):
        print(
            f"Skipping environment failure for {item['site']}: "
            f"{item.get('message', '')}"
        )
        return True
    return False


def build_requests(diff: dict) -> list[dict]:
    requests = []

    # Identify genuine, stable regressions
    for failure in diff.get("new_failures", []):
        if should_skip(failure):
            continue

        requests.append(
            {
                "site": failure["site"],
                "type": "REGRESSION",
                "priority": "HIGH" if failure["previous"] == "PASS" else "MEDIUM",
                "previous": failure["previous"],
                "current": failure["current"],
                "class": failure["class"],
                "message": failure["message"],
                "description": f"Site {failure['site']} regressed from {failure['previous']} to {failure['current']}.\nError class: {failure['class']}\nMessage: {failure['message']}",
            }
        )

    # Identify step regressions (e.g., search broke but site is still overall PASS/WARN)
    for reg in diff.get("step_regressions", []):
        if should_skip(reg):
            continue

        requests.append(
            {
                "site": reg["site"],
                "type": "STEP_REGRESSION",
                "priority": "LOW",
                "step": reg["step"],
                "previous": reg["previous"],
                "current": reg["current"],
                "class": reg["class"],
                "message": reg["message"],
                "description": f"Site {reg['site']} experienced a regression in the '{reg['step']}' step ({reg['previous']} -> {reg['current']}).\nError class: {reg['class']}\nMessage: {reg['message']}",
            }
        )

    # Identify persistent failures
    for failure in diff.get("persistent_failures", []):
        if should_skip(failure):
            continue

        requests.append(
            {
                "site": failure["site"],
                "type": "PERSISTENT_FAILURE",
                "priority": "MEDIUM",
                "previous": failure["previous"],
                "current": failure["current"],
                "class": failure["class"],
                "message": failure["message"],
                "description": f"Site {failure['site']} is a persistent failure ({failure['previous']} -> {failure['current']}).\nError class: {failure['class']}\nMessage: {failure['message']}",
            }
        )

    return requests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--diff",
        required=True,
        help="Path to the site_health_diff_latest.json file",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to save the triage requests JSON",
    )
    args = parser.parse_args()

    diff_path = Path(args.diff)
    if not diff_path.exists():
        print(f"Error: Diff file not found: {diff_path}")
        return 1

    diff = json.loads(diff_path.read_text(encoding="utf-8"))
    requests = build_requests(diff)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(requests, indent=2), encoding="utf-8")

    print(f"Generated {len(requests)} triage requests to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
