---
name: kodi-repo-manager
description: Automation and guidance for building Kodi addons, packaging ZIPs, and updating repository indexes (addons.xml). Use when preparing releases or updating the repository.
---

# Kodi Repository Manager

This skill manages the build and distribution workflow for the Dobbelina repository.

## Build Workflow

The project uses `build_repo_addons.py` to package addons. This script ensures that ZIP files have the correct root folder structure required by Kodi.

### Build All Addons
```bash
python build_repo_addons.py
```

### Build Specific Addon
```bash
python build_repo_addons.py --addons plugin.video.cumination
```

### Update Repository Index
When you release a new version, you must update the global `addons.xml` and its MD5 hash.
```bash
python build_repo_addons.py --update-index
```

## Releasing a New Version

1.  **Bump Version**: Increment the `version` attribute in the addon's `addon.xml`.
2.  **Update Changelog**: Add a new entry to `changelog.txt`.
3.  **Build & Index**: Run the build script with `--update-index`.
4.  **Verify**: Check that `addons.xml` contains the new version and `addons.xml.md5` is updated.

## Troubleshooting Builds

- **Missing Addon**: Ensure the directory contains a valid `addon.xml`.
- **Zip Root Error**: The script automatically handles this, but verify that the ZIP contains a folder named after the addon ID (e.g., `plugin.video.cumination/`).
- **MD5 Mismatch**: If users can't update, re-run with `--update-index` to ensure the MD5 matches the XML content exactly.

## Excluded Files
The build script automatically excludes:
- `.git`, `.github`, `__pycache__`
- `*.zip`, `*.pyc`
- `Thumbs.db`, `.DS_Store`
Do not manually delete these before building; the script handles it.
