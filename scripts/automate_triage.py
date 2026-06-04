#!/usr/bin/env python3
"""Automate GitHub issue creation and updates based on triage requests."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def run_gh(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running gh {' '.join(args)}: {result.stderr}")
    return result

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
        print("No regressions to triage.")
        return 0

    repo_args = ["--repo", args.repo] if args.repo else []

    print(f"Triaging {len(requests)} regressions...")
    for req in requests:
        site = req["site"]
        req_type = req["type"]
        
        if req_type == "REGRESSION":
            title = f"[Site Health] Regression: {site}"
        elif req_type == "STEP_REGRESSION":
            title = f"[Site Health] Step Regression: {site}"
        else:
            title = f"[Site Health] Persistent Failure: {site}"
            
        body = req["description"]
        labels = ",".join(req.get("labels", ["status/needs-triage", "bug"]))
        comment = req.get("comment", "")
        comment_marker = comment.split("\n")[0].strip() if comment else ""
        
        # Check if an open issue already exists
        search_result = run_gh(["issue", "list", "--state", "open", "--search", title, "--json", "number", "--jq", ".[0].number"] + repo_args)
        existing_number = search_result.stdout.strip()
        
        if existing_number:
            print(f"Issue #{existing_number} already exists for {site}, updating labels/comment if needed.")
            run_gh(["issue", "edit", existing_number, "--add-label", labels] + repo_args)
            if comment:
                # Check for existing comment with marker
                comment_search = run_gh(["issue", "view", existing_number, "--json", "comments", "--jq", f'[.comments[].body | contains("{comment_marker}")] | any'] + repo_args)
                if comment_search.stdout.strip() != "true":
                    with open("temp_comment.md", "w", encoding="utf-8") as f:
                        f.write(comment)
                    run_gh(["issue", "comment", existing_number, "--body-file", "temp_comment.md"] + repo_args)
            continue
            
        print(f"Creating issue for {site}...")
        create_result = run_gh(["issue", "create", "--title", title, "--body", body, "--label", labels] + repo_args)
        if create_result.returncode == 0:
            issue_url = create_result.stdout.strip()
            issue_number = issue_url.split("/")[-1]
            if comment:
                with open("temp_comment.md", "w", encoding="utf-8") as f:
                    f.write(comment)
                run_gh(["issue", "comment", issue_number, "--body-file", "temp_comment.md"] + repo_args)

    if os.path.exists("temp_comment.md"):
        os.remove("temp_comment.md")

if __name__ == "__main__":
    main()
