#!/usr/bin/env python3
"""Automate GitHub issue creation, updates, and closure based on triage requests."""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running gh {' '.join(args)}: {result.stderr}")
    return result


def execute_triage_requests(requests: list[dict[str, Any]], repo: str | None = None) -> list[str]:
    """Execute gh CLI issue operations for generated triage requests."""
    repo_args = ["--repo", repo] if repo else []
    executed_summary = []

    for req in requests:
        action = req.get("action", "NONE")
        site = req.get("site", "unknown")
        issue_number = str(req.get("issue_number", "") or "").strip()

        if action == "NONE":
            executed_summary.append(f"{site}: NONE")
            continue

        title = req.get("title", f"[Site Monitor] {site} issue")
        body = req.get("body", "")
        labels = ",".join(req.get("labels", ["site-monitor"]))
        comment = req.get("comment", "")

        if action == "CREATE_OR_REOPEN":
            if issue_number:
                print(f"Reopening existing issue #{issue_number} for {site}...")
                run_gh(["issue", "reopen", issue_number] + repo_args)
                if body:
                    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as f:
                        f.write(body)
                        temp_body_path = f.name
                    run_gh(["issue", "edit", issue_number, "--body-file", temp_body_path, "--add-label", labels] + repo_args)
                    Path(temp_body_path).unlink(missing_ok=True)
                executed_summary.append(f"{site}: REOPEN #{issue_number}")
            else:
                print(f"Creating new issue for {site}...")
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as f:
                    f.write(body)
                    temp_body_path = f.name
                create_res = run_gh(["issue", "create", "--title", title, "--body-file", temp_body_path, "--label", labels] + repo_args)
                Path(temp_body_path).unlink(missing_ok=True)
                executed_summary.append(f"{site}: CREATE")

        elif action == "UPDATE":
            if issue_number:
                print(f"Updating issue #{issue_number} for {site}...")
                if body:
                    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as f:
                        f.write(body)
                        temp_body_path = f.name
                    run_gh(["issue", "edit", issue_number, "--body-file", temp_body_path, "--add-label", labels] + repo_args)
                    Path(temp_body_path).unlink(missing_ok=True)
                if comment:
                    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as f:
                        f.write(comment)
                        temp_comment_path = f.name
                    run_gh(["issue", "comment", issue_number, "--body-file", temp_comment_path] + repo_args)
                    Path(temp_comment_path).unlink(missing_ok=True)
                executed_summary.append(f"{site}: UPDATE #{issue_number}")

        elif action == "CLOSE":
            if issue_number:
                print(f"Closing issue #{issue_number} for {site} after recovery...")
                if comment:
                    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as f:
                        f.write(comment)
                        temp_comment_path = f.name
                    run_gh(["issue", "comment", issue_number, "--body-file", temp_comment_path] + repo_args)
                    Path(temp_comment_path).unlink(missing_ok=True)
                run_gh(["issue", "close", issue_number] + repo_args)
                executed_summary.append(f"{site}: CLOSE #{issue_number}")

    return executed_summary


def main():
    parser = argparse.ArgumentParser(description="Automate GitHub issue triage")
    parser.add_argument("--requests", required=True, help="Path to triage_requests.json")
    parser.add_argument("--repo", help="Target repository (owner/repo)")
    args = parser.parse_args()

    requests_path = Path(args.requests)
    if not requests_path.exists():
        print("No triage requests found.")
        return 0

    requests = json.loads(requests_path.read_text(encoding="utf-8"))
    if not requests:
        print("No requests to triage.")
        return 0

    execute_triage_requests(requests, args.repo)


if __name__ == "__main__":
    main()
