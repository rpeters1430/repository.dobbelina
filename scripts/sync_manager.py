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
SYNC_FILE = REPO_ROOT / "docs" / "development" / "UPSTREAM_SYNC.md"
TRIAGE_FILE = REPO_ROOT / "docs" / "development" / "UPSTREAM_TRIAGE.md"
AUDIT_FILE = REPO_ROOT / "docs" / "status" / "bs4_migration_audit.csv"
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"


class SyncManager:
    def __init__(self, dry_run=False, skip_changelog=True):
        self.dry_run = dry_run
        self.skip_changelog = skip_changelog
        self.bs4_sites = self._load_bs4_sites()
        self.existing_sites = self._load_existing_sites()
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
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("BeautifulSoup", "").strip().lower() == "true":
                        bs4_sites.add(row["Site"].strip().lower())
        except Exception as e:
            print(f"Warning: Could not load audit file: {e}")
        return bs4_sites

    def _load_existing_sites(self):
        if not SITES_DIR.exists():
            return set()
        return {
            p.stem.lower() for p in SITES_DIR.glob("*.py") if p.stem != "__init__"
        }

    def _load_tracked_hashes(self):
        if not SYNC_FILE.exists():
            print(f"Warning: {SYNC_FILE} not found")
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
        if not result.stdout or not result.stdout.strip():
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
        # Get files changed in this commit, with their status (A/M/D/R...)
        result = self._run_git(["show", "--name-status", "--format=", sha])
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]

        # Get full commit message for deeper analysis
        msg_full = self._run_git(["show", "-s", "--format=%B", sha]).stdout.lower()

        files = []
        sites_affected = set()
        added_sites = set()
        changelog_affected = False
        for line in lines:
            parts = line.split("\t")
            status = parts[0]
            f = parts[-1]
            files.append(f)
            if "plugin.video.cumination/resources/lib/sites/" in f:
                site_name = Path(f).stem.lower()
                sites_affected.add(site_name)
                if status.startswith("A"):
                    added_sites.add(site_name)
            if "changelog.txt" in f.lower():
                changelog_affected = True

        # Keep this list specific - generic terms like "play"/"vid"/"stream"
        # match almost any site module (e.g. the `Playvid` function name).
        playback_keywords = ["playback", "decrypt", "kvs", "m3u8", "hls", "drm"]
        playback_affected = any(kw in msg_full for kw in playback_keywords)

        is_bs4_only = False
        if sites_affected:
            is_bs4_only = all(site in self.bs4_sites for site in sites_affected)

        # Sites newly added in this commit that we don't have at all.
        new_sites = added_sites - self.existing_sites

        return {
            "files": files,
            "sites": list(sites_affected),
            "new_sites": list(new_sites),
            "is_bs4_only": is_bs4_only,
            "changelog_affected": changelog_affected,
            "playback_affected": playback_affected,
        }

    def get_pending_commits(self):
        new_commits = self.get_new_commits()
        pending = []
        for c in new_commits:
            sha = c["sha"]
            if any(sha.startswith(h) or h.startswith(sha) for h in self.tracked_hashes):
                continue
            if any(
                sha.startswith(h) or h.startswith(sha) for h in self.integrated_in_git
            ):
                continue
            pending.append(c)
        return pending

    @staticmethod
    def _extract_issue(msg):
        m = re.search(r"#(\d+)", msg)
        return m.group(1) if m else None

    def group_commits(self, pending):
        """Group commits by referenced issue number so duplicate/iterative
        commits for the same PR collapse into one triage item."""
        groups = {}
        order = []
        for c in pending:
            issue = self._extract_issue(c["msg"])
            key = f"#{issue}" if issue else c["sha"]
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(c)
        return [(key, groups[key]) for key in order]

    def categorize_group(self, commits):
        all_sites = set()
        new_sites = set()
        playback_affected = False
        changelog_affected = False
        for c in commits:
            a = self.analyze_commit(c["sha"])
            all_sites.update(a["sites"])
            new_sites.update(a["new_sites"])
            playback_affected = playback_affected or a["playback_affected"]
            changelog_affected = changelog_affected or a["changelog_affected"]

        sites_we_have = all_sites & self.existing_sites

        if not all_sites:
            category = "auto_skip"
        elif new_sites:
            # A site file we don't have was added in this commit.
            category = "new_site"
        elif sites_we_have:
            non_bs4 = sites_we_have - self.bs4_sites
            if non_bs4 or playback_affected:
                category = "needs_review"
            else:
                category = "covered"
        else:
            # Touches only sites we don't have, with nothing newly added
            # (e.g. upstream removed/renamed a site we never carried).
            category = "auto_skip"

        return category, all_sites, new_sites, playback_affected, changelog_affected

    def generate_report(self):
        self.ensure_upstream()
        pending = self.get_pending_commits()

        if not pending:
            print("✅ Fork is up to date! No report generated.")
            return

        groups = self.group_commits(pending)

        categories = {
            "new_site": [],
            "needs_review": [],
            "covered": [],
            "auto_skip": [],
        }

        for key, commits in groups:
            category, all_sites, new_sites, playback, changelog = self.categorize_group(commits)
            categories[category].append((key, commits, all_sites, new_sites, playback, changelog))

        section_titles = {
            "new_site": (
                "New Sites Available",
                "Sites touched by these commits don't exist in our fork yet. Candidates for new site modules.",
            ),
            "needs_review": (
                "Needs Review",
                "Touches a site we have that isn't BeautifulSoup-migrated, or mentions playback/decrypt - worth reviewing for porting.",
            ),
            "covered": (
                "Likely Already Covered",
                "Only touches BeautifulSoup-migrated sites we already have - spot-check, likely skip.",
            ),
            "auto_skip": (
                "Auto-Skip",
                "No site module changes detected (changelog/icon/docs/version-bump-style commits).",
            ),
        }

        lines = []
        lines.append("# Upstream Triage Report")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"Pending commits: {len(pending)} (grouped into {len(groups)} items)")
        lines.append("")
        lines.append(
            "Run `python scripts/sync_manager.py` (interactive) to review/cherry-pick, "
            "or `python scripts/sync_manager.py --report` to regenerate this file."
        )
        lines.append("")

        for cat_key in ["new_site", "needs_review", "covered", "auto_skip"]:
            title, desc = section_titles[cat_key]
            items = categories[cat_key]
            lines.append(f"## {title} ({len(items)})")
            lines.append("")
            lines.append(desc)
            lines.append("")
            if not items:
                lines.append("_None._")
                lines.append("")
                continue
            lines.append("| Group | Commits | Sites | New Sites | Playback | Message(s) |")
            lines.append("|---|---|---|---|---|---|")
            for key, commits, all_sites, new_sites, playback, changelog in items:
                shas = ", ".join(f"`{c['sha']}`" for c in commits)
                sites_str = ", ".join(sorted(all_sites)) or "-"
                new_sites_str = ", ".join(sorted(new_sites)) or "-"
                msgs = "<br>".join(c["msg"].replace("|", "\\|") for c in commits)
                lines.append(
                    f"| {key} | {shas} | {sites_str} | {new_sites_str} | {'yes' if playback else ''} | {msgs} |"
                )
            lines.append("")

        TRIAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        TRIAGE_FILE.write_text("\n".join(lines), encoding="utf-8")
        print(f"📝 Wrote triage report to {TRIAGE_FILE} ({len(groups)} groups from {len(pending)} commits)")

    def preview_commit(self, sha):
        print(f"\n--- PREVIEW: {sha} ---")
        result = self._run_git(["show", "--stat", sha])
        print(result.stdout)
        print("--------------------------\n")

    def update_sync_file(self, sha, msg, fork_sha=None, skip_reason=None):
        if self.dry_run:
            print(f"[DRY RUN] Would update {SYNC_FILE} for {sha}")
            return

        if not SYNC_FILE.exists():
            print(f"Error: {SYNC_FILE} not found. Cannot update tracking.")
            return

        content = SYNC_FILE.read_text(encoding="utf-8")
        today = datetime.now().strftime("%Y-%m-%d")

        if skip_reason:
            # Add to "Intentionally Skipped" section
            entry = f"| `{sha}` | {msg} | {skip_reason} |\n"
            section_header = "### Intentionally Skipped"
            if section_header not in content:
                content += (
                    f"\n{section_header}\n\n| Upstream Hash | Message | Reason |\n|---|---|---|\n"
                    + entry
                )
            else:
                section_idx = content.find(section_header)
                table_end = content.find("\n\n", section_idx)
                if table_end == -1:
                    table_end = len(content)
                content = content[:table_end].rstrip() + "\n" + entry + content[table_end:]
        else:
            # Add to today's "Cherry-Pick Session" section
            entry = f"| `{sha}` | {msg} | `{fork_sha}` | {today} | Cherry-picked with -x |\n"

            section_header = f"### {today} Cherry-Pick Session"
            if section_header not in content:
                # Insert new section right after "## Sync Sessions"
                insertion_point = content.find("## Sync Sessions")
                if insertion_point != -1:
                    insertion_point = content.find("\n", insertion_point) + 1
                else:
                    insertion_point = len(content)
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
        pending = self.get_pending_commits()

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
                msg_extra = ""
                if analysis["changelog_affected"]:
                    msg_extra = " [CHANGELOG]"
                print(f"🆕 NEW: {c['sha']} - {c['msg']}{msg_extra}")
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
            analysis = self.analyze_commit(sha)
            
            if self.dry_run:
                print(f"[DRY RUN] Would cherry-pick {sha}")
                continue

            print(f"🍒 Cherry-picking {sha}...")
            
            # If changelog is affected and we want to skip it, use a cleaner approach
            if analysis["changelog_affected"] and self.skip_changelog:
                print(f"   Note: This commit contains changelog changes. Attempting to exclude them...")
                # Cherry-pick without committing
                self._run_git(["cherry-pick", "-n", "-x", sha])
                
                # Revert any changelog files
                for f in analysis["files"]:
                    if "changelog.txt" in f:
                        self._run_git(["checkout", "HEAD", "--", f])
                
                # Try to commit
                result = self._run_git(["commit", "-m", f"cherry picked from commit {sha} (excluded changelog)"])
                if result.returncode != 0:
                    # If commit failed (maybe only changelog was changed?), check if anything is staged
                    status = self._run_git(["status", "--porcelain"])
                    if not status.stdout.strip():
                        print(f"⚠️  Skipping {sha} because it only contained changelog changes after filtering.")
                        # Still track it as integrated to avoid re-prompting
                        self.update_sync_file(sha, c["msg"], fork_sha="skipped-changelog-only")
                        continue
                    else:
                        print(f"❌ Failed to commit after excluding changelog for {sha}")
                        print(result.stderr)
                        break
            else:
                # Normal cherry-pick
                result = self._run_git(["cherry-pick", "-x", sha])
                if result.returncode != 0:
                    print(f"❌ Conflict while cherry-picking {sha}!")
                    print(result.stderr)
                    print("\nPlease resolve manually, commit, then update UPSTREAM_SYNC.md.")
                    break

            fork_sha = self._run_git(["log", "-1", "--format=%h"]).stdout.strip()
            self.update_sync_file(sha, c["msg"], fork_sha=fork_sha)
            print(f"✅ Successfully integrated {sha} as {fork_sha}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sync Manager for Dobbelina Repository Fork")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--no-skip-changelog", action="store_true", help="Don't skip changelog files during cherry-picking")
    parser.add_argument("--report", action="store_true", help="Generate docs/development/UPSTREAM_TRIAGE.md instead of running interactively")

    args = parser.parse_args()

    manager = SyncManager(dry_run=args.dry_run, skip_changelog=not args.no_skip_changelog)
    if args.report:
        manager.generate_report()
    else:
        manager.run()
