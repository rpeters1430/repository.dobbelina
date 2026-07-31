#!/usr/bin/env python3
"""Split sites into chunks for parallel processing in GitHub Actions."""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITES_DIR = ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
SITE_PROFILES_PATH = ROOT / "config" / "site_profiles.json"


def discover_site_names() -> list[str]:
    names = []
    for file_path in sorted(SITES_DIR.glob("*.py")):
        name = file_path.stem
        if name in {"__init__", "soup_spec"}:
            continue
        names.append(name)
    return names


def load_profiles() -> dict[str, Any]:
    if not SITE_PROFILES_PATH.exists():
        return {}
    return json.loads(SITE_PROFILES_PATH.read_text(encoding="utf-8"))


def build_strict_matrix(profiles: dict[str, Any]) -> dict[str, Any]:
    names = sorted(
        name for name, profile in profiles.get("sites", {}).items()
        if profile.get("tier") == 1
    )
    return {"include": [{"site": name} for name in names]}


def main():
    profiles = load_profiles()
    if "--strict" in sys.argv:
        matrix = build_strict_matrix(profiles)
        print(json.dumps(matrix))
        return

    sites = discover_site_names()
    num_chunks = 4
    chunks = [[] for _ in range(num_chunks)]

    for i, site in enumerate(sites):
        chunks[i % num_chunks].append(site)

    matrix = {"include": []}
    for i, chunk_sites in enumerate(chunks):
        matrix["include"].append({
            "chunk": i + 1,
            "sites": " ".join(chunk_sites)
        })

    print(json.dumps(matrix))


if __name__ == "__main__":
    main()
