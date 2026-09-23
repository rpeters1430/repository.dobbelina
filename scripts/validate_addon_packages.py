#!/usr/bin/env python3
"""Validate the archives that will be uploaded to the Kodi repository."""

import argparse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath


def validate_packages(package_dir: Path, index_path: Path) -> list[str]:
    errors = []
    index = ET.parse(index_path).getroot()
    entries = {addon.get("id"): addon for addon in index.findall("addon")}
    archives = sorted(package_dir.glob("*/*.zip"))
    if not archives:
        return [f"No add-on ZIPs in {package_dir}"]
    packaged = set()
    metadata_by_archive = {}
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as zf:
                names = zf.namelist()
                if zf.testzip() is not None:
                    errors.append(f"{archive}: corrupt archive member")
                if not names or len(names) != len(set(names)):
                    errors.append(f"{archive}: empty or duplicate ZIP entries")
                    continue
                for name in names:
                    parts = PurePosixPath(name).parts
                    if ("\\" in name or name.startswith("/") or ".." in parts
                            or not parts or parts[0] != archive.parent.name):
                        errors.append(f"{archive}: unsafe or misplaced member {name}")
                metadata = ET.fromstring(zf.read(f"{archive.parent.name}/addon.xml"))
        except (OSError, KeyError, ValueError, ET.ParseError, zipfile.BadZipFile) as exc:
            errors.append(f"{archive}: invalid archive or metadata: {exc}")
            continue
        addon_id, version = metadata.get("id"), metadata.get("version")
        metadata_by_archive[archive] = metadata
        packaged.add(addon_id)
        if addon_id != archive.parent.name or archive.name != f"{addon_id}-{version}.zip":
            errors.append(f"{archive}: archive name differs from packaged add-on id/version")
        indexed = entries.get(addon_id)
        if indexed is None or indexed.get("version") != version:
            errors.append(f"{archive}: add-on missing from index or version differs")
        if indexed is not None:
            index_imports = {(item.get("addon"), item.get("version"), item.get("optional"))
                             for item in indexed.findall("./requires/import")}
            archive_imports = {(item.get("addon"), item.get("version"), item.get("optional"))
                               for item in metadata.findall("./requires/import")}
            if index_imports != archive_imports:
                errors.append(f"{archive}: dependencies differ from repository index")
    for archive, addon in metadata_by_archive.items():
        for dependency in addon.findall("./requires/import"):
            required = dependency.get("addon")
            if required in entries and required not in packaged and dependency.get("optional") != "true":
                errors.append(f"{archive}: indexed dependency {required} has no package")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("index", type=Path)
    args = parser.parse_args()
    errors = validate_packages(args.package_dir, args.index)
    for error in errors:
        print(error)
    print(f"Package validation: {'FAILED' if errors else 'OK'}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
