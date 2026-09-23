#!/usr/bin/env python3
"""Report live site states and fail only for repeated, matching strict regressions."""

import json
import os
import sys
from pathlib import Path


def confirmed_regressions(history):
    failures = []
    for site, data in history.get("sites", {}).items():
        recent = data.get("runs", [])[-2:]
        if (len(recent) == 2 and all(run.get("state") == "BROKEN" for run in recent)
                and recent[0].get("failure_signature")
                and recent[0]["failure_signature"] == recent[1].get("failure_signature")):
            failures.append(site)
    return sorted(failures)


def main(history_path, broad_path):
    history = json.loads(Path(history_path).read_text(encoding="utf-8"))
    broad = json.loads(Path(broad_path).read_text(encoding="utf-8"))
    failures = confirmed_regressions(history)
    strict_states = {site: data.get("last_state", "NOT_TESTED")
                     for site, data in history.get("sites", {}).items()}
    lines = ["## Live site status", "",
             "Strict: " + ", ".join(f"{state}={list(strict_states.values()).count(state)}"
                                    for state in ("HEALTHY", "BROKEN", "BLOCKED", "HARNESS_ERROR", "NOT_TESTED")),
             "Broad: " + ", ".join(f"{state}={broad.get('summary', {}).get(state.lower(), 0)}"
                                   for state in ("PASS", "WARN", "FAIL", "ERROR", "SKIP")),
             "Confirmed regressions (same failure twice): " + (", ".join(failures) or "none")]
    summary = "\n".join(lines) + "\n"
    print(summary)
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write(summary)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
