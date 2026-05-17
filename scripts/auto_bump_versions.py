import os
import pathlib
import subprocess
import xml.etree.ElementTree as ET

def bump_version(version: str) -> str:
    """Increment the last numeric part of a version string."""
    parts = version.split(".")
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].isdigit():
            parts[i] = str(int(parts[i]) + 1)
            return ".".join(parts)
    return version + ".1"

def get_changed_files(before: str, after: str) -> list[str]:
    """Get the list of changed files between two SHAs."""
    if not before or set(before) == {"0"}:
        return subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", after],
            text=True,
        ).splitlines()
    
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
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", after],
            text=True,
        ).splitlines()

def main():
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
        if (top / "addon.xml").is_file():
            addon_dirs.add(top)

    bumped = []
    for addon_dir in sorted(addon_dirs):
        addon_xml_rel = f"{addon_dir.as_posix()}/addon.xml"
        if addon_xml_rel in changed_set:
            print(f"Skipping {addon_dir}: addon.xml already changed in commit.")
            continue
        
        addon_xml = addon_dir / "addon.xml"
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
