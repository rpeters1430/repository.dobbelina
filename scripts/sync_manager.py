#!/usr/bin/env python3
"""
Sync Manager for Dobbelina Repository Fork.
Automates identifying, analyzing, and cherry-picking commits from upstream.
"""

import subprocess
import re
import sys
from pathlib import Path
import csv
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Configuration
UPSTREAM_REMOTE = "https://github.com/dobbelina/repository.dobbelina.git"
REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_FILE = REPO_ROOT / "UPSTREAM_SYNC.md"
AUDIT_FILE = REPO_ROOT / "bs4_migration_audit.csv"
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"


class SyncManager:
    def __init__(self):
        self.bs4_sites = self._load_bs4_sites()
        self.tracked_hashes = self._load_tracked_hashes()
        self.integrated_in_git = self._load_git_history_hashes()

    def _run_git(self, args):
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            encoding="utf-8",
            errors="replace",
        )
        return result

    def _load_bs4_sites(self):
        if not AUDIT_FILE.exists():
            return set()
        bs4_sites = set()
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("BeautifulSoup", "").strip().lower() == "true":
                    bs4_sites.add(row["Site"].strip().lower())
        return bs4_sites

    def _load_tracked_hashes(self):
        if not SYNC_FILE.exists():
            return set()
        content = SYNC_FILE.read_text(encoding="utf-8")
        # Find all 7-character hex strings in backticks
        hashes = set(re.findall(r"`([0-9a-f]{7,40})`", content))
        return hashes

    def _load_git_history_hashes(self):
        # Find hashes mentioned in "cherry picked from commit ..."
        result = self._run_git(["log", "--all", "--grep=cherry picked from commit"])
        hashes = set(
            re.findall(r"cherry picked from commit ([0-9a-f]{7,40})", result.stdout)
        )
        return hashes

    def ensure_upstream(self):
        result = self._run_git(["remote"])
        if "upstream" not in result.stdout.split():
            print(f"Adding upstream remote: {UPSTREAM_REMOTE}")
            self._run_git(["remote", "add", "upstream", UPSTREAM_REMOTE])

        print("Fetching upstream...")
        self._run_git(["fetch", "upstream", "--quiet"])

    def get_new_commits(self):
        # Get commits in upstream/master not in origin/master
        result = self._run_git(
            [
                "log",
                "upstream/master",
                "--not",
                "origin/master",
                "--oneline",
                "--no-merges",
            ]
        )
        commits = []
        if not result.stdout.strip():
            return []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            sha, msg = parts
            if "Bumped to v." in msg:
                continue
            commits.append({"sha": sha, "msg": msg})
        return commits

    def analyze_commit(self, sha):
        # Get files changed in this commit
        result = self._run_git(["show", "--name-only", "--format=", sha])
        files = result.stdout.strip().split("\n")

        sites_affected = set()
        for f in files:
            if "plugin.video.cumination/resources/lib/sites/" in f:
                site_name = Path(f).stem.lower()
                sites_affected.add(site_name)

        is_bs4_only = False
        if sites_affected:
            is_bs4_only = all(site in self.bs4_sites for site in sites_affected)

        return {
            "files": files,
            "sites": list(sites_affected),
            "is_bs4_only": is_bs4_only,
        }

    def update_sync_file(self, sha, msg, fork_sha=None, skip_reason=None):
        content = SYNC_FILE.read_text(encoding="utf-8")
        today = datetime.now().strftime("%Y-%m-%d")

        if skip_reason:
            # Add to "Intentionally Skipped" section
            entry = f"| `{sha}` | {msg} | {skip_reason} |\n"
            # Find the table header for skipped commits
            pattern = r"(### Intentionally Skipped.*?\n\|.*?\n\|.*?\n)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                content = content[: match.end()] + entry + content[match.end() :]
            else:
                content += (
                    f"\n### Intentionally Skipped\n\n| Upstream Hash | Message | Reason |\n|---|---|---|\n"
                    + entry
                )
        else:
            # Add to "Integrated" section
            entry = f"| `{sha}` | {msg} | `{fork_sha}` | {today} | Cherry-picked with -x |\n"

            section_header = f"### {today} Cherry-Pick Session"
            if section_header not in content:
                # Insert new section after "## Already Integrated Commits"
                insertion_point = content.find("## Already Integrated Commits")
                if insertion_point != -1:
                    insertion_point = content.find("\n", insertion_point) + 1
                    new_section = f"\n{section_header}\n\n| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |\n|---------------|---------|-----------|-----------------|-------|\n"
                    content = (
                        content[:insertion_point]
                        + new_section
                        + content[insertion_point:]
                    )

            section_idx = content.find(section_header)
            table_end = content.find("\n\n", section_idx)
            if table_end == -1:
                table_end = len(content)

            content = content[:table_end].rstrip() + "\n" + entry + content[table_end:]

        SYNC_FILE.write_text(content, encoding="utf-8")

    def run(self):
        self.ensure_upstream()
        new_commits = self.get_new_commits()

        pending = []
        for c in new_commits:
            sha = c["sha"]
            # Check tracking file (handle varying SHA lengths)
            if any(sha.startswith(h) or h.startswith(sha) for h in self.tracked_hashes):
                continue
            # Check git history
            if any(sha.startswith(h) or h.startswith(sha) for h in self.integrated_in_git):
                continue
            pending.append(c)

        if not pending:
            print("✅ Fork is up to date!")
            return

        print(f"📊 Found {len(pending)} new commits to analyze.")

        to_integrate = []
        to_skip = []

        for c in pending:
            analysis = self.analyze_commit(c["sha"])
            if analysis["is_bs4_only"]:
                print(
                    f"⏭️  Auto-skipping {c['sha']} (BS4 site: {', '.join(analysis['sites'])})"
                )
                to_skip.append(c)
            else:
                print(f"🆕 NEW: {c['sha']} - {c['msg']}")
                if analysis["sites"]:
                    print(f"   Affected sites: {', '.join(analysis['sites'])}")
                to_integrate.append(c)

        if to_skip:
            confirm = input(f"Auto-skip {len(to_skip)} BS4-related commits? (y/n): ")
            if confirm.lower() == "y":
                for c in to_skip:
                    self.update_sync_file(
                        c["sha"],
                        c["msg"],
                        skip_reason="Fork has BeautifulSoup migration",
                    )
                print(f"✅ Updated {SYNC_FILE} with skipped commits.")

        if not to_integrate:
            print("No new commits require integration.")
            return

        print(f"\nRemaining commits to integrate ({len(to_integrate)}):")
        for i, c in enumerate(to_integrate):
            print(f"{i + 1}. {c['sha']} - {c['msg']}")

        action = input(
            "\nSelect action: [number] to cherry-pick, 'all' to cherry-pick all, 'q' to quit: "
        )

        if action.lower() == "q":
            return

        targets = []
        if action.lower() == "all":
            targets = to_integrate
        elif action.isdigit() and 1 <= int(action) <= len(to_integrate):
            targets = [to_integrate[int(action) - 1]]

        for c in targets:
            sha = c["sha"]
            print(f"🍒 Cherry-picking {sha}...")
            result = self._run_git(["cherry-pick", "-x", sha])
            if result.returncode == 0:
                fork_sha = self._run_git(["log", "-1", "--format=%h"]).stdout.strip()
                self.update_sync_file(sha, c["msg"], fork_sha=fork_sha)
                print(f"✅ Successfully integrated {sha} as {fork_sha}")
            else:
                print(f"❌ Conflict while cherry-picking {sha}!")
                print(result.stderr)
                print(
                    "\nPlease resolve manually, commit, then update UPSTREAM_SYNC.md."
                )
                break


if __name__ == "__main__":
    manager = SyncManager()
    manager.run()
