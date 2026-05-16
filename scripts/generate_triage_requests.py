#!/usr/bin/env python3
"""Generate triage requests for Gemini based on site health regressions."""

import argparse
import json
import sys
from pathlib import Path


SKIP_CLASSES = {"ENV"}
BASE_LABELS = ["status/needs-triage", "bug", "site-health"]
CLASS_LABELS = {
    "NETWORK": "failure/network",
    "PARSER": "failure/parser",
    "PLAYBACK": "failure/playback",
}
CLASS_FIX_HINTS = {
    "NETWORK": [
        "Rerun the live smoke for the single site to confirm the HTTP status is stable and not a temporary block.",
        "Check whether the base/list URL changed, now redirects, or requires Cloudflare/FlareSolverr handling.",
        "If the site is intermittently unavailable, update the site health profile instead of changing parser code.",
    ],
    "PARSER": [
        "Fetch the failing list/search page HTML and compare selectors against the current site markup.",
        "Update the site module's listing selectors and add a focused fixture test for the new structure.",
        "Confirm the scraper still adds playable video items, thumbnails, and descriptions in the live smoke harness.",
    ],
    "PLAYBACK": [
        "Reproduce the failing video page and inspect whether the hoster, player config, or source JSON changed.",
        "Update the playback extraction path or resolver integration, then add a focused playback fixture test.",
        "Verify the resolved URL includes required headers such as User-Agent, Referer, and Origin when needed.",
    ],
}


def labels_for(item: dict, request_type: str) -> list[str]:
    labels = list(BASE_LABELS)
    if request_type == "REGRESSION":
        labels.extend(["site-health/regression", "site-health/new-failure"])
    elif request_type == "STEP_REGRESSION":
        labels.append("site-health/step-regression")
    elif request_type == "PERSISTENT_FAILURE":
        labels.append("site-health/persistent-failure")

    class_label = CLASS_LABELS.get(item.get("class"))
    if class_label:
        labels.append(class_label)
    return labels


def comment_for(item: dict, request_type: str) -> str:
    site = item["site"]
    failure_class = item.get("class", "UNKNOWN")
    message = item.get("message", "")
    marker = f"<!-- site-health-triage:{site}:{request_type}:{failure_class} -->"
    hints = CLASS_FIX_HINTS.get(
        failure_class,
        [
            "Rerun the single-site live smoke test to confirm the failure is still current.",
            "Inspect the failing step in the site module and add or update a focused regression test.",
        ],
    )
    step = item.get("step")
    step_line = f"- Failing step: `{step}`\n" if step else ""
    hint_lines = "\n".join(f"- {hint}" for hint in hints)
    return (
        f"{marker}\n"
        "Automated site-health triage notes:\n\n"
        f"- Classification: `{request_type}` / `{failure_class}`\n"
        f"{step_line}"
        f"- Reported message: `{message}`\n"
        f"- Reproduce locally: `.venv\\Scripts\\python.exe scripts\\live_smoke_test.py --site {site} --steps main,list,categories,search,play --keyword test --timeout 45 --site-timeout 220`\n\n"
        "Possible fix path:\n"
        f"{hint_lines}\n\n"
        "If the reproduce command now passes, close this as stale or note the transient condition in the issue."
    )


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
                "labels": labels_for(failure, "REGRESSION"),
                "comment": comment_for(failure, "REGRESSION"),
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
                "labels": labels_for(reg, "STEP_REGRESSION"),
                "comment": comment_for(reg, "STEP_REGRESSION"),
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
                "labels": labels_for(failure, "PERSISTENT_FAILURE"),
                "comment": comment_for(failure, "PERSISTENT_FAILURE"),
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
