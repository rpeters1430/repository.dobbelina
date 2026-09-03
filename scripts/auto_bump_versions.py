import argparse
import os
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET


def bump_version(version: str) -> str:
    """Increment the last numeric part of a version string, preserving format/leading zeros."""
    match = re.search(r"^(.*?)(\d+)$", version)
    if match:
        prefix, num_str = match.groups()
        new_num = str(int(num_str) + 1).zfill(len(num_str))
        return f"{prefix}{new_num}"
    return f"{version}.1"


def get_changed_files(before: str, after: str) -> list[str]:
    """Get the list of changed files between two SHAs or from uncommitted git changes."""
    if not before or set(before) == {"0"}:
        if after:
            return subprocess.check_output(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", after],
                text=True,
            ).splitlines()
        # Fallback to unstaged / staged git changes
        res = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return [line[3:].strip() for line in res.splitlines() if line.strip()]

    try:
        return subprocess.check_output(
            ["git", "diff", "--name-only", before, after],
            text=True,
            stderr=subprocess.PIPE,
        ).splitlines()
    except subprocess.CalledProcessError:
        # Fallback if before commit is not available (e.g., shallow clone)
        print(f"Warning: Could not diff {before}..{after}, using current commit only")
        return subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", after or "HEAD"],
            text=True,
        ).splitlines()


def main():
    parser = argparse.ArgumentParser(description="Auto-bump Kodi addon versions.")
    parser.add_argument("--addons", nargs="*", help="Specific addon directories to bump.")
    parser.add_argument("--all", action="store_true", help="Bump all addons found in the repo.")
    args = parser.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parents[1]

    if args.all:
        addon_dirs = {p.parent for p in repo_root.glob("*/addon.xml")}
        changed_set = set()
    elif args.addons:
        addon_dirs = {pathlib.Path(a) for a in args.addons}
        changed_set = set()
    else:
        before = os.environ.get("BEFORE_SHA", "").strip()
        after = os.environ.get("AFTER_SHA", "").strip()
        changed = get_changed_files(before, after)
        changed_set = set(changed)

        addon_dirs = set()
        for raw_path in changed:
            path = pathlib.Path(raw_path)
            if not path.parts:
                continue
            top = pathlib.Path(path.parts[0])
            if (repo_root / top / "addon.xml").is_file():
                addon_dirs.add(top)

    bumped = []
    for addon_dir in sorted(addon_dirs):
        addon_dir_path = repo_root / addon_dir if not addon_dir.is_absolute() else addon_dir
        addon_xml_rel = f"{addon_dir.as_posix()}/addon.xml"
        if addon_xml_rel in changed_set:
            print(f"Skipping {addon_dir}: addon.xml already changed in commit.")
            continue

        addon_xml = addon_dir_path / "addon.xml"
        if not addon_xml.is_file():
            continue

        tree = ET.parse(addon_xml)
        root = tree.getroot()
        current = root.get("version")
        if not current:
            continue

        new_version = bump_version(current)
        root.set("version", new_version)

        # Write back with XML declaration and UTF-8 encoding
        tree.write(addon_xml, encoding="utf-8", xml_declaration=True)
        bumped.append((str(addon_dir), current, new_version))

    for addon_dir, current, new_version in bumped:
        print(f"Bumped {addon_dir}: {current} -> {new_version}")

    if not bumped:
        print("No add-on directories changed; no version bump needed.")


if __name__ == "__main__":
    main()
