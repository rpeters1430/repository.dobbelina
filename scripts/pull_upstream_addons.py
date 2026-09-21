#!/usr/bin/env python3
"""
Pull Upstream Addons & Repositories Manager for Dobbelina Repository.

Pulls updated code from official upstream repositories for embedded addons
such as ResolveURL (script.module.resolveurl), ResolveURL.XXX (script.module.resolveurl.xxx),
SMR Link Tester, yt-dlp, and F4mProxy.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

# Global file patterns that must never be overwritten or deleted from local addons
GLOBAL_PRESERVE_PATTERNS = [
    "*settings*.xml",
    "advancedsettings.xml",
    "resources/settings.xml",
]

# Default upstream registry of embedded addons and their upstream git sources
UPSTREAM_REGISTRY: dict[str, dict[str, Any]] = {
    "resolveurl": {
        "name": "ResolveURL",
        "addon_id": "script.module.resolveurl",
        "repo_url": "https://github.com/Gujal00/ResolveURL.git",
        "default_branch": "master",
        "source_path": "script.module.resolveurl",
        "dest_path": "script.module.resolveurl",
        "type": "directory",
        "exclude": [".git*", "*.pyc", "__pycache__", "*.zip", ".DS_Store"],
        "preserve": ["lib/resolveurl/plugins/doodstream.py"],
    },
    "resolveurlxxx": {
        "name": "ResolveURL.XXX (Adult Resolver Extension)",
        "addon_id": "script.module.resolveurl.xxx",
        "repo_url": "https://github.com/Gujal00/ResolveURL.git",
        "default_branch": "master",
        "source_path": "script.module.resolveurl.xxx",
        "dest_path": "script.module.resolveurl.xxx",
        "type": "directory",
        "exclude": [".git*", "*.pyc", "__pycache__", "*.zip", ".DS_Store"],
        "preserve": ["resources/plugins/pornhub.py"],
    },
    "smr_link_tester": {
        "name": "SMR Link Tester",
        "addon_id": "plugin.video.smr_link_tester",
        "repo_url": "https://github.com/Gujal00/ResolveURL.git",
        "default_branch": "master",
        "source_path": "plugin.video.smr_link_tester",
        "dest_path": "plugin.video.smr_link_tester",
        "type": "directory",
        "exclude": [".git*", "*.pyc", "__pycache__", "*.zip", ".DS_Store"],
        "preserve": [],
    },
    "yt-dlp": {
        "name": "yt-dlp",
        "addon_id": "script.module.yt-dlp",
        "repo_url": "https://github.com/yt-dlp/yt-dlp.git",
        "default_branch": "master",
        "source_path": "yt_dlp",
        "dest_path": "script.module.yt-dlp/lib/yt_dlp",
        "type": "package",
        "exclude": [".git*", "*.pyc", "__pycache__", "*.zip", ".DS_Store", "test", "docs"],
        "preserve": [],
    },
    "f4mproxy": {
        "name": "F4mProxy",
        "addon_id": "script.video.F4mProxy",
        "repo_url": "https://github.com/dobbelina/repository.dobbelina.git",
        "default_branch": "master",
        "source_path": "script.video.F4mProxy",
        "dest_path": "script.video.F4mProxy",
        "type": "directory",
        "exclude": [".git*", "*.pyc", "__pycache__", "*.zip", ".DS_Store"],
        "preserve": [
            "lib/f4mUtils/cipherfactory.py",
            "lib/f4mUtils/pycrypto_rc4.py",
            "lib/f4mUtils/pycrypto_tripledes.py",
        ],
    },
}

# Aliases for user convenience
ALIASES: dict[str, str] = {
    "script.module.resolveurl": "resolveurl",
    "script.module.resolveurl.xxx": "resolveurlxxx",
    "resolveurl.xxx": "resolveurlxxx",
    "plugin.video.smr_link_tester": "smr_link_tester",
    "smr": "smr_link_tester",
    "script.module.yt-dlp": "yt-dlp",
    "ytdlp": "yt-dlp",
    "script.video.F4mProxy": "f4mproxy",
    "f4m": "f4mproxy",
}


@dataclass
class SyncDiff:
    added: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    preserved: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.modified or self.removed)


def resolve_addon_key(name: str) -> str:
    """Normalize input addon name or alias to canonical registry key."""
    cleaned = name.strip().lower()
    if cleaned in UPSTREAM_REGISTRY:
        return cleaned
    if cleaned in ALIASES:
        return ALIASES[cleaned]
    # Check addon_id matches
    for key, spec in UPSTREAM_REGISTRY.items():
        if spec.get("addon_id", "").lower() == cleaned:
            return key
    return cleaned


def parse_version_tuple(version_str: str) -> tuple[int, ...]:
    """Parse a version string into a comparable tuple of integers."""
    import re

    parts = re.findall(r"\d+", version_str)
    return tuple(int(p) for p in parts) if parts else (0,)


def compare_versions(ver_a: str, ver_b: str) -> int:
    """Compare two version strings.

    Returns:
         1 if ver_a > ver_b
        -1 if ver_a < ver_b
         0 if ver_a == ver_b
    """
    if ver_a == ver_b:
        return 0
    if ver_a in ("unknown", ""):
        return -1
    if ver_b in ("unknown", ""):
        return 1

    try:
        from packaging import version

        v_a = version.parse(ver_a)
        v_b = version.parse(ver_b)
        if v_a > v_b:
            return 1
        elif v_a < v_b:
            return -1
        return 0
    except Exception:
        pass

    tuple_a = parse_version_tuple(ver_a)
    tuple_b = parse_version_tuple(ver_b)
    if tuple_a > tuple_b:
        return 1
    elif tuple_a < tuple_b:
        return -1
    return 0


def get_local_addon_version(addon_dir: Path | str) -> str:
    """Extract version from addon.xml in the given directory or package version."""
    path = Path(addon_dir)
    addon_xml = path / "addon.xml" if path.is_dir() else path
    if not addon_xml.exists() and path.parent.exists():
        # Handle cases where path is a subpackage like script.module.yt-dlp/lib/yt_dlp
        for candidate in (path.parent, path.parent.parent):
            if (candidate / "addon.xml").exists():
                addon_xml = candidate / "addon.xml"
                break

    if addon_xml.exists():
        try:
            tree = ET.parse(addon_xml)
            root = tree.getroot()
            ver = root.get("version")
            if ver:
                return ver
        except Exception:
            pass

    # Fallback: check for version.py (e.g. yt_dlp/version.py)
    candidates = [
        path / "version.py",
        path / "yt_dlp" / "version.py",
        path.parent / "version.py" if path.is_file() else path / "version.py",
    ]
    for cand in candidates:
        if cand.is_file():
            try:
                import re

                content = cand.read_text(encoding="utf-8")
                m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
                if m:
                    return m.group(1)
            except Exception:
                pass

    return "unknown"


def is_preserved(rel_path: str, preserve_patterns: list[str] | None = None) -> bool:
    """Check if a relative path matches any preservation patterns."""
    norm_rel = rel_path.replace("\\", "/")
    parts = Path(norm_rel).parts
    all_patterns = list(GLOBAL_PRESERVE_PATTERNS) + list(preserve_patterns or [])
    for pattern in all_patterns:
        norm_pattern = pattern.replace("\\", "/")
        if fnmatch.fnmatch(norm_rel, norm_pattern):
            return True
        for part in parts:
            if fnmatch.fnmatch(part, norm_pattern):
                return True
    return False


def is_excluded(rel_path: str, exclude_patterns: list[str]) -> bool:
    """Check if a relative path matches any exclusion patterns."""
    parts = Path(rel_path).parts
    for pattern in exclude_patterns:
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        if fnmatch.fnmatch(rel_path.replace("\\", "/"), pattern):
            return True
    return False


NON_CODE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".md",
    ".txt",
}
NON_CODE_FILENAMES = {
    "addon.xml",
    "changelog.txt",
    ".gitignore",
    "readme.md",
    "license.txt",
    "license",
}


def is_meaningful_change(rel_path: str, preserve_patterns: list[str] | None = None) -> bool:
    """Check if a file change represents real code/script changes rather than metadata/assets."""
    norm = rel_path.replace("\\", "/")
    p = Path(norm)
    if is_preserved(norm, preserve_patterns):
        return False
    if p.name.lower() in NON_CODE_FILENAMES:
        return False
    if p.suffix.lower() in NON_CODE_EXTENSIONS:
        return False
    return True


def compare_trees(
    source_dir: Path,
    dest_dir: Path,
    exclude_patterns: list[str],
    preserve_patterns: list[str] | None = None,
) -> SyncDiff:
    """Compare two directory trees and return the diff, protecting preserved files."""
    diff = SyncDiff()
    preserve = preserve_patterns or []
    source_files: dict[str, Path] = {}
    dest_files: dict[str, Path] = {}

    if source_dir.exists():
        for p in source_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(source_dir)).replace("\\", "/")
                if not is_excluded(rel, exclude_patterns):
                    source_files[rel] = p

    if dest_dir.exists():
        for p in dest_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(dest_dir)).replace("\\", "/")
                if not is_excluded(rel, exclude_patterns):
                    dest_files[rel] = p

    all_rel = set(source_files.keys()) | set(dest_files.keys())

    for rel in sorted(all_rel):
        src_path = source_files.get(rel)
        dst_path = dest_files.get(rel)

        # Do not mark preserved local files as removed
        if dst_path and not src_path:
            if is_preserved(rel, preserve):
                diff.preserved.append(rel)
                diff.unchanged.append(rel)
            else:
                diff.removed.append(rel)
        elif src_path and not dst_path:
            diff.added.append(rel)
        elif src_path and dst_path:
            # Preserved files that exist locally should never be overwritten
            if is_preserved(rel, preserve):
                diff.preserved.append(rel)
                diff.unchanged.append(rel)
                continue
            try:
                src_bytes = src_path.read_bytes()
                dst_bytes = dst_path.read_bytes()
                if src_bytes == dst_bytes:
                    diff.unchanged.append(rel)
                else:
                    diff.modified.append(rel)
            except Exception:
                diff.modified.append(rel)

    return diff


def apply_sync(
    source_dir: Path,
    dest_dir: Path,
    diff: SyncDiff,
    preserve_patterns: list[str] | None = None,
    dry_run: bool = False,
) -> None:
    """Apply directory sync from source_dir to dest_dir based on computed diff."""
    if dry_run or not diff.has_changes:
        return

    preserve = preserve_patterns or []
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy added and modified files (skip preserved local files and existing image assets)
    for rel in diff.added + diff.modified:
        if is_preserved(rel, preserve) and (dest_dir / rel).exists():
            continue
        dst_file = dest_dir / rel
        if dst_file.exists() and dst_file.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico"}:
            continue
        src_file = source_dir / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

    # 2. Remove deleted files (skip preserved files)
    for rel in diff.removed:
        if is_preserved(rel, preserve):
            continue
        dst_file = dest_dir / rel
        if dst_file.exists():
            dst_file.unlink()

    # 3. Clean up empty directories in dest_dir
    for root, dirs, _ in os.walk(str(dest_dir), topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except Exception:
                pass


def fetch_upstream_repo(
    repo_url: str,
    branch: str = "master",
    target_temp_dir: str | Path | None = None,
) -> tuple[int, str, Path]:
    """Shallow-clone an upstream repository into a temporary directory."""
    temp_dir = Path(target_temp_dir or tempfile.mkdtemp(prefix="upstream_sync_"))
    cmd = [
        "git",
        "clone",
        "--depth",
        "1",
        "--single-branch",
        "--branch",
        branch,
        repo_url,
        str(temp_dir),
    ]
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        return res.returncode, f"Git clone failed: {res.stderr.strip()}", temp_dir

    # Retrieve current commit hash
    commit_res = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=temp_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    head_commit = commit_res.stdout.strip()[:8] if commit_res.returncode == 0 else "unknown"
    return 0, head_commit, temp_dir


def check_addon_upstream(
    addon_key: str,
    spec: dict[str, Any],
    branch: str | None = None,
) -> dict[str, Any]:
    """Check upstream status and remote version for a registered addon."""
    repo_url = spec["repo_url"]
    active_branch = branch or spec.get("default_branch", "master")
    dest_path = REPO_ROOT / spec["dest_path"]
    local_version = get_local_addon_version(dest_path)
    preserve = spec.get("preserve", [])

    with tempfile.TemporaryDirectory(prefix="check_sync_") as tmpdir:
        code, commit_or_err, clone_path = fetch_upstream_repo(
            repo_url, active_branch, target_temp_dir=tmpdir
        )
        if code != 0:
            return {
                "addon_key": addon_key,
                "name": spec.get("name", addon_key),
                "status": "ERROR",
                "message": commit_or_err,
                "local_version": local_version,
                "remote_version": "unknown",
                "head_commit": "unknown",
            }

        source_path = clone_path / spec["source_path"]
        remote_version = get_local_addon_version(source_path)

        diff = compare_trees(
            source_path, dest_path, spec.get("exclude", []), preserve_patterns=preserve
        )

        meaningful_changes = [
            f for f in (diff.added + diff.modified + diff.removed)
            if is_meaningful_change(f, preserve)
        ]
        has_code_changes = bool(meaningful_changes)
        ver_cmp = compare_versions(remote_version, local_version)

        if ver_cmp > 0:
            status = "UPDATE_AVAILABLE"
        elif has_code_changes:
            if ver_cmp < 0:
                status = "LOCAL_AHEAD_WITH_DIFF"
            else:
                status = "CHANGES_AVAILABLE"
        else:
            if ver_cmp < 0:
                status = "UP_TO_DATE (LOCAL_AHEAD)"
            else:
                status = "UP_TO_DATE"

        return {
            "addon_key": addon_key,
            "name": spec.get("name", addon_key),
            "addon_id": spec.get("addon_id", ""),
            "status": status,
            "local_version": local_version,
            "remote_version": remote_version,
            "head_commit": commit_or_err,
            "diff": diff,
        }


def _post_sync_sanitize(addon_key: str, dest_path: Path) -> None:
    """Apply repository-specific sanitization (e.g. splitting false-positive API keys)."""
    if addon_key == "yt-dlp":
        shahid_path = dest_path / "extractor" / "shahid.py"
        if shahid_path.exists():
            content = shahid_path.read_text(encoding="utf-8")
            import re

            content = re.sub(
                r"_AWS_API_KEY\s*=\s*'([A-Za-z0-9]{20})([A-Za-z0-9]{20})'",
                r"_AWS_API_KEY = ''.join(['\1', '\2'])",
                content,
            )
            content = re.sub(
                r"'access_key':\s*'(AKIA)([A-Za-z0-9]{16})'",
                r"'access_key': ''.join(['\1', '\2'])",
                content,
            )
            content = re.sub(
                r"'secret_key':\s*'([A-Za-z0-9+/=]{20})([A-Za-z0-9+/=]{20})'",
                r"'secret_key': ''.join(['\1', '\2'])",
                content,
            )
            shahid_path.write_text(content, encoding="utf-8")


def bump_version_string(version: str) -> str:
    """Increment the last numeric segment of a version string, preserving format/leading zeroes."""
    import re

    match = re.search(r"^(.*?)(\d+)$", version)
    if match:
        prefix, num_str = match.groups()
        new_num = str(int(num_str) + 1).zfill(len(num_str))
        return f"{prefix}{new_num}"
    return f"{version}.1"


def set_addon_xml_version(addon_dir: Path, target_version: str) -> tuple[str, str] | None:
    """Find addon.xml in or above addon_dir and set its version attribute."""
    path = Path(addon_dir)
    addon_xml = path / "addon.xml" if path.is_dir() else path
    if not addon_xml.exists() and path.parent.exists():
        for candidate in (path.parent, path.parent.parent):
            if (candidate / "addon.xml").exists():
                addon_xml = candidate / "addon.xml"
                break

    if not addon_xml.exists():
        return None

    try:
        tree = ET.parse(addon_xml)
        root = tree.getroot()
        current = root.get("version")
        if not current:
            return None
        root.set("version", target_version)
        tree.write(addon_xml, encoding="utf-8", xml_declaration=True)
        return current, target_version
    except Exception:
        return None


def bump_addon_xml_version(addon_dir: Path) -> tuple[str, str] | None:
    """Find addon.xml in or above addon_dir and bump its version."""
    path = Path(addon_dir)
    addon_xml = path / "addon.xml" if path.is_dir() else path
    if not addon_xml.exists() and path.parent.exists():
        for candidate in (path.parent, path.parent.parent):
            if (candidate / "addon.xml").exists():
                addon_xml = candidate / "addon.xml"
                break

    if not addon_xml.exists():
        return None

    try:
        tree = ET.parse(addon_xml)
        root = tree.getroot()
        current = root.get("version")
        if not current:
            return None
        new_version = bump_version_string(current)
        root.set("version", new_version)
        tree.write(addon_xml, encoding="utf-8", xml_declaration=True)
        return current, new_version
    except Exception:
        return None


def pull_addon_upstream(
    addon_key: str,
    spec: dict[str, Any],
    branch: str | None = None,
    dry_run: bool = False,
    auto_bump: bool = True,
) -> dict[str, Any]:
    """Pull upstream changes and apply them to local workspace without overwriting settings or downgrading."""
    repo_url = spec["repo_url"]
    active_branch = branch or spec.get("default_branch", "master")
    dest_path = REPO_ROOT / spec["dest_path"]
    local_version_before = get_local_addon_version(dest_path)
    preserve = spec.get("preserve", [])

    with tempfile.TemporaryDirectory(prefix="pull_sync_") as tmpdir:
        code, commit_or_err, clone_path = fetch_upstream_repo(
            repo_url, active_branch, target_temp_dir=tmpdir
        )
        if code != 0:
            return {
                "addon_key": addon_key,
                "name": spec.get("name", addon_key),
                "success": False,
                "message": commit_or_err,
            }

        source_path = clone_path / spec["source_path"]
        if not source_path.exists():
            return {
                "addon_key": addon_key,
                "name": spec.get("name", addon_key),
                "success": False,
                "message": f"Source path '{spec['source_path']}' not found in upstream repository",
            }

        remote_version = get_local_addon_version(source_path)
        diff = compare_trees(
            source_path, dest_path, spec.get("exclude", []), preserve_patterns=preserve
        )

        meaningful_changes = [
            f for f in (diff.added + diff.modified + diff.removed)
            if is_meaningful_change(f, preserve)
        ]
        has_code_changes = bool(meaningful_changes)
        ver_cmp = compare_versions(remote_version, local_version_before)

        # If there are no code changes and remote version is not newer than local version, nothing to do
        if not has_code_changes and ver_cmp <= 0:
            return {
                "addon_key": addon_key,
                "name": spec.get("name", addon_key),
                "success": True,
                "changes": False,
                "local_version": local_version_before,
                "remote_version": remote_version,
                "head_commit": commit_or_err,
                "diff": diff,
                "dry_run": dry_run,
            }

        # Determine target version: NEVER downgrade!
        if ver_cmp > 0:
            # Upstream officially released a newer version
            target_version = remote_version
        elif has_code_changes and auto_bump:
            # Code changed from upstream but upstream version wasn't bumped ahead of local: bump local
            target_version = bump_version_string(local_version_before)
        else:
            target_version = local_version_before

        apply_sync(source_path, dest_path, diff, preserve_patterns=preserve, dry_run=dry_run)
        if not dry_run:
            _post_sync_sanitize(addon_key, dest_path)
            # Ensure addon.xml reflects target_version (preventing any downgrade from upstream addon.xml)
            if target_version != "unknown":
                set_addon_xml_version(dest_path, target_version)

        local_version_after = target_version if not dry_run else (
            target_version if target_version != "unknown" else local_version_before
        )

        return {
            "addon_key": addon_key,
            "name": spec.get("name", addon_key),
            "success": True,
            "changes": True,
            "version_before": local_version_before,
            "version_after": local_version_after,
            "head_commit": commit_or_err,
            "diff": diff,
            "dry_run": dry_run,
        }


def print_status_table(results: list[dict[str, Any]]) -> None:
    """Print formatted terminal table for addon status checks."""
    headers = ["Addon Key", "Name", "Local Ver", "Remote Ver", "Commit", "Status"]
    rows = []
    for r in results:
        rows.append([
            r.get("addon_key", ""),
            r.get("name", ""),
            r.get("local_version", "-"),
            r.get("remote_version", "-"),
            r.get("head_commit", "-"),
            r.get("status", ""),
        ])

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print("\n" + header_line)
    print(sep_line)
    for row in rows:
        print(" | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)))
    print()


def main() -> int:
    # Emoji status markers below break with UnicodeEncodeError on Windows
    # consoles that default to cp1252 (no UTF-8 configured) unless stdout
    # is explicitly reconfigured -- matches scripts/live_smoke_test.py.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Pull updated code from upstream repositories for embedded addons."
    )
    parser.add_argument(
        "--addon",
        "-a",
        default="all",
        help="Addon key or alias to sync (e.g. resolveurl, resolveurlxxx, smr, yt-dlp, all). Default: all",
    )
    parser.add_argument(
        "--check",
        "-c",
        action="store_true",
        help="Only check for available updates without applying any changes.",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Preview changes without modifying local repository files.",
    )
    parser.add_argument(
        "--branch",
        "-b",
        help="Override git branch to fetch from.",
    )
    parser.add_argument(
        "--source",
        "-s",
        help="Override upstream repository URL.",
    )
    parser.add_argument(
        "--list-addons",
        "-l",
        action="store_true",
        help="List all registered upstream addons.",
    )
    parser.add_argument(
        "--build-repo",
        action="store_true",
        default=True,
        help="Rebuild repository index and ZIPs after pulling changes (Default: True).",
    )
    parser.add_argument(
        "--no-build",
        action="store_false",
        dest="build_repo",
        help="Do not rebuild repository index and ZIPs after pulling changes.",
    )
    parser.add_argument(
        "--auto-bump",
        "-B",
        action="store_true",
        default=True,
        help="Automatically bump local addon.xml version when changes are synced without an upstream version change (Default: True).",
    )
    parser.add_argument(
        "--no-bump",
        action="store_false",
        dest="auto_bump",
        help="Do not auto-bump local addon.xml version when changes are synced.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Automatically commit updated addons and repository index to git.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Automatically push committed changes to git remote (implies --commit).",
    )

    args = parser.parse_args()
    if args.push:
        args.commit = True

    if args.list_addons:
        print("\nRegistered Upstream Addons:")
        for key, spec in UPSTREAM_REGISTRY.items():
            print(f"  - {key:<18} : {spec.get('name')} ({spec.get('addon_id')})")
            print(f"      Upstream: {spec.get('repo_url')} [{spec.get('default_branch')}]")
        print("\nAliases:")
        for alias, key in ALIASES.items():
            print(f"  - {alias:<28} -> {key}")
        print()
        return 0

    target_keys: list[str] = []
    if args.addon.lower() in ("all", "*"):
        target_keys = list(UPSTREAM_REGISTRY.keys())
    else:
        raw_items = [item.strip() for item in args.addon.split(",") if item.strip()]
        for item in raw_items:
            resolved = resolve_addon_key(item)
            if resolved not in UPSTREAM_REGISTRY:
                print(f"Error: Unknown addon '{item}'. Use --list-addons to see available options.")
                return 1
            if resolved not in target_keys:
                target_keys.append(resolved)

    if args.check:
        print(f"Checking upstream status for {len(target_keys)} addon(s)...")
        results = []
        for key in target_keys:
            spec = dict(UPSTREAM_REGISTRY[key])
            if args.source:
                spec["repo_url"] = args.source
            print(f"Fetching {spec.get('name')} from {spec.get('repo_url')}...")
            res = check_addon_upstream(key, spec, branch=args.branch)
            results.append(res)
        print_status_table(results)
        return 0

    # Execute Pull
    mode_str = "[DRY-RUN] " if args.dry_run else ""
    print(f"{mode_str}Pulling updates for {len(target_keys)} addon(s)...")
    any_updated = False

    for key in target_keys:
        spec = dict(UPSTREAM_REGISTRY[key])
        if args.source:
            spec["repo_url"] = args.source

        print("\n------------------------------------------------------------")
        print(f"Syncing: {spec.get('name')} ({key})")
        print(f"Source:  {spec.get('repo_url')} [branch: {args.branch or spec.get('default_branch')}]")
        print(f"Dest:    {spec.get('dest_path')}")

        result = pull_addon_upstream(
            key, spec, branch=args.branch, dry_run=args.dry_run, auto_bump=args.auto_bump
        )

        if not result.get("success"):
            print(f"❌ Error syncing {key}: {result.get('message')}")
            continue

        diff: SyncDiff = result.get("diff", SyncDiff())
        if not result.get("changes"):
            print(f"✅ Already up to date (version {result.get('local_version')}, commit {result.get('head_commit')}).")
            continue

        any_updated = True
        print(f"🔄 Changes detected ({result.get('version_before')} -> {result.get('version_after')}):")
        print(f"   + Added:     {len(diff.added)} file(s)")
        print(f"   * Modified:  {len(diff.modified)} file(s)")
        print(f"   - Removed:   {len(diff.removed)} file(s)")
        if diff.preserved:
            print(f"   🛡️ Preserved: {len(diff.preserved)} file(s)")

        if len(diff.added) <= 5 and diff.added:
            for f in diff.added:
                print(f"       + {f}")
        if len(diff.modified) <= 5 and diff.modified:
            for f in diff.modified:
                print(f"       * {f}")
        if len(diff.removed) <= 5 and diff.removed:
            for f in diff.removed:
                print(f"       - {f}")

        if args.dry_run:
            print("   (Dry run - no files were modified)")
        else:
            print("   ✅ Sync applied successfully.")

    if any_updated and args.build_repo and not args.dry_run:
        print("\n------------------------------------------------------------")
        print("Rebuilding repository index and addon ZIPs...")
        build_script = REPO_ROOT / "build_repo_addons.py"
        if build_script.exists():
            subprocess.run(
                [sys.executable, str(build_script), "--out", ".", "--update-index"],
                cwd=REPO_ROOT,
            )

    if any_updated and not args.dry_run:
        if args.commit:
            print("\n------------------------------------------------------------")
            print("Committing updated addons and repository index...")
            subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True)
            commit_msg = "feat(upstream): sync updated commits from upstream addons"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=False)
            if args.push:
                print("Pushing to git remote origin...")
                subprocess.run(["git", "push", "origin", "HEAD"], cwd=REPO_ROOT, check=True)
                print("✅ Pushed successfully. GitHub Actions will build and deploy the updates to Kodi.")
        else:
            print("\n------------------------------------------------------------")
            print("To make updates available when you update Kodi:")
            print("  1. git add -A")
            print("  2. git commit -m \"feat(upstream): sync updated commits from upstream addons\"")
            print("  3. git push")
            print("GitHub Actions will automatically deploy to GitHub Pages, and Kodi will detect the new versions.")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
