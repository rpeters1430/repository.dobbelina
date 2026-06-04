#!/usr/bin/env python3
"""Ensure required GitHub labels exist in the repository."""

import argparse
import subprocess
import sys

LABELS = [
    ("site-health", "5319e7", "Automated site health issue"),
    ("site-health/new-failure", "b60205", "Site newly failed in health checks"),
    ("site-health/regression", "d93f0b", "Site health regressed from a healthier state"),
    ("site-health/step-regression", "fbca04", "One site health step regressed"),
    ("site-health/persistent-failure", "cfd3d7", "Failure persisted across health checks"),
    ("failure/network", "006b75", "Network or availability failure"),
    ("failure/parser", "c2e0c6", "Parser or listing extraction failure"),
    ("failure/playback", "f9d0c4", "Playback resolution failure"),
    ("status/needs-triage", "ededed", "Issue needs attention from a maintainer"),
]

def run_gh(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return result

def main():
    parser = argparse.ArgumentParser(description="Ensure GitHub labels")
    parser.add_argument("--repo", help="Target repository (owner/repo)")
    args = parser.parse_args()

    repo_args = ["--repo", args.repo] if args.repo else []

    print("Ensuring site health labels...")
    for name, color, description in LABELS:
        # Check if label exists
        check = run_gh(["label", "list", "--search", name, "--json", "name", "--jq", ".[0].name"] + repo_args)
        if check.stdout.strip() == name:
            print(f"  Label '{name}' already exists.")
            continue

        print(f"  Creating label '{name}'...")
        run_gh(["label", "create", name, "--color", color, "--description", description] + repo_args)

if __name__ == "__main__":
    main()
